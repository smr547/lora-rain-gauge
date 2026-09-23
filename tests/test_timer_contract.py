"""Regression tests for timer contract diagnostics."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_architecture import parse_collab
from timer_contract import check_timers


class TimerContractTests(unittest.TestCase):
    def test_declared_unimplemented_timer_is_error(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            collab = base / "test.collab"
            collab.write_text('''collab 1
ao Control
timer SleepTimer "One-shot; inactivity interval"
collaboration SleepTimer Control
  SleepTimer -> Control
    CONSIDER_SLEEPING
end
''')
            qm = base / "model.qm"
            qm.write_text('''<model><class name="Control" superclass="qpcpp::QActive">
<statechart><state name="Running"/></statechart></class></model>''')
            _, routes, timers = parse_collab(collab)
            diagnostics = []
            check_timers(timers, routes, qm, lambda level, message: diagnostics.append((level, message)))
            self.assertTrue(any(level == "ERROR" and "no QP::QTimeEvt member" in message
                                for level, message in diagnostics), diagnostics)

    def test_complete_static_pattern_has_no_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            qm = Path(directory) / "model.qm"
            qm.write_text('''<model><class name="Control" superclass="qpcpp::QActive">
<attribute name="m_sleepTimer" type="QP::QTimeEvt"/>
<operation name="Control"><code>: QActive(Q_STATE_CAST(&amp;Control::initial)),
m_sleepTimer(this, CONSIDER_SLEEPING_SIG, 0U)</code></operation>
<statechart><state name="Running"><entry>m_sleepTimer.armX(100U);</entry>
<tran trig="CONSIDER_SLEEPING"><action>m_sleepTimer.disarm();</action></tran>
</state></statechart></class>
<directory><file name="main.cpp"><text>QP::QF::TICK_X(0U, nullptr);</text></file></directory></model>''')
            diagnostics = []
            check_timers({"SleepTimer": "One-shot"}, [("SleepTimer", "Control", "CONSIDER_SLEEPING", 1)],
                         qm, lambda level, message: diagnostics.append((level, message)))
            self.assertFalse(any(level == "ERROR" for level, _ in diagnostics), diagnostics)


if __name__ == "__main__":
    unittest.main()
