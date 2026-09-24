"""Cross-model checks for conceptual Collab timers backed by QP QTimeEvt.

Conservative static checks: presence is evidence, not proof of runtime paths.
A timer with no matching implementation is an error; uncertain lifecycle is a warning.
RTC/deep-sleep timers require a separate contract and are not misidentified as QTimeEvt.
"""
import re
import xml.etree.ElementTree as ET


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
                report("WARNING", f"{prefix}: no explicit disarm/rearm found; review lifecycle (may be valid for one-shot)")
            report("INFO", f"{prefix}: static checks cannot prove scheduling paths or runtime delivery")
