"""Cross-model checks for conceptual Collab timers backed by QP QTimeEvt.

Conservative static checks: presence is evidence, not proof of runtime paths.
A timer with no matching implementation is an error; uncertain lifecycle is a warning.
RTC/deep-sleep timers require a separate contract and are not misidentified as QTimeEvt.
"""
import re
import xml.etree.ElementTree as ET



def _constant_value(expression, source, seen=None):
    """Resolve a deliberately small subset of integral C++ constant expressions."""
    import ast
    seen = seen or frozenset()
    expression = expression.strip()
    expression = re.sub(r"\\b(0[xX][0-9a-fA-F]+|[0-9]+)[uUlL]+\\b", r"\\1", expression)
    try:
        tree = ast.parse(expression, mode="eval").body
    except SyntaxError:
        return None

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.Name):
            name = node.id
            if name in seen:
                return None
            patterns = (
                r"(?m)^\\s*#\\s*define\\s+" + re.escape(name) + r"\\s+([^\\n]+)",
                r"\\b(?:constexpr|const)\\s+(?:[\\w:]+\\s+)+" + re.escape(name) + r"\\s*=\\s*([^;]+);",
            )
            for pattern in patterns:
                match = re.search(pattern, source)
                if match:
                    return _constant_value(match.group(1).split("//")[0], source, seen | {name})
            return None
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = evaluate(node.operand)
            return None if value is None else (value if isinstance(node.op, ast.UAdd) else -value)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
            left, right = evaluate(node.left), evaluate(node.right)
            if left is None or right is None:
                return None
            return (left + right if isinstance(node.op, ast.Add) else
                    left - right if isinstance(node.op, ast.Sub) else left * right)
        return None

    return evaluate(tree)


def _arm_intervals(code, member):
    """Return interval expressions; omitted second argument means one-shot."""
    pattern = r"\\b" + re.escape(member) + r"\\s*\\.\\s*armX\\s*\\("
    intervals = []
    for match in re.finditer(pattern, code):
        start = match.end()
        depth = 0
        args = []
        last = start
        for index in range(start, len(code)):
            char = code[index]
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    args.append(code[last:index].strip())
                    break
                depth -= 1
            elif char == "," and depth == 0:
                args.append(code[last:index].strip())
                last = index + 1
        if args:
            intervals.append(args[1] if len(args) > 1 else "0U")
    return intervals


def check_timers(timers, routes, qm_path, report):
    root = ET.parse(qm_path).getroot()
    classes = {node.get("name"): node for node in root.findall(".//class")}
    all_text = "\n".join(node.text or "" for node in root.iter())
    tick_service = bool(re.search(r"QF::TICK_X\s*\(|QF::tickX_\s*\(", all_text))

    for timer, cadence in timers.items():
        outgoing = [(receiver, sig) for sender, receiver, sig, _ in routes if sender == timer]
        if not outgoing:
            report("ERROR", f"timer {timer}: no outgoing signal route in Collab")
            continue
        if len(outgoing) != 1:
            report("WARNING", f"timer {timer}: {len(outgoing)} routes; check whether one timer instance can satisfy them")
        for receiver, signal in outgoing:
            prefix = f"timer {timer} -> {receiver} : {signal}"
            owner = classes.get(receiver)
            if owner is None:
                report("ERROR", f"{prefix}: receiving QM class missing")
                continue
            members = [(a.get("name"), a.get("type", "")) for a in owner.findall("./attribute")
                       if "QTimeEvt" in a.get("type", "")]
            if not members:
                report("ERROR", f"{prefix}: no QP::QTimeEvt member in QM class")
            triggers = {t.get("trig") for t in owner.findall(".//tran")}
            if signal not in triggers:
                report("ERROR", f"{prefix}: QM HSM has no transition triggered by {signal}")
            if not members:
                continue
            # Prefer a constructor binding to the declared signal over a guessed
            # correspondence between conceptual and C++ timer names.
            constructors = [op.findtext("code") or "" for op in owner.findall("./operation")
                            if op.get("name") == receiver]
            bound = []
            for member, _ in members:
                pattern = r"\b" + re.escape(member) + r"\s*\(\s*this\s*,\s*" + re.escape(signal + "_SIG") + r"\s*,"
                if any(re.search(pattern, code) for code in constructors):
                    bound.append(member)
            if not bound:
                report("ERROR", f"{prefix}: no QTimeEvt constructor binding (this, {signal}_SIG, tickRate) in QM")
                continue
            if len(bound) > 1:
                report("WARNING", f"{prefix}: multiple QTimeEvt members bind the same signal: {', '.join(bound)}")
            member = bound[0]
            code = "\n".join(node.text or "" for node in owner.iter() if node.tag in ("code", "entry", "exit", "action"))
            # Code inside QM actions/entries is captured by iterating text nodes.
            if not re.search(r"\b" + re.escape(member) + r"\s*\.\s*armX\s*\(", code):
                report("ERROR", f"{prefix}: {member}.armX(...) not found in QM embedded code/actions")
            triggers = {t.get("trig") for t in owner.findall(".//tran")}
            if not tick_service:
                report("WARNING", f"{prefix}: no QF tick service found in QM templates; verify external tick integration")
            if not re.search(r"\b" + re.escape(member) + r"\s*\.\s*(?:disarm|rearm)\s*\(", code):
                report("WARNING", f"{prefix}: no explicit disarm/rearm found; review lifecycle (not required for periodic rearming)")
            report("INFO", f"{prefix}: static checks cannot prove scheduling paths or runtime delivery")
