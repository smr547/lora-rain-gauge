# Rain gauge hardware-in-the-loop soak-test strategy

Status: **planned, not yet implemented** (2026-10-14).

## Objective
Establish an independent, repeatable baseline for the existing [LoRa experimental firmware](https://github.com/smr547/lora_experiments) (branch `e1-rain-gauge-v3`), then reuse the same tests for the QP/HSM firmware and Rev A custom hardware. Determine whether tips are missed, duplicated, or rejected, and under what circumstances.

## Architecture
1. **Independent ESP32 stimulus generator:** spare ESP32 generates deterministic and seeded-pseudorandom tipping-bucket switch closures with precise timestamps and an authoritative count of *intended valid tips*. Drive the gauge input through a suitable isolated open-collector/opto-isolated or dry-contact-equivalent circuit, not a direct unverified GPIO connection.
2. **Device under test:** current LilyGO node, later QP/HSM node and custom PCB. Exercise the actual input electronics and deep-sleep wake path; do not substitute an internal software tip generator.
3. **Observation:** local debug logs when available and LoRa base station -> Signal K -> InfluxDB. Capture raw packets, sequence numbers, cumulative bucket count, battery/uptime/reset information, and (when implemented) candidate/rejected counters.
4. **Independent evidence:** persist the stimulus schedule and actual delivered pulses; use controller input feedback or oscilloscope/logic-analyser traces to confirm signal delivery, especially at short intervals.

## Test cases
- Slow regular clean pulses; seeded random intervals representative of rainfall.
- Closely spaced valid pulses and boundary sweeps near minimum supported interval.
- Deliberate contact-bounce waveforms, spurious short pulses and simulated electrical interference.
- Pulses during deep sleep, wake-up, NVS activity and LoRa transmission.
- Extended continuous operation (days/weeks), counter overflow considerations, brownout/reboot and power interruption.
- Temporary radio/base-station outage and recovery, checking whether cumulative counts reconstruct correctly.

## Data and analysis
- Record hardware identity/revision, firmware Git SHA (not only branch), configuration, battery/power source, test start/end times, controller firmware SHA, random seed, pulse widths/intervals, stimulus event IDs and logs.
- For clean tips, compute `countError = reportedAcceptedCount - generatedValidTipCount` after allowing final transmission and recovery. Desired result: zero.
- For noisy stimuli, compare accepted counts against **intended valid operations**, not raw edges. Track false positives and false negatives separately.
- Compare local DUT counts with remote packet-derived counts to distinguish missed input from delayed/lost radio delivery.
- Preserve timestamped stimulus data so any failure can be replayed. Use independently observed signal timing where practical.
- Note that cumulative totals alone do not reveal which individual tip was lost; correlate timestamps and controlled segments to narrow failures.
- Document resets, communication gaps, and ambiguities rather than treating missing data as zero rainfall.

## Acceptance and sequencing
Begin with short deterministic tests and confirm instrumentation, then progressively run longer randomized soak tests. Define quantitative pass/fail limits and maximum realistic tip rate before formal qualification. Avoid changing experimental firmware until baseline telemetry proves insufficient.

This test strategy is intended to be reused unchanged across firmware architectures; implementation deferred.
