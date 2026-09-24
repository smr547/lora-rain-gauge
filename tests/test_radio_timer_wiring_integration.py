"""Regression tests for RadioTxTimer wiring through the full validator.

Mutate temporary copies of the real QM model, not generated C++ or the
developer's working tree. Each test asserts a failing process exit.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "rain-gauge-node" / "model"
VALIDATOR = ROOT / "tools" / "validate_architecture.py"
PREFIX = "ERROR: timer RadioTxTimer -> Radio : RADIO_TX_TIMEOUT: "


class RadioTimerWiringTests(unittest.TestCase):
    def run_with_qm_change(self, old, new):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            qm = work / "model.qm"
            original = (MODEL / "model.qm").read_text(encoding="utf-8")
            self.assertEqual(1, original.count(old),
                             f"QM fixture expected exactly one occurrence of {old!r}")
            qm.write_text(original.replace(old, new, 1), encoding="utf-8")
            collab = work / "rain-gauge.collab"
            collab.write_bytes((MODEL / "rain-gauge.collab").read_bytes())
            (work / "rain-gauge-signals.hpp").write_bytes(
                (MODEL / "rain-gauge-signals.hpp").read_bytes()
            )
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(collab), str(qm)],
                capture_output=True, text=True, check=False,
            )

    def assert_timer_error(self, result, diagnostic):
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(PREFIX + diagnostic, result.stdout)
        self.assertIn("1 error(s)", result.stdout)

    def test_missing_arm_is_error(self):
        result = self.run_with_qm_change(
            "<entry>m_txTimer.armX(TX_TIMEOUT_TICKS);</entry>",
            "<entry></entry>",
        )
        self.assert_timer_error(
            result, "m_txTimer.armX(...) not found in QM embedded code/actions"
        )

    def test_arm_in_qm_comment_does_not_count(self):
        result = self.run_with_qm_change(
            "<entry>m_txTimer.armX(TX_TIMEOUT_TICKS);</entry>",
            "<entry></entry><documentation>m_txTimer.armX(TX_TIMEOUT_TICKS);</documentation>",
        )
        self.assert_timer_error(
            result, "m_txTimer.armX(...) not found in QM embedded code/actions"
        )

    def test_missing_receiving_transition_is_error(self):
        result = self.run_with_qm_change(
            '<tran trig="RADIO_TX_TIMEOUT" target="../../../2">',
            '<tran trig="CONTINUE" target="../../../2">',
        )
        self.assert_timer_error(
            result, "QM HSM has no transition triggered by RADIO_TX_TIMEOUT"
        )
        self.assertIn("WARNING: collab:", result.stdout)

    def test_wrong_constructor_signal_is_error(self):
        result = self.run_with_qm_change(
            "m_txTimer(this, RADIO_TX_TIMEOUT_SIG, 0U)",
            "m_txTimer(this, CONTINUE_SIG, 0U)",
        )
        self.assert_timer_error(
            result,
            "no QTimeEvt constructor binding (this, RADIO_TX_TIMEOUT_SIG, tickRate) in QM",
        )

    def test_wrong_constructor_recipient_is_error(self):
        result = self.run_with_qm_change(
            "m_txTimer(this, RADIO_TX_TIMEOUT_SIG, 0U)",
            "m_txTimer(AO_Control, RADIO_TX_TIMEOUT_SIG, 0U)",
        )
        self.assert_timer_error(
            result,
            "no QTimeEvt constructor binding (this, RADIO_TX_TIMEOUT_SIG, tickRate) in QM",
        )


if __name__ == "__main__":
    unittest.main()
