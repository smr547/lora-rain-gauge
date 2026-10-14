# Proposed protocol extension: tipping-bucket diagnostics

Status: **proposal only** (2026-10-14). Not implemented, not a wire-format specification. To be reviewed when QP/HSM development resumes.

## Motivation
A filtering HSM may reject candidate switch transitions. These rejections are useful diagnostic evidence: they may indicate contact bounce, RF/electrical interference, or genuine tips incorrectly rejected by filtering configuration or software. Do not label all rejections as proven noise.

## Proposed cumulative fields
- `candidateTipCount`: number of input events actually observed and submitted for classification.
- `acceptedTipCount`: number classified as valid bucket tips; existing cumulative `bucketCount` may serve this purpose if semantics are identical.
- `rejectedTipCount`: number classified as invalid by the HSM.

All counters are monotonically increasing within a documented counter epoch, subject to reset/wrap policy. For fully classified candidates, the invariant is `candidateTipCount = acceptedTipCount + rejectedTipCount`. Define what constitutes one candidate, how bounce is grouped, and when classification completes before relying on this invariant.

## Protocol and persistence considerations
- Send **cumulative** counters so packet loss does not erase intermediate totals.
- Associate diagnostics with node ID, sequence number, firmware source/version and counter epoch or reset information.
- Specify persistence across deep sleep, power failure, and reboot; do not assume NVS writes on every transition are acceptable.
- Consider optional rejection-reason counters only after HSM states and timing criteria are designed.
- A missed hardware pulse that never wakes or reaches the ESP32 is **not** counted as a candidate or rejection; independent stimulus testing is required.
- Distinguish true counter changes from repeated/out-of-order LoRa packets.
- Keep radio payload compact and version the extension explicitly; do not silently change existing protocol v3 fields.

## Verification
Use the [repeatable soak-test strategy](../tests/rain-gauge-soak-test-strategy.md) to inject known valid tips and deliberate noise/bounce. Compare stimulus logs, local counters and base-station observations. Test false rejection, false acceptance, close pulses, sleep/wake, and transmission overlap.

Implementation deferred.
