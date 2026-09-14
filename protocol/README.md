# LoRa Application Protocol

## Purpose
This directory defines the application-level protocol used between remote LoRa sensor nodes and the base station.

## Scope
Packet framing, protocol versioning, node identification, message types, payload formats, sequencing, integrity behaviour, examples and protocol test vectors belong here.

## Design principle
LoRa messages are not SignalK messages. Remote nodes report observations using a small transport-appropriate protocol; semantic translation to SignalK occurs on the base-station side of the system.

## Does not belong here
Sensor-specific processing belongs with the sensor implementation. SignalK path mappings belong in `signalk/`. Deployment-specific radio settings belong with deployment documentation where appropriate.

## Relationships
The protocol is the stable seam between sensor spokes and the base-station hub and should be capable of supporting future sensor types without coupling them to SignalK.

## Status
Version 1 will initially support the rain-gauge use case while providing a clean path for additional message types.
