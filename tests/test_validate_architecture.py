"""Regression tests for the read-only architecture validator.

Run from repository root: python3 -m unittest discover -s tests -v
No QM, Collab, PlantUML, or firmware toolchain required.
"""
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validate_architecture", ROOT / "tools" / "validate_architecture.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

COLLAB = """collab 1
isr BucketReedSwitch
ao TippingBucket
ao Control
ao Radio
collaboration BucketReedSwitch TippingBucket
BUCKET_SWITCH_CLOSING
end
collaboration TippingBucket Control
BUCKET_TIPPED
end
collaboration Control TippingBucket
BUCKET_SWITCH_CLOSING
end
"""
HEADER = """enum AppSignals {
BUCKET_SWITCH_CLOSING_SIG = QP::Q_USER_SIG,
BUCKET_TIPPED_SIG,
MAX_APP_SIG
};
"""
QM = """<?xml version="1.0"?>
<model><class name="TippingBucket"><state><tran trig="BUCKET_SWITCH_CLOSING"/></state></class>
<class name="Control"><state><tran trig="BUCKET_TIPPED"/></state></class></model>
"""


class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.collab = self.directory / "rain-gauge.collab"
        self.qm = self.directory / "model.qm"
        self.header = self.directory / "rain-gauge-signals.hpp"
        self.collab.write_text(COLLAB, encoding="utf-8")
        self.qm.write_text(QM, encoding="utf-8")
        self.header.write_text(HEADER, encoding="utf-8")

    def run_validator(self):
        output = io.StringIO()
        with patch("sys.argv", ["validate_architecture.py", str(self.collab), str(self.qm)]):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                code = validator.main()
        return code, output.getvalue()

    def test_isr_requires_no_qm_class(self):
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)
        self.assertNotIn("BucketReedSwitch: QM class", output)

    def test_duplicate_participant_across_roles_is_error(self):
        self.collab.write_text(COLLAB.replace("ao TippingBucket", "ao TippingBucket\nisr TippingBucket"), encoding="utf-8")
        code, output = self.run_validator()
        self.assertEqual(code, 2, output)
        self.assertIn("duplicate participant", output)

    def test_generated_signal_declarations_are_recognised(self):
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)
        self.assertNotIn("missing from Collab-generated header", output)

    def test_repeated_signal_counts_as_one_unique_signal(self):
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)
        self.assertIn("3 directed routes, 2 unique signals", output)

    def test_transition_must_belong_to_receiving_class(self):
        # The signal exists in QM, but only in the wrong AO.
        self.qm.write_text(QM.replace(
            '<tran trig="BUCKET_TIPPED"/>', '<tran trig="UNRELATED"/>'
        ).replace(
            '<tran trig="BUCKET_SWITCH_CLOSING"/>',
            '<tran trig="BUCKET_SWITCH_CLOSING"/><tran trig="BUCKET_TIPPED"/>'
        ), encoding="utf-8")
        code, output = self.run_validator()
        self.assertEqual(code, 1, output)
        self.assertIn("ERROR: collab:", output)
        self.assertIn("Control has no QM transition for BUCKET_TIPPED", output)

    def test_misspelled_health_report_transition_is_error(self):
        self.collab.write_text(COLLAB + """collaboration Control Radio
Control -> Radio
SEND_HEALTH_REPORT
end
""", encoding="utf-8")
        self.header.write_text(HEADER.replace("MAX_APP_SIG", "SEND_HEALTH_REPORT_SIG,\\nMAX_APP_SIG"), encoding="utf-8")
        self.qm.write_text(QM.replace(
            '</model>', '<class name="Radio"><state><tran trig="SEND_HEALT_REPORT"/></state></class></model>'
        ), encoding="utf-8")
        code, output = self.run_validator()
        self.assertEqual(1, code, output)
        self.assertIn("ERROR: collab:", output)
        self.assertIn("Radio has no QM transition for SEND_HEALTH_REPORT", output)

    def test_health_report_transition_in_wrong_ao_is_error(self):
        self.collab.write_text(COLLAB + """collaboration Control Radio
Control -> Radio
SEND_HEALTH_REPORT
end
""", encoding="utf-8")
        self.header.write_text(HEADER.replace("MAX_APP_SIG", "SEND_HEALTH_REPORT_SIG,\\nMAX_APP_SIG"), encoding="utf-8")
        self.qm.write_text(QM.replace(
            '<tran trig="BUCKET_TIPPED"/>',
            '<tran trig="BUCKET_TIPPED"/><tran trig="SEND_HEALTH_REPORT"/>'
        ).replace(
            '</model>', '<class name="Radio"><state/></class></model>'
        ), encoding="utf-8")
        code, output = self.run_validator()
        self.assertEqual(1, code, output)
        self.assertIn("Radio has no QM transition for SEND_HEALTH_REPORT", output)

    def test_missing_qm_implementation_is_warning_not_error(self):
        self.qm.write_text('<model/>', encoding="utf-8")
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)
        self.assertIn("QM class Radio not yet implemented", output)
        self.assertIn("0 error(s)", output)

    def test_missing_generated_signal_is_error(self):
        self.header.write_text(HEADER.replace("BUCKET_TIPPED_SIG,", ""), encoding="utf-8")
        code, output = self.run_validator()
        self.assertEqual(code, 1, output)
        self.assertIn("ERROR:", output)
        self.assertIn("BUCKET_TIPPED_SIG missing", output)

    def test_malformed_qm_is_error(self):
        self.qm.write_text("<model>", encoding="utf-8")
        code, output = self.run_validator()
        self.assertEqual(code, 2, output)
        self.assertIn("ERROR:", output)

    def test_validation_does_not_modify_inputs(self):
        before = {p: p.read_bytes() for p in (self.collab, self.qm, self.header)}
        self.run_validator()
        self.assertEqual(before, {p: p.read_bytes() for p in before})


if __name__ == "__main__":
    unittest.main()
