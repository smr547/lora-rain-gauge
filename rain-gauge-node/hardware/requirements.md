# Rain gauge node Rev A — requirements
Date: 2026-10-14. Initial design baseline; values not yet verified are marked as targets.

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
