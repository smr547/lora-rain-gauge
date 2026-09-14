# Requirements

## Purpose

This directory records what the product must do and how satisfaction of those requirements will be demonstrated.

The requirements documentation is deliberately separated from architecture and implementation. Requirements describe required behaviour, qualities and constraints; architecture and ADRs describe how those requirements are satisfied.

## Contents

### `user-requirements.md`

The User Requirements Specification (URS) records requirements from the Users' point of view.

User requirements describe the outcomes and capabilities that matter to Users without unnecessarily prescribing implementation details. They are the starting point for the engineering design and should remain understandable to non-developer stakeholders.

Examples include the ability to view today's rainfall, inspect historical rainfall, recognise stale data and operate the system unattended.

### `system-requirements.md`

The System Requirements Specification (SRS) will contain the engineering requirements derived from the User Requirements.

System requirements translate User needs into precise, testable obligations on the complete system or one of its major subsystems. They may define behaviour, interfaces, performance, environmental constraints, persistence, communications, diagnostics and other engineering properties.

A single User Requirement may give rise to several System Requirements. Conversely, one System Requirement may support more than one User Requirement.

### `verification-matrix.md`

The verification matrix provides traceability from requirements to evidence that those requirements have been satisfied.

Its intended chain is:

```text
User Requirement
      ↓
System Requirement(s)
      ↓
Architecture / implementation
      ↓
Verification method or test
      ↓
Evidence / result
```

The matrix should make it possible to determine, for every accepted requirement, how the delivered system demonstrates compliance.

## Requirement identification convention

Requirement identifiers are stable engineering references rather than paragraph numbers.

The initial User Requirements use identifiers of the form:

```text
UR-RG-014
│  │   └── unique numeric identifier
│  └────── Rain Gauge product requirement set
└───────── User Requirement
```

The prefix identifies the kind and scope of the requirement. For example:

- `UR-RG-xxx` — User Requirement for the LoRa Rain Gauge product;
- `SR-RG-xxx` — system-level Rain Gauge requirement;
- `SR-NODE-xxx` — rain-gauge node requirement;
- `SR-BS-xxx` — base-station requirement;
- `SR-SK-xxx` — SignalK integration requirement; and
- `SR-DASH-xxx` — dashboard requirement.

These prefixes are an initial convention and may be refined as the system requirements are developed, but any identifier already referenced elsewhere in the engineering record should remain stable.

## Numbering ranges and intentional gaps

Numbers are grouped into broad subject ranges. For the initial User Requirements:

```text
001–009   Rainfall measurement
010–019   User display
020–029   Operation and maintenance
030–039   Future expansion
040–049   Ownership, documentation and longevity
```

The gaps are intentional. They allow new requirements to be inserted beside related requirements without renumbering existing ones.

The numbers do **not** imply priority, implementation order or importance.

## Identifier stability

Once a requirement identifier has been used in the engineering record, it should not be silently renumbered or reused for a different requirement.

This matters because the identifier may subsequently appear in:

- system requirements;
- ADRs;
- architecture documents;
- source-code comments;
- test procedures;
- verification records;
- issues and pull requests; or
- historical releases.

A stable identifier therefore becomes part of the project's long-term traceability.

## Changed and superseded requirements

Requirements will evolve as User understanding and the engineering design mature.

Minor editorial improvements that do not change the meaning of a requirement may retain the same identifier.

If the meaning changes materially, the history should be explicit. A requirement that is no longer applicable should be marked as **superseded**, **withdrawn** or otherwise retired rather than deleted and having its identifier reused.

For example:

```text
UR-RG-012 — SUPERSEDED
Superseded by UR-RG-015 and UR-RG-016.
```

This preserves the meaning of older commits, ADRs, test reports and released documentation that may still refer to `UR-RG-012`.

## Traceability principle

The long-term objective is bidirectional traceability:

- from a User Requirement to the System Requirements and verification evidence that satisfy it; and
- from a System Requirement or verification result back to the User need that justified it.

Traceability should be useful rather than bureaucratic. The purpose is to make engineering intent and verification understandable to future maintainers, not merely to populate a matrix.

## Does not belong here

Implementation choices belong in architecture documents or ADRs. Detailed hardware and software design belongs with the relevant system component. Test implementation may live under `tests/` or with a component, while this directory records the requirement-to-verification relationship.

## Status

The User Requirements Specification is currently a draft for User review. System requirements and verification traceability will follow as Version 1 is defined.
