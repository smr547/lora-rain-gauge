# lora-rain-gauge
Rain gauge designed for remote installtions


## Repo structure
The proposed repository structure is

```
lora-rain-gauge/
│
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
│
├── docs/
│   ├── requirements/
│   │   ├── user-requirements.md
│   │   ├── system-requirements.md
│   │   └── verification-matrix.md
│   │
│   ├── architecture/
│   │   ├── system-overview.md
│   │   ├── communications.md
│   │   ├── data-flow.md
│   │   └── diagrams/
│   │
│   ├── adr/
│   │   ├── ADR-0001-v1-scope.md
│   │   ├── ADR-0002-lora-topology.md
│   │   ├── ADR-0003-rainfall-counter-semantics.md
│   │   └── ...
│   │
│   ├── operation/
│   │   ├── user-guide.md
│   │   ├── maintenance.md
│   │   ├── troubleshooting.md
│   │   └── handover.md
│   │
│   └── development/
│       ├── build-environment.md
│       ├── programming.md
│       └── test-strategy.md
│
├── rain-gauge-node/
│   ├── firmware/
│   ├── hardware/
│   │   ├── schematic/
│   │   ├── wiring/
│   │   ├── enclosure/
│   │   └── bom.md
│   ├── tests/
│   └── README.md
│
├── base-station/
│   ├── firmware/
│   ├── hardware/
│   │   ├── schematic/
│   │   ├── wiring/
│   │   └── bom.md
│   ├── tests/
│   └── README.md
│
├── protocol/
│   ├── lora-message-format.md
│   ├── node-identification.md
│   ├── message-types.md
│   └── examples/
│
├── signalk/
│   ├── adapter/
│   ├── paths.md
│   ├── delta-examples/
│   ├── configuration/
│   └── README.md
│
├── dashboard/
│   ├── design.md
│   ├── configuration/
│   ├── screenshots/
│   └── README.md
│
├── deployment/
│   └── barking-owl/
│       ├── README.md
│       ├── site-notes.md
│       ├── configuration/
│       ├── device-register.md
│       ├── installation/
│       ├── photos/
│       └── acceptance-test.md
│
├── tests/
│   ├── integration/
│   ├── system/
│   └── field/
│
├── tools/
│
└── history/
    └── prior-art.md
```
