# Prior Work Inventory

## Purpose

This document records rain-gauge-related assets and adjacent engineering work developed before the production `lora-rain-gauge` repository.

The inventory is deliberately performed **before migration**. Finding an asset does not imply that it belongs in the Version 1 product.

## Inventory method

Each relevant asset is classified as one of:

- **REUSE** — suitable for direct use with little or no change.
- **ADAPT** — useful work that should be brought into the product after modification.
- **REFERENCE** — valuable experimental evidence or design history that should remain in its original repository.
- **OBSOLETE** — superseded work retained only for historical context.
- **INVESTIGATE** — potentially relevant, but more work is needed before choosing a disposition.

Where practical, source paths and blob SHAs are recorded so that this survey remains reproducible even as the source repositories evolve.

## Repositories surveyed

The GitHub installation currently exposes nine repositories:

| Repository | Relevance to LoRa Rain Gauge | Initial assessment |
|---|---|---|
| `smr547/lora-rain-gauge` | Production repository | Target, not prior art |
| `smr547/qp-lab` | QP/C++, HSM, ESP32 and LilyGO/LoRa experiments | High |
| `smr547/lora_experiments` | Working LilyGO LoRa hardware, deep sleep/wake experiments and emerging packet protocol | Very high |
| `smr547/collab` | Rain-gauge collaboration model and generated signal artefacts | High |
| `smr547/barking-owl-power-flow` | SignalK webapp/delta consumption and Barking Owl deployment experience | High |
| `smr547/signalk-modbus-plugin` | SignalK server plugin and delta production | High |
| `smr547/sdm230-signalk` | Authenticated external SignalK publication, automatic device access provisioning and EV-meter deployment | High |
| `smr547/solar_monitor` | ESP32/SensESP to SignalK example | Medium |
| `smr547/family-history` | No expected product relevance | None; not surveyed further |

This is an **initial survey**, not yet an exhaustive file-by-file audit.

---

## 1. `qp-lab`

### QP/C++ ESP32 baseline and LilyGO target

**Source:** `smr547/qp-lab`  
**Paths:** `blinky-button/README.md`, `blinky-button/platformio.ini`  
**Observed blob SHAs:** `94878767ea6e7f28cb50aa3d1d92969eefdd6a7e`, `aa1719d1cad393ddb757df564cb460ea54c32b7b`  
**Disposition:** **ADAPT**

The lab establishes a known QP/C++/ESP32/PlatformIO baseline with Q_SPY tracing. It also adds a `lilygo-t3-v16` PlatformIO environment specifically to explore QP for a weather-station application using LoRa.

Useful assets include:

- ESP32/QP build structure;
- LilyGO T3 target configuration;
- Q_SPY engineering-build practice;
- the working ESP32 QP port/toolchain experience.

**Migration note:** do not copy the Blinky application wholesale. Extract the proven platform/toolchain configuration and apply it to the Version 1 rain-gauge node after the node architecture is settled.

### Embedded HSM design practices / BucketSensor reasoning

**Source:** `smr547/qp-lab`  
**Path:** `docs/HSM_design_practices.md`  
**Observed blob SHA:** `5567dbfbc9ce1978a782a2415a85724d2a2a106c`  
**Disposition:** **REFERENCE**, with selected principles to **ADAPT**

The working paper captures substantial reasoning directly motivated by the rain gauge:

- short, non-blocking run-to-completion actions;
- time represented by events rather than delays;
- explicit physical observation events;
- distinction between observations, domain events, infrastructure events and temporal events;
- BucketSensor debounce/confirmation behaviour;
- separation into collaborating Active Objects;
- instrumentation using Q_SPY.

The document is broader than the rain-gauge product and should remain in `qp-lab`. Product-specific consequences should later be captured in the rain-gauge architecture/ADRs rather than duplicating the working paper.

---

## 2. `lora_experiments`

### Initial architecture and packet philosophy

**Source:** `smr547/lora_experiments`  
**Path:** `2026-06-13-lora-experiments-initial-notes.md`  
**Observed blob SHA:** `86e0956943e1504b86f400b1f95998116d44e6e4`  
**Disposition:** **ADAPT — HIGH VALUE**

This repository is direct rain-gauge prior art and should have been included in the first survey. The initial notes already establish several important product ideas: private LoRa rather than BLE/LoRaWAN, one gateway serving many sensor nodes, and—most importantly—transmitting **absolute counts rather than individual tip events** so that lost packets or gateway outages need not lose accumulated rainfall.

That packet philosophy should be reviewed explicitly against the Version 1 requirements and is a strong candidate for a product ADR.

### LilyGO T3 V1.6.1 / SX1276 hardware bring-up

**Source:** `smr547/lora_experiments`  
**Paths:** `e1/roaming/src/main.cpp`, `e1/base/src/main.cpp`, corresponding `platformio.ini` files  
**Observed blob SHAs:** `b1729179c72a0ab6766d593ad3b3727b9f1f1bdf`, `300e3ce88a685688be8d1a24e964f1f88c5439c9`, `e0184e4f3fbd9525ecb218168f6412519d62eea3`, `25e336813975e924efbc89f10c992a7981102cdf`  
**Disposition:** **REUSE / ADAPT — HIGH VALUE**

The experiment contains concrete, working hardware knowledge rather than merely a prospective LoRa target:

- LilyGO T3 V1.6.1 / SX1276 SPI and DIO pin mapping;
- RadioLib/PlatformIO configuration;
- 915 MHz operation with 125 kHz bandwidth, SF7 and coding rate 4/5;
- transmitter and continuously receiving base-station examples;
- RSSI and SNR reporting at the receiver;
- application-level packet validation.

The production project should preserve the proven hardware mapping and radio bring-up while moving tunable radio parameters into an explicit configuration/protocol definition.

### Deep sleep, timer wake and bucket-tip wake

**Source:** `smr547/lora_experiments`  
**Path:** `e1/roaming/src/main.cpp`  
**Disposition:** **ADAPT — HIGH VALUE**

The roaming-node experiment demonstrates the core low-power mechanism needed by the rain gauge:

- ESP32 deep sleep after each wake cycle;
- timer wake for periodic heartbeat/endurance operation;
- EXT0 wake from an active-low tipping-bucket contact on RTC-capable GPIO13;
- RTC pull-up configuration while the digital GPIO domain is powered down;
- protection against immediate repeated wake when the level-sensitive bucket contact remains closed;
- radio sleep before ESP32 deep sleep;
- RTC-retained sequence and wake counters; and
- wake-reason classification.

This is close to the required Version 1 node behaviour, but production integration must reconcile the raw wake/contact handling with the QP/HSM debounce and fault-detection work identified in `qp-lab` and `collab`.

### Battery and supply monitoring

**Source:** `smr547/lora_experiments`  
**Path:** `e1/roaming/src/main.cpp`  
**Disposition:** **ADAPT**

The experiment samples both the regulated supply and LiPo terminal voltage using calibrated `analogReadMilliVolts()`, averaging and divider compensation. This is useful for node-health telemetry.

The associated design conversation also identified that a permanent 100k/100k battery divider itself consumes material standby current. The production low-power design should therefore measure actual board-level sleep current and revisit the divider/power architecture rather than copying the prototype unchanged.

### Emerging telemetry protocol — Version 2 experiment

**Source:** `smr547/lora_experiments`  
**Paths:** `e1/roaming/src/main.cpp`, `e1/base/src/main.cpp`  
**Disposition:** **ADAPT — PROTOCOL INPUT**

The transmitter and receiver share a packed binary `TelemetryPacket` containing:

- magic byte;
- protocol version;
- node ID;
- message type;
- sequence number;
- wake-cycle uptime;
- temperature field (currently synthetic);
- supply voltage;
- battery voltage;
- wake reason; and
- CRC-16/CCITT.

The base rejects bad magic, incompatible protocol versions and application-CRC failures, and records RSSI/SNR separately as receiver observations. The transmitter increments its retained sequence only after a successful RadioLib transmission.

This is an **experimental protocol, not yet the Version 1 product protocol**. In particular, the current packet does not yet carry the absolute rain-tip count advocated by the initial design notes. The production protocol should retain the useful framing/versioning/node-identification/error-detection ideas while being specified independently under `protocol/`.

---

## 3. `collab`

### Rain Gauge AO collaboration model

**Source:** `smr547/collab`  
**Path:** `examples/rain-gauge.collab`  
**Observed blob SHA:** `c007ad8336415d48a2691be1257eb8be6aa75336`  
**Disposition:** **ADAPT**

The current example identifies `BucketSensorAO` and `ControlAO` and the semantic events:

- `BUCKET_TIPPED`;
- `BUCKET_SENSOR_BUSY`;
- `BUCKET_SENSOR_IDLE`;
- `RAIN_BUCKET_FAULT`.

This is valuable design input, but it is also an example used to develop the `collab` language. It must therefore be reviewed against Version 1 product requirements before becoming production architecture.

### Generated collaboration diagram

**Source:** `smr547/collab`  
**Path:** `examples/rain-gauge.puml`  
**Observed blob SHA:** `74accc52c60d0a87b493d41e61b11f598ece4030`  
**Disposition:** **REFERENCE**

The generated PlantUML is evidence of the model/tooling pipeline. The `.collab` semantic source is the more important prior-art asset; generated output should not be treated as authoritative product design.

### Multiple-source signal semantics

**Source:** `smr547/collab`  
**Path:** `docs/Decisions/ADR-0003-multiple-sources-for-one-signal.md`  
**Observed blob SHA:** `eabb320edd774631141bd5c4443e0e0abb1b62ed`  
**Disposition:** **REFERENCE**

This ADR arose from a richer rain-gauge model in which `BUCKET_SWITCH_CLOSING` could originate from both a reed-switch ISR and `ControlAO`. Its receiver-centric distinction between signal meaning and sender provenance may be useful when we reconstruct the Version 1 event model.

**Important:** this is a decision about `collab` semantics, not automatically a product ADR.

---

## 4. `signalk-modbus-plugin`

### Server-side SignalK delta production

**Source:** `smr547/signalk-modbus-plugin`  
**Path:** `index.js`  
**Disposition:** **ADAPT / REFERENCE**

The plugin demonstrates the cleanest server-side SignalK publication mechanism found in this first survey. It constructs a delta containing path, value, context, source and timestamp and injects it through:

`app.handleMessage(PLUGIN_ID, deltas)`

This is particularly relevant to the LoRa base station if its SignalK boundary is implemented as, or through, a SignalK server plugin.

Other useful practices include provider status/error reporting and whole-plugin recovery after communications failure.

**Architectural observation:** a base-station integration running inside SignalK may avoid the external-client authentication problem entirely. This should be evaluated, not assumed.

---

## 5. `barking-owl-power-flow`

### SignalK webapp and delta consumer

**Source:** `smr547/barking-owl-power-flow`  
**Paths:** `public/index.html`, `package.json`, `Makefile`  
**Observed `public/index.html` blob SHA:** `6844203eb3614a2e2933c85bb7284fc249769183`  
**Disposition:** **ADAPT**

This repository provides useful production-adjacent experience for the rain dashboard:

- packaging a webapp for installation on the SignalK server;
- WebSocket consumption of SignalK deltas;
- handling updates in browser-side JavaScript;
- stale/update-status presentation patterns;
- Barking Owl deployment/build workflow.

The power-flow visualisation itself is application-specific and should not be copied as the rainfall UI.

---

## 6. `sdm230-signalk`

### Authenticated external SignalK publisher and automatic device provisioning

**Source:** `smr547/sdm230-signalk`  
**Paths:** `README.md`, `src/signalk_access.py`, `src/signalk_ws.py`, `src/publisher.py`, `systemd/sdm230-signalk.default`  
**Observed blob SHAs:** `553f71323d0090fd25e1837de630bf44a0032f2f`, `e570badc89353a5a8ada69535dbe8dc79076016d`, `a3b25a9af6be552d34848913f43c672cf4fa8913`, `65bb47f4650902534ba5abbf4b9c02c48052a5b3`, `fa9e72c1fb2c47d9e10fffffd53af571eb082ec7`  
**Disposition:** **ADAPT — HIGH VALUE**

This is the previously remembered EV-monitoring SignalK authentication work. It provides a well-separated implementation of the commissioning and authenticated-publication problem that the LoRa base station is likely to face.

Useful assets include:

- persistent per-installation client UUID creation;
- SignalK device access request submission and approval polling;
- persistent approved-token storage with restrictive local permissions (`0700` directory and `0600` files);
- authenticated WebSocket connection using `Authorization: Bearer <token>`;
- validation of the SignalK `hello` message and use of server `self` as the default context;
- metadata publication after connection/reconnection;
- reconnect behaviour; and
- systemd deployment/configuration practices that keep credentials out of the repository.

The architecture is already usefully factored: `signalk_access.py` owns provisioning and credential storage, while `signalk_ws.py` owns authenticated WebSocket transport. Neither is intrinsically coupled to an SDM230 meter.

**Migration note:** adapt/generalise these components for the base station rather than reimplementing SignalK authentication. Product-specific names, configuration paths and descriptions should change, while retaining the commissioning principle: first run requests access, an administrator approves it in SignalK, and subsequent operation uses securely stored credentials.

**Architectural consequence:** this gives Version 1 a credible external-publisher option alongside the in-process plugin approach demonstrated by `signalk-modbus-plugin`. The choice should be explicit rather than driven by authentication difficulty.

---

## 7. `solar_monitor`

### SensESP SignalK output

**Source:** `smr547/solar_monitor`  
**Path:** `src/main.cpp`  
**Observed blob SHA:** `11e91212ef34ea7f9db74651073b275bcbee7141`  
**Disposition:** **REFERENCE**

This older ESP32 example uses SensESP `SKOutputFloat` objects to publish solar measurements to SignalK. It demonstrates a working embedded-to-SignalK path and useful path/metadata conventions.

For Version 1, the LoRa sensor node should remain independent of SignalK semantics; therefore this is more useful as historical SignalK integration evidence than as node code to reuse.

**Security note:** the surveyed source contains hard-coded network credentials. They must not be migrated into the public rain-gauge repository. Any reusable implementation pattern must be separated from secrets/configuration.

---

## Initial findings

The survey already reveals several strong seams:

1. **Sensor behaviour:** `qp-lab` contains valuable QP/HSM and physical-observation design experience.
2. **Collaboration semantics:** `collab` contains a rain-gauge-specific AO vocabulary that should be reviewed rather than blindly adopted.
3. **LoRa hardware and low power:** `lora_experiments` contains working LilyGO/SX1276 TX/RX code, timer and bucket-contact wake, deep sleep, radio sleep, battery/supply monitoring and link-quality observations.
4. **Protocol:** `lora_experiments` contains a useful Version 2 experimental binary telemetry frame, while its earlier design notes establish the stronger rain-gauge principle of transmitting absolute tip counts rather than fragile tip events.
5. **SignalK producer:** `signalk-modbus-plugin` demonstrates native server-side delta injection.
6. **SignalK consumer/dashboard:** `barking-owl-power-flow` demonstrates a deployable SignalK webapp and live delta consumption.
7. **Embedded SignalK precedent:** `solar_monitor` demonstrates SensESP publication, but also reminds us to keep credentials out of source.
8. **Authentication:** `sdm230-signalk` contains the remembered EV-monitoring solution: automatic SignalK device access provisioning, persistent credentials and authenticated WebSocket publication. This is high-value prior art for the base station.

These findings reinforce the proposed architecture boundary: **LoRa messages should describe sensor observations, not SignalK deltas.** SignalK translation belongs on the base-station/server side.

## Follow-up survey

Before migration decisions are finalised:

- compare the external authenticated-publisher pattern in `sdm230-signalk` with the in-process plugin pattern in `signalk-modbus-plugin` and capture the Version 1 choice as an architectural decision;
- inspect repository history/branches where default-branch search is insufficient;
- turn the `lora_experiments` hardware/radio findings into an explicit Version 1 node hardware baseline and identify any remaining range-test evidence;
- reconcile its deep-sleep/bucket-wake mechanism with the QP/HSM debounce and fault model;
- specify the Version 1 LoRa message protocol under `protocol/`, explicitly deciding how absolute tip count, sequence number, node identity, health telemetry and protocol versioning interact;
- inspect the fuller historical rain-gauge collaboration model, if retained in repository history;
- identify actual hardware used in experiments (LilyGO variant, LoRa chipset, tipping-bucket hardware and pin assignments);
- identify executable BucketSensor/QP examples beyond the design working paper;
- review SignalK path conventions appropriate for rainfall and node health;
- determine which findings warrant product ADRs.

## Status

**Initial survey complete; detailed archaeology in progress.**

No source code has been migrated by this inventory.
