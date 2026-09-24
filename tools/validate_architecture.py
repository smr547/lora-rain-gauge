#!/usr/bin/env python3
"""Read-only, deliberately conservative Collab/QM architecture checker (v0.2).

The collaboration source is the design intent. QM is a work in progress.
Missing implementations are warnings; malformed sources and demonstrable
contradictions are errors. This tool does not inspect generated C++.
"""
import argparse
import re
import shlex
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timer_contract import check_timers

PARTICIPANT = re.compile(r"^(ao|isr)\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
START = re.compile(r"^collaboration\s+(\w+)\s+(\w+)\s*$")
ROUTE = re.compile(r"^(\w+)\s*->\s*(\w+)\s*$")
SIGNAL = re.compile(r"^[A-Z][A-Z0-9_]*$")


def parse_collab(path):
    participants, routes, block, sender, receiver = {}, [], False, None, None
    timers = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if not block and line.startswith("timer "):
            try:
                fields = shlex.split(line)
            except ValueError as exc:
                raise ValueError(f"{path}:{number}: invalid timer declaration: {exc}") from exc
            if len(fields) not in (2, 3) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", fields[1]):
                raise ValueError(f"{path}:{number}: expected timer Name [quoted cadence]")
            name = fields[1]
            if name in participants:
                raise ValueError(f"{path}:{number}: duplicate participant {name}")
            participants[name] = "timer"
            timers[name] = fields[2] if len(fields) == 3 else ""
            continue
        match = PARTICIPANT.fullmatch(line)
        if match and not block:
            role, name = match.groups()
            if name in participants:
                raise ValueError(f"{path}:{number}: duplicate participant {name}")
            participants[name] = role
            continue
        match = START.fullmatch(line)
        if match and not block:
            sender, receiver = match.groups()
            block = True
            continue
        if line == "end" and block:
            block = False
            sender = receiver = None
            continue
        if block:
            match = ROUTE.fullmatch(line)
            if match:
                sender, receiver = match.groups()
            elif SIGNAL.fullmatch(line):
                routes.append((sender, receiver, line, number))
            else:
                raise ValueError(f"{path}:{number}: unrecognised collaboration line: {line}")
        elif not (line == "collab 1" or line.startswith("title ")):
            raise ValueError(f"{path}:{number}: unrecognised top-level line: {line}")
    if block:
        raise ValueError(f"{path}: unterminated collaboration")
    return participants, routes, timers


def qm_facts(path):
    root = ET.parse(path).getroot()
    classes = {node.get("name"): node for node in root.findall(".//class")}
    triggers = {}
    for name, node in classes.items():
        triggers[name] = {tran.get("trig", "") for tran in node.findall(".//tran")}
    # The QM model embeds C++ templates; the signal enum may be in a <text>.
    source = "\n".join(node.text or "" for node in root.iter())
    symbols = set(re.findall(r"\b[A-Z][A-Z0-9_]*_SIG\b", source))
    return classes, triggers, symbols


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collab", type=Path)
    parser.add_argument("qm", type=Path)
    parser.add_argument("--signals", type=Path, default=None,
                        help="Collab-generated signal header (default: beside .collab)")
    args = parser.parse_args()
    try:
        participants, routes, timers = parse_collab(args.collab)
        classes, triggers, qm_symbols = qm_facts(args.qm)
        signal_path = args.signals or args.collab.with_name(args.collab.stem + "-signals.hpp")
        signal_text = signal_path.read_text(encoding="utf-8")
        declared_signals = set(re.findall(r"\b[A-Z][A-Z0-9_]*_SIG\b", signal_text))
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = warnings = 0
    def report(level, message):
        nonlocal errors, warnings
        print(f"{level}: {message}")
        errors += level == "ERROR"
        warnings += level == "WARNING"

    for sender, receiver, signal, line in routes:
        if sender not in participants or receiver not in participants:
            report("ERROR", f"collab:{line}: undeclared endpoint in {sender} -> {receiver}")
        if signal + "_SIG" not in declared_signals:
            report("ERROR", f"collab:{line}: {signal}_SIG missing from Collab-generated header")
        if participants.get(receiver) == "ao" and receiver in classes and signal not in triggers.get(receiver, set()):
            report("WARNING", f"collab:{line}: {receiver} has no QM transition for {signal}")
    for participant, role in sorted(participants.items()):
        if role == "ao" and participant not in classes:
            report("WARNING", f"{participant}: QM class {participant} not yet implemented")

    check_timers(timers, routes, args.qm, report)

    print(f"Architecture check: {len(participants)} participants, {len(routes)} directed routes, "
          f"{len(set(signal for _, _, signal, _ in routes))} unique signals; "
          f"{errors} error(s), {warnings} warning(s).")
    print("UNVERIFIED: QM/header integration, C++ event posts, ISR wiring, payloads and end-to-end routing "
          "are outside v0.2 scope.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
