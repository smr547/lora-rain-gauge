# Rain Gauge Node

## Purpose
This directory contains the design and implementation of the remote rain-gauge appliance.

## Scope
Firmware, hardware, enclosure information, bill of materials and node-specific tests belong here.

## Responsibilities
The node detects valid tipping-bucket events, maintains rainfall observation state, reports its state over LoRa and provides sufficient health information for unattended operation.

## Does not belong here
Base-station processing belongs in `base-station/`. Shared application-level LoRa protocol definitions belong in `protocol/`. SignalK semantics belong in `signalk/`.

## Relationships
The rain-gauge node is the first sensor spoke. It communicates with the base station using the shared LoRa protocol.

## Status
Version 1 is under development. Existing rain-gauge and QP experiments will be inventoried before production implementation is selected.
