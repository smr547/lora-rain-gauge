# Barking Owl Rainfall Monitoring System
## User Requirements Specification — Version 0.1 Draft

**Document status:** Draft for User review  
**Initial deployment:** Barking Owl  
**Project:** LoRa Rain Gauge  
**Date:** 14 September 2026

---

## 1. Purpose

The Barking Owl Rainfall Monitoring System will provide Users with reliable, continuously available rainfall information without requiring routine technical intervention.

The first delivered system will measure rainfall using a remotely located rain gauge and present current and historical rainfall information through a simple dashboard.

The rainfall system is also intended to become the first component of a broader environmental monitoring system. Future sensors may measure other weather and farm quantities while sharing the same general communications and information infrastructure.

This document describes requirements from the Users' point of view. It deliberately avoids prescribing particular implementation technologies except where they are part of the intended product concept.

---

## 2. Users

The primary Users require straightforward access to current and historical rainfall information.

Future site occupants or operators may require access to the same information. A technically competent maintainer may need to diagnose, repair, replace or extend the system.

The system should not require ordinary Users to understand its internal hardware, communications network or software architecture.

---

## 3. Rainfall Measurement

### UR-RG-001 — Permanent rainfall measurement
The system shall measure rainfall using a permanently installed outdoor rain gauge.

### UR-RG-002 — Useful rainfall accuracy
The system shall record rainfall events sufficiently accurately to provide useful daily and historical rainfall totals.

### UR-RG-003 — Autonomous measurement
Rainfall measurements shall continue to be collected without requiring a computer, browser or dashboard to remain open.

### UR-RG-004 — Tolerance of communications interruptions
Temporary interruption of the communications link or base-station processing shall not, where reasonably practicable, result in loss of accumulated rainfall measurements.

---

## 4. User Display

### UR-RG-010 — Browser access
Users shall be able to view rainfall information using an ordinary web browser on their normal devices, both locally or from any location with internet access

### UR-RG-011 — Today's rainfall
The main display shall prominently show the rainfall recorded today.

### UR-RG-012 — Recent rainfall totals
The display shall provide useful recent rainfall totals, including:
- yesterday (local midnight to midnight);
- last 24 hours
- since 9am
- the previous seven days;
- the current month; and
- the current year.

### UR-RG-013 — Historical rainfall
Users shall be able to view graphs of historical rainfall.

### UR-RG-014 — Data freshness
The display shall make it reasonably apparent whether the displayed rainfall information is current or has stopped updating.

---

## 5. Operation and Maintenance

### UR-RG-020 — Unattended operation
The installed system shall normally operate unattended.

### UR-RG-021 — Outdoor operation
Outdoor equipment shall be suitable for long-term operation in the environmental conditions experienced at the deployment site (high winds, temperature extremes).

### UR-RG-022 — Low routine maintenance
Routine maintenance requirements, including battery replacement where applicable, shall be kept low and shall be clearly documented.

### UR-RG-023 — Diagnosability
A failure of the rain gauge, communications link or supporting system should be diagnosable without specialist test equipment wherever reasonably practicable.

### UR-RG-024 — System health
The system shall retain sufficient health information to assist a maintainer in identifying failures such as a depleted battery, loss of communication, false bucket trips and tipping mechanism faults.

---

## 6. Future Expansion

### UR-RG-030 — Foundation for environmental monitoring
The rainfall monitoring system shall form the first part of a future environmental monitoring system.

### UR-RG-031 — Multiple remote sensors
The system shall permit additional remote sensor units to communicate through the same base station or communications infrastructure.

### UR-RG-032 — Independent expansion
Addition of another sensor unit shall not require replacement or significant modification of an existing operational rain gauge.

### UR-RG-033 — Future measurements
Future sensor units may measure quantities including:
- air temperature;
- relative humidity;
- atmospheric pressure;
- wind speed;
- wind direction;
- water-tank level; and
- other weather, environmental or farm measurements.

### UR-RG-034 — Common presentation
Measurements from future sensors shall be capable of being presented through the same general user interface as rainfall measurements.

---

## 7. Ownership, Documentation and Longevity

### UR-RG-040 — Independence from original developer
The system shall not depend upon its original developer for continued operation.

### UR-RG-041 — Maintainability
The hardware, software, configuration, installation and maintenance procedures shall be sufficiently documented for another technically competent person to maintain the system.

### UR-RG-042 — Version-controlled engineering record
Source code and engineering documentation shall be maintained under version control.

### UR-RG-043 — Reproducibility
It shall be possible to reconstruct or replace the principal system components using the project documentation.

### UR-RG-044 — Installed-component identification
Installed components shall be identifiable and traceable to their corresponding documentation and configuration.

---

## 8. Initial Definition of Success

The first version will be considered successful from a User perspective when:

1. a physical rain gauge is installed at the deployment site;
2. rainfall is measured automatically and reliably;
3. measurements are communicated to the site's information system without routine User intervention;
4. Users can readily see today's rainfall;
5. useful recent rainfall totals are available;
6. historical rainfall can be graphed;
7. it is apparent when measurements have stopped updating;
8. the installed system can normally operate unattended; and
9. sufficient documentation exists for another technically competent person to maintain or replace it.

---

## 9. Matters for User Review

This draft is intended to start a conversation with Users. In particular, their views are requested on:

- What information should appear on the main rainfall dashboard?
- Which rainfall periods or totals are most useful?
- How far back should historical rainfall information be retained?
- On which devices are Users most likely to view the dashboard?
- Would warnings or notifications about heavy rain, prolonged dry periods or equipment failure be useful?
- What level and frequency of routine maintenance would be acceptable?
- How important is continued operation during Internet or power outages?
- Which additional weather measurements would Users most like to see next?
- Which non-weather measurements, such as tank levels, might be useful in the future?
- Is there anything else Users would expect from a useful rainfall monitoring system?

---

## 10. Review Record

| Version | Date | Status | Reviewers | Notes |
|---|---|---|---|---|
| 0.1 | 14 September 2026 | Draft | Users | Initial draft for User review |

---

*This is a User Requirements document. Detailed engineering requirements, architecture, communications protocols, SignalK integration, hardware selections and implementation decisions will be documented separately.*
