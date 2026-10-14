# Rain gauge node Rev A — requirements
Date: 2026-10-14. Initial design baseline; values not yet verified are marked as targets.

## User Requirements

These statements express the needs of Jim and Liz, currently represented by their proxy. They are provisional until Jim and Liz review and approve them. They describe the overall rainfall monitoring system, not just the remote node.

- **UR-01 Unattended reliability:** The rain gauge shall operate reliably without attendance for weeks and preferably months at a time.
- **UR-02 Minimal maintenance:** Routine maintenance shall be minimal, ordinarily limited to occasional cleaning of the collecting funnel.
- **UR-03 Safe accessibility:** The gauge shall be mountable on a post so the user can reach it while standing on the ground, without a ladder.
- **UR-04 Battery service:** Battery replacement shall be infrequent and achievable with a screwdriver and readily available replacement batteries, without specialist tools.
- **UR-05 Battery warning:** The system shall warn the user in sufficient time when battery replacement or attention is required.
- **UR-06 Faithful rainfall record:** The system shall reliably capture rainfall occurrences, their duration and the total rainfall associated with each event.
- **UR-07 Rainfall intensity:** Rainfall rates in mm/min shall be available.
- **UR-08 Configurable accumulation:** The user shall be able to configure and view rainfall accumulation over useful periods.
- **UR-09 Internet access:** Rainfall data and other weather status and historical information shall be accessible via the internet.
- **UR-10 Farm integration:** One or more rain gauges shall integrate readily with a farm-wide system using a central radio base station and data collection computer.
- **UR-11 Identification and provenance:** Each rain gauge shall have a unique identifier clearly visible on the physical gauge, and that identifier shall be associated with its resulting data stream.

### Clarifications for later review

- Define a rainfall event and the dry interval that terminates one; distinguish event duration from periods when rain is actively falling.
- Establish acceptable measurement accuracy, tip loss, communication outage recovery and explicit missing-data indication.
- Agree warning thresholds and how alerts reach users, including loss of contact with a gauge.
- Confirm battery format/availability, acceptable service interval and safe replacement procedure.
- Agree configurable accumulation windows, reporting latency, access permissions and expected historical retention.
- Define the boundary between node responsibilities and base-station/computer processing (event detection, rates, accumulation, alerting).
- Confirm whether solar charging is the normal operating mode and battery replacement is a rare maintenance exception.

## Functional
- ESP32 module, SX1276 LoRa module operating at 915 MHz.
- Wake ESP32 on tipping-bucket switch activity, debounce and count in firmware. No external counter.
- Preserve accumulated count through deep sleep and define behavior through resets and power loss.
- On-board battery voltage measurement using an ADC, with low-leakage or switched divider.
- Preserve compatibility with the existing LilyGO T3 v1.6.1 implementation where practical.
- Provide accessible programming, boot and reset connections.

## Power
- Single-cell 3.7 V nominal Li-ion/LiPo battery inside the enclosure.
- Two alternative assembly variants: integrated BQ25185 solar charger plus 3.3 V buck regulator, or external regulated 3.3 V supply from the existing Adafruit board.
- Prevent backfeeding between supply variants; external variant also supports battery sensing.
- Hardware option to disable each populated indicator LED.
- Minimise complete-system sleep current, including regulator and indicators.
- Preserve demonstrated prototype autonomy of approximately three days in darkness under comparable test conditions.
- Verify charger settings, charging-temperature safety, cell protection, brownout and ADC calibration.

## Packaging
- Small plastic enclosure with PCB and battery; either under the Davis collector base or possibly beneath the funnel.
- Solar panel mounted to the front of the gauge base.
- Internal antenna initially; external antenna provision if range tests require it.
- External solar panel and bucket cables no longer than 10–30 cm.
- Corrosion-resistant, weather-resistant connectors or sealed cable glands.
- Protect against water, condensation, UV, solar heating and cable strain; maintain tipping mechanism clearance and drainage.
- Experiment with white exterior coating on black polycarbonate collector only after thermal and material compatibility testing.

## Verification
- Test first-tip capture, bounce, rapid successive tips, NVS endurance and reset behavior.
- Measure current in wake, transmit and sleep states, and confirm three-day autonomy.
- Verify charger/power path and LED disable options.
- Measure mechanical clearances and RF range with the final enclosure and battery installed.
- Confirm ingress protection, connector corrosion resistance, mounting and service access.
