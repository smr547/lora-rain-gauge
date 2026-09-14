# Base Station

## Purpose
This directory contains the design and implementation of the LoRa base-station appliance.

## Scope
Base-station firmware/software, hardware, configuration guidance and component-specific tests belong here.

## Responsibilities
The base station receives and validates LoRa messages, distinguishes remote nodes and message types, maintains appropriate per-node state, and passes observations toward the SignalK integration.

The base station is intended to act as a hub for multiple sensor spokes. The rain gauge is the first spoke; future sensors may include weather and farm instrumentation.

## Does not belong here
Sensor-node implementation belongs in the relevant sensor repository or directory. Shared radio application protocol definitions belong in `protocol/`.

## Relationships
Remote nodes communicate with the base station over LoRa. The base station feeds observations to the SignalK integration and ultimately to storage and dashboards.

## Status
Version 1 is under development. Multi-node capability is an architectural requirement even though the rain gauge is the first deployed sensor.
