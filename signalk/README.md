# SignalK Integration

## Purpose
This directory defines and implements the boundary between the LoRa sensor system and SignalK.

## Scope
SignalK path definitions, unit conventions, delta generation, adapter/service implementation, configuration examples and integration tests belong here.

## Does not belong here
The LoRa wire protocol belongs in `protocol/`. Dashboard presentation belongs in `dashboard/`.

## Relationships
The base station provides sensor observations to this layer. SignalK then provides a standard information boundary for storage, dashboards and other consumers.

## Status
Version 1 will provide rainfall observations and the information needed to support current and historical rainfall presentation.
