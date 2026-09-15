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

The GitHub installation currently exposes seven repositories:

| Repository | Relevance to LoRa Rain Gauge | Initial assessment |
|---|---|---|
| `smr547/lora-rain-gauge` | Production repository | Target, not prior art |
| `smr547/qp-lab` | QP/C++, HSM, ESP32 and LilyGO/LoRa experiments | High |
| `smr547/collab` | Rain-gauge collaboration model and generated signal artefacts | High |
| `smr547/barking-owl-power-flow` | SignalK webapp/delta consumption and Barking Owl deployment experience | High |
| `smr547/signalk-modbus-plugin` | SignalK server plugin and delta production | High |
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

## 2. `collab`

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

## 3. `signalk-modbus-plugin`

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

## 4. `barking-owl-power-flow`

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

### SignalK authentication / recent EV monitoring work

**Disposition:** **INVESTIGATE**

The User specifically identified recent EV monitoring work as having solved SignalK authentication in a way likely to suit the LoRa base station. The first default-branch code search did **not** locate an obvious authentication implementation in this repository.

Possible explanations include a different path, branch, recent commit, or another of the selected repositories. This is a high-priority follow-up item because it may determine whether the base station should publish as an authenticated external client or use an in-process SignalK plugin boundary.

---

## 5. `solar_monitor`

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
3. **LoRa-capable platform:** `qp-lab` has a LilyGO T3 build target, but this survey has not yet found a complete rain-gauge LoRa TX/RX implementation.
4. **SignalK producer:** `signalk-modbus-plugin` demonstrates native server-side delta injection.
5. **SignalK consumer/dashboard:** `barking-owl-power-flow` demonstrates a deployable SignalK webapp and live delta consumption.
6. **Embedded SignalK precedent:** `solar_monitor` demonstrates SensESP publication, but also reminds us to keep credentials out of source.
7. **Authentication:** the specifically remembered recent authenticated EV-monitoring implementation remains to be located.

These findings reinforce the proposed architecture boundary: **LoRa messages should describe sensor observations, not SignalK deltas.** SignalK translation belongs on the base-station/server side.

## Follow-up survey

Before migration decisions are finalised:

- locate the remembered recent SignalK authentication solution;
- inspect repository history/branches where default-branch search is insufficient;
- locate any complete LoRa TX/RX experiments and radio configuration/range-test evidence;
- inspect the fuller historical rain-gauge collaboration model, if retained in repository history;
- identify actual hardware used in experiments (LilyGO variant, LoRa chipset, tipping-bucket hardware and pin assignments);
- identify executable BucketSensor/QP examples beyond the design working paper;
- review SignalK path conventions appropriate for rainfall and node health;
- determine which findings warrant product ADRs.

## Status

**Initial survey complete; detailed archaeology in progress.**

No source code has been migrated by this inventory.
