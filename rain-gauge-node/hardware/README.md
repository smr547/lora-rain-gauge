# Rain gauge node hardware — Revision A

Design baseline dated 2026-10-14. Initial build: 5–10 instruments.

The custom PCB will use ESP32 and SX1276 (915 MHz) modules, firmware-based bucket counting, and optional integrated BQ25185 solar charging with a 3.3 V regulator. Alternatively it will accept power from the existing external Adafruit module. The single-cell 3.7 V Li-ion/LiPo battery is housed with the electronics. Battery voltage sensing and hardware-disable options for indicator LEDs are required.

The small plastic enclosure may fit beneath the Davis funnel or beneath the gauge base. Solar panel and bucket cables are at most 10–30 cm, with corrosion-resistant weatherproof terminations. Start with an internal antenna, retain an external option. Existing prototype operation for three days without sunlight is the autonomy baseline.

Reference designs:
- https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series
- https://github.com/adafruit/Adafruit-bq25185-with-3.3V-Buck-PCB

Firmware reference: https://github.com/smr547/lora_experiments branch e1-rain-gauge-v3. QP firmware remains a separate development stream. Confirm exact reference design revisions, power behavior, wake reliability, environmental suitability and antenna performance before schematic release.
