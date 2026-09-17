# LoRa Application Protocol — Version 1 Draft

**Status:** Draft for design review  
**Protocol version:** 1  
**Date:** 2026-09-17

## 1. Purpose

This document defines Version 1 of the application-level protocol used between remote LoRa sensor nodes ("spokes") and the base-station ("hub").

Version 1 is driven by the rain-gauge use case but is deliberately structured to support additional sensor types without coupling them to SignalK or to rain-gauge-specific fields.

This is a semantic specification first. Exact byte widths, offsets and byte order are intentionally left open until the semantics have been reviewed.

## 2. Design principles

1. **LoRa messages are not SignalK messages.** Spokes report sensor-domain observations; the base station translates them into SignalK.
2. **Prefer absolute state to transient events.** Where possible, a later message should allow recovery after an earlier message was lost.
3. **No acknowledgement is required for normal telemetry.** Version 1 is loss tolerant rather than packet-delivery reliable.
4. **Keep the common envelope small.** Sensor-specific values belong in specialised payloads.
5. **Preserve raw evidence.** The base station should expose useful raw/protocol observations as well as derived sensor observations.
6. **Separate observation from policy.** User accumulation periods, alarming and monitoring policy are downstream concerns.
7. **Design for evolution.** New message types and new versions of existing payloads should not unnecessarily invalidate deployed nodes.
8. **Make deployed firmware identifiable.** A node should be able to report the provenance of the firmware it is running.

## 3. Frame model

Every application frame has three logical parts:

```text
+-------------------------+---------------------------+-------------+
| Common envelope         | Type-specific payload     | Integrity   |
+-------------------------+---------------------------+-------------+
```

The specialised payload is a discriminated union selected by `message_type`. A frame contains exactly one payload type; it does not contain a large structure with fields reserved for every possible sensor.

### 3.1 Candidate common-envelope fields

The following semantics are currently required:

| Field | Purpose |
|---|---|
| `magic` | Recognise this application protocol |
| `protocol_version` | Version of common protocol/framing rules |
| `message_type` | Select specialised payload semantics |
| `payload_version` | Version of the selected payload schema |
| `payload_length` | Permit safe framing/skipping of unsupported payloads |
| `node_id` | Persistent identity of the physical/logical appliance |
| `boot_id` | Identify a node execution session across true resets |
| `sequence` | Order messages and diagnose loss/duplicates/out-of-order reception |

Field widths and encoding are TBD.

Values such as battery voltage, supply voltage and sensor measurements are deliberately **not** common-envelope fields merely because several sensor types may use them.

RSSI and SNR are receiver observations and are not transmitted by the spoke.

### 3.2 Integrity

LoRa PHY CRC failures are rejected by the radio stack.

Version 1 will also retain an application-level integrity check. The exact CRC algorithm and coverage are TBD; the prior experiment used CRC-16/CCITT.

Integrity should be checked before interpreting an otherwise untrusted specialised payload.

## 4. Versioning and compatibility

`protocol_version`, `message_type` and `payload_version` have different meanings.

Adding a new message type does not by itself require a new protocol version.

Changing one specialised payload should, where practical, advance that payload's version without forcing unrelated message types to change.

A receiver encountering a valid but unsupported message type or payload version must not treat it as radio corruption. It should ignore the unsupported payload safely and may publish/log a diagnostic observation.

## 5. Initial message types

The numeric registry is TBD. The initial semantic registry is:

| Message type | Purpose | V1 status |
|---|---|---|
| `RAIN_GAUGE` | Report cumulative accepted bucket tips and rain-gauge-specific telemetry | Required |
| `NODE_IDENTITY` | Report appliance, hardware and running-firmware provenance | Required |

Future types may include air/weather observations, tank level and node-health messages.

A single `node_id` may emit more than one message type.

## 6. RAIN_GAUGE payload

### 6.1 Required semantic value

`tip_count` is the cumulative number of bucket tips accepted by the rain-gauge application during the current count/session semantics.

For the currently characterised Davis gauge, one accepted tip represents 0.2 mm rainfall. Whether the calibration belongs in protocol data, node configuration or downstream metadata remains TBD.

The packet does **not** represent a `BUCKET_TIPPED` QP event. The BucketAO/HSM is responsible for converting physical switch behaviour into accepted tips; the protocol reports resulting state.

### 6.2 Candidate rain-gauge telemetry

The Version 1 payload may additionally carry:

- battery voltage;
- regulated supply voltage;
- wake reason; and
- sensor/node status relevant to interpreting the observation.

Exact inclusion and encoding remain TBD.

### 6.3 Receiver interpretation

For two accepted observations from the same node and boot/session, with monotonically advancing state:

```text
delta_tips = current_tip_count - previous_tip_count
```

The base station may translate `delta_tips` into incremental rainfall and publish both the raw count and the derived observation.

Missing sequence numbers do not themselves imply missing rainfall. They are communications diagnostics. The cumulative tip count is the rainfall recovery mechanism.

## 7. Reliability behaviour

### 7.1 Lost packet

If an intermediate packet is lost, a subsequent absolute count recovers the accumulated change.

Example:

```text
received: seq 100, tip_count 420
lost:     seq 101, tip_count 421
received: seq 102, tip_count 422
```

The receiver derives two new tips since the last accepted observation.

### 7.2 Corrupt packet

A frame failing LoRa PHY CRC or application integrity validation is discarded and does not update accepted node state.

### 7.3 Duplicate packet

A duplicate must not generate duplicate rainfall. Sequence and absolute state allow duplicate detection.

### 7.4 Out-of-order packet

An older packet arriving after newer state has already been accepted must not move receiver state backwards or generate rainfall a second time.

Exact modular sequence comparison rules are TBD.

### 7.5 Deep sleep

Deep-sleep timer wake and bucket-input wake are normal continuation of a node session. Working counters may be retained in ESP32 RTC memory across deep sleep.

Deep-sleep wake must not by itself create a new `boot_id`.

### 7.6 Hard reset / power loss

A true restart begins a new boot/session identity. This prevents the base station from interpreting a reset counter as an ordinary backwards-moving count.

The exact semantics of `tip_count` across a new boot/session remain a V1 design item. In particular, we must decide whether the count is lifetime-persistent or session-relative.

### 7.7 Base-station outage

While the base station is unavailable, the spoke continues accumulating absolute state. When reception resumes within the same node session, the latest count can recover rainfall accumulated during the outage.

If the node loses its unreported count state during the same outage, those observations cannot be reconstructed unless the node has separately persisted them.

### 7.8 Base-station restart

The base station must retain enough durable per-node receiver state to resume interpretation without double-counting or treating an existing absolute count as entirely new rainfall.

The storage technology is TBD and depends partly on the base-station hardware decision.

### 7.9 Counter and sequence wrap

Counters will use widths and modular comparison arithmetic chosen so that wrap is either operationally negligible or unambiguous to the receiver.

### 7.10 Node replacement

`node_id` identifies an appliance independently of `boot_id`. Replacing an appliance creates an explicit identity/continuity boundary rather than being inferred solely from a counter discontinuity.

## 8. Base-station responsibilities

The base station should remain simple. Its protocol responsibilities are to:

- receive LoRa frames;
- validate transport/application integrity;
- parse supported envelope and payload versions;
- maintain the minimum per-node state needed for correct interpretation;
- reject/ignore duplicates, stale/out-of-order and unsupported messages appropriately;
- derive incremental observations where the protocol requires interpretation of cumulative state;
- preserve useful raw observations;
- publish observations to SignalK; and
- retain sufficient durable receiver state to survive its own restart.

It is **not** responsible for policy such as "node offline", "battery low", "rain today", "rain since 09:00" or user alarms. Those are downstream monitoring/dashboard functions.

## 9. NODE_IDENTITY payload

A deployed node should be able to report enough identity/provenance information for an engineer to determine what appliance is transmitting and what firmware source produced the running image.

Candidate semantics include:

- product/appliance identity;
- hardware revision;
- firmware semantic version;
- immutable Git commit identifier;
- source repository identifier or URL; and
- build/protocol information useful for support.

The repository URL need not be transmitted in every telemetry frame. `NODE_IDENTITY` may be sent at boot and/or occasionally, allowing the base station to cache and publish it.

Firmware version and commit identity should be injected by the build process rather than manually edited in source code.

This is the radio equivalent of a remotely readable appliance label and complements future physical UbiEstRes-generated Item labels.

## 10. SignalK boundary

SignalK path names and accumulation semantics are outside this wire protocol.

The base station may expose two classes of SignalK information:

1. **raw/engineering state** — node ID, boot ID, sequence, cumulative count, battery/supply measurements, RSSI, SNR, last reception and protocol/firmware identity;
2. **derived observations** — for example newly observed tips or incremental rainfall.

Historical totals and time-window calculations belong downstream.

## 11. Open Version 1 questions

Before freezing the binary layout we still need to decide:

- exact common-envelope field widths;
- byte order and packing rules;
- application CRC algorithm and coverage;
- numeric message-type registry;
- `node_id` allocation/provisioning;
- `boot_id` generation and persistence;
- exact rain-gauge counter persistence/session semantics;
- sequence and counter widths/wrap rules;
- whether node health is embedded in sensor payloads, a separate message type, or both;
- exact `NODE_IDENTITY` representation, including repository/commit encoding;
- base-station persistent receiver-state semantics;
- whether SignalK unavailability requires a durable store-and-forward queue;
- base-station implementation platform; and
- test vectors for encoding, corruption, loss, duplicates, reset and wrap.

## 12. Prior-art relationship

Version 1 draws on the experiments inventoried in `history/prior-art.md`, especially:

- `lora_experiments` for LilyGO/SX1276 operation, deep sleep, timer/bucket wake, sequence/version/CRC framing and telemetry;
- `qp-lab` and `collab` for BucketSensor event/state-machine reasoning;
- `sdm230-signalk` for authenticated external SignalK publication; and
- `signalk-modbus-plugin` and `barking-owl-power-flow` for SignalK integration and diagnostics.

The experimental Version 2 telemetry packet is prior art, not the normative Version 1 format defined here.
