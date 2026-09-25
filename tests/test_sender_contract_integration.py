"""Fault injection for the implemented Control -> Radio rainfall sender contract."""
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "rain-gauge-node" / "model"
VALIDATOR = ROOT / "tools" / "validate_architecture.py"
DIAGNOSTIC = "Control has no QM event construction and POST for SEND_RAIN_REPORT to Radio"


class RainSenderContractTests(unittest.TestCase):
    def run_mutation(self, change=None):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            tree = ET.parse(MODEL / "model.qm")
            control = next(node for node in tree.findall(".//class")
                           if node.get("name") == "Control")
            actions = [node for node in control.findall(".//action")
                       if "Q_NEW(SendReportEvt, SEND_RAIN_REPORT_SIG)" in (node.text or "")]
            self.assertEqual(1, len(actions), "expected one rainfall report action")
            if change:
                change(actions[0])
            qm = work / "model.qm"
            tree.write(qm, encoding="unicode", xml_declaration=True)
            collab = work / "rain-gauge.collab"
            collab.write_bytes((MODEL / "rain-gauge.collab").read_bytes())
            (work / "rain-gauge-signals.hpp").write_bytes(
                (MODEL / "rain-gauge-signals.hpp").read_bytes())
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(collab), str(qm)],
                capture_output=True, text=True, check=False)

    def assert_sender_error(self, result):
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR: collab:", result.stdout)
        self.assertIn(DIAGNOSTIC, result.stdout)

    def test_real_rain_sender_passes(self):
        result = self.run_mutation()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("0 error(s), 0 warning(s)", result.stdout)

    def test_missing_post_is_error(self):
        self.assert_sender_error(self.run_mutation(
            lambda action: setattr(action, "text", (action.text or "").replace(
                "AO_Radio->POST(report, this);", ""))))

    def test_wrong_destination_is_error(self):
        self.assert_sender_error(self.run_mutation(
            lambda action: setattr(action, "text", (action.text or "").replace(
                "AO_Radio->POST(report, this);", "AO_Control->POST(report, this);"))))

    def test_missing_construction_is_error(self):
        self.assert_sender_error(self.run_mutation(
            lambda action: setattr(action, "text", (action.text or "").replace(
                "Q_NEW(SendReportEvt, SEND_RAIN_REPORT_SIG)",
                "Q_NEW(SendReportEvt, SEND_HEALTH_REPORT_SIG)"))))

    def test_commented_out_post_is_error(self):
        self.assert_sender_error(self.run_mutation(
            lambda action: setattr(action, "text", (action.text or "").replace(
                "AO_Radio->POST(report, this);", "// AO_Radio->POST(report, this);"))))


if __name__ == "__main__":
    unittest.main()
