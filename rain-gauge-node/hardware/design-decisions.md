# Rev A hardware decisions
Recorded 2026-10-14.

## Agreed
1. Develop 5–10 boards for our own installations, in KiCad.
2. Use an ESP32 module and SX1276 915 MHz LoRa module on a custom PCB, rather than a complete LilyGO development board or bare RF ICs.
3. Count tipping-bucket events in the ESP32 after wake; no external pulse counter.
4. Support optional populated on-board BQ25185-based solar charger and 3.3 V regulator, or an external Adafruit power module. Power options are assembly alternatives, not parallel connected supplies.
5. House a single-cell nominal 3.7 V lithium battery inside the instrument enclosure.
6. Include battery voltage sensing and a hardware option to disable indicator LEDs.
7. Prefer an internal antenna inside a plastic enclosure; preserve an external antenna option.
8. Aim to fit the enclosure under the Davis gauge base or inside beneath the funnel, subject to measurement.
9. Use short (10–30 cm maximum) corrosion-resistant weatherproof solar and bucket connections.
10. Investigate white paint on the black polycarbonate collector for thermal performance, subject to compatibility testing.

## Open choices
- Exact ESP32 and LoRa module part numbers, GPIO map and wake timing.
- Battery capacity, charger current, thermal protection, ADC circuit, regulator and power selection links.
- Antenna layout and connector, PCB dimensions, enclosure and cable terminations.
- Debug header/pads and manufacturing test points.
- Whether the enclosure can safely sit within the collector, without moisture or drainage problems.

## Software and source control
- Product repo: smr547/lora-rain-gauge.
- QP development branch: feature/timer-contract-validation.
- Working prototype: smr547/lora_experiments, branch e1-rain-gauge-v3.
- Before validation, record the exact firmware commit deployed on the prototype, not just its branch name.
- Keep design files, BOM, assembly variants, manufacturing files and PCB revision identifiers under rain-gauge-node/hardware/.
- Do not modify the software branches as part of the hardware baseline.

## Reference designs
- LilyGO LoRa Series: https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series
- Adafruit BQ25185/3.3 V Buck: https://github.com/adafruit/Adafruit-bq25185-with-3.3V-Buck-PCB

Confirm exact upstream schematic revisions and licenses before importing or adapting their designs.
