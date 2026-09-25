"""End-to-end cadence regression tests through validate_architecture.py.

Use real project models and generated signal header, changing only a temporary
Collab copy. This catches checks that exist but are not wired into main().
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "rain-gauge-node" / "model"
VALIDATOR = ROOT / "tools" / "validate_architecture.py"


class TimerContractIntegrationTests(unittest.TestCase):
    def run_validator(self, replacements=()):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            collab = work / "rain-gauge.collab"
            source = (MODEL / "rain-gauge.collab").read_text(encoding="utf-8")
            for old, new in replacements:
                self.assertIn(old, source, f"fixture no longer contains {old!r}")
                source = source.replace(old, new, 1)
            collab.write_text(source, encoding="utf-8")
            # The validator resolves the generated header beside the Collab file.
            (work / "rain-gauge-signals.hpp").write_bytes(
                (MODEL / "rain-gauge-signals.hpp").read_bytes()
            )
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(collab), str(MODEL / "model.qm")],
                capture_output=True, text=True, check=False,
            )

    def test_real_two_timer_model_passes(self):
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("0 error(s), 0 warning(s)", result.stdout)
        self.assertIn("timer SleepTimer -> Control : CONSIDER_SLEEPING", result.stdout)
        self.assertIn("timer RadioTxTimer -> Radio : RADIO_TX_TIMEOUT", result.stdout)

    def test_one_shot_radio_rejects_periodic_contract(self):
        result = self.run_validator((
            ('timer RadioTxTimer "One-shot; transmission timeout"',
             'timer RadioTxTimer "Periodic; transmission timeout"'),
        ))
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "timer RadioTxTimer -> Radio : RADIO_TX_TIMEOUT: "
            "Collab declares Periodic, but armX interval resolves to zero",
            result.stdout,
        )
        self.assertIn("1 error(s)", result.stdout)

    def test_periodic_sleep_rejects_one_shot_contract(self):
        result = self.run_validator((
            ('timer SleepTimer "Periodic; inactivity interval"',
             'timer SleepTimer "One-shot; inactivity interval"'),
        ))
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "timer SleepTimer -> Control : CONSIDER_SLEEPING: "
            "Collab declares One-shot, but armX interval resolves to",
            result.stdout,
        )
        self.assertIn("1 error(s)", result.stdout)


if __name__ == "__main__":
    unittest.main()
