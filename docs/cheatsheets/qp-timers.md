# QP/C++ + QM timer cheatsheet

A working recipe for the rain-gauge HSMs. This expands the timer notes in `qp-lab/blinky-button/docs/qp_qm_cheatsheet_sten.md`; it does not replace that broader QP/QM reference.

## Mental model

A `QTimeEvt` is owned by an active object (AO). The QP tick source advances its tick rate; expiry posts a signal to the owning AO's event queue. The HSM handles that signal during a later run-to-completion step. A timer is **not** a callback and does not execute the HSM action at the instant it expires.

In this application, `main.cpp` advances tick rate **0** at nominally 100 Hz; `BSP::TICKS_PER_SEC = 100`. The third constructor argument, `0U`, selects the tick-rate index, **not** a duration.

## Implementation recipe

- [ ] Declare a `QP::QTimeEvt` as an AO member in **QM**.
- [ ] Initialise it in the QM constructor with `this`, the correct `*_SIG`, and tick-rate index.
- [ ] Define meaningful duration constants in the **QM-owned file template** for that AO's `.cpp`; do not hand-edit generated code.
- [ ] Check tick frequency, integer conversion, minimum one tick, and representability of the desired period.
- [ ] Choose one-shot or periodic operation explicitly.
- [ ] Put arm/rearm/disarm calls in the appropriate **HSM actions** (typically state entry/exit or transitions).
- [ ] Decide what happens on normal completion, timeout, interruption, and a queued late timeout.
- [ ] Record an expected trace and compare it with QSPY observations.

### 1. Declare and construct (QM)

Radio class attribute:

```cpp
QP::QTimeEvt m_txTimer;
```

Radio constructor initialiser:

```cpp
: QActive(Q_STATE_CAST(&Radio::initial)),
  m_txTimer(this, RADIO_TX_TIMEOUT_SIG, 0U)
```

Use a distinct signal for each independently meaningful deadline. In QM transition triggers, omit the C++ `_SIG` suffix: `RADIO_TX_TIMEOUT`.

### 2. Put duration constants in the AO's QM file template

For `radio.cpp` (already used by this project):

```cpp
static constexpr std::uint32_t TX_TIMEOUT_TICKS =
    5U * BSP::TICKS_PER_SEC;
```

For a *hypothetical* 30 ms debounce interval in `tippingBucket.cpp`:

```cpp
static constexpr std::uint32_t DEBOUNCE_TICKS =
    30U * BSP::TICKS_PER_SEC / 1000U;

static_assert(DEBOUNCE_TICKS > 0U, "Debounce must last at least one tick");
```

The debounce value is illustrative, **not** an agreed rain-gauge setting. At 100 Hz, one tick is nominally 10 ms; integer division truncates. Avoid zero-tick results and do not assume sub-tick precision. A named duration belongs in the collaboration specification as well **when its value is part of the collaboration contract**.

### 3. One-shot: Radio transmission deadline

In the QM `Transmitting` **entry action**:

```cpp
m_txTimer.armX(TX_TIMEOUT_TICKS); // equivalent to armX(TX_TIMEOUT_TICKS, 0U)
```

On `RADIO_TX_DONE`, before the success/error choice:

```cpp
m_txTimer.disarm();
m_lastRadioError = BSP::radioFinishTransmit();
```

Also disarm in the `Transmitting` **exit action** so *every* departure, including timeout and future cancellation paths, has one cleanup policy. If this is added, remove the redundant transition-level disarm or document why both are intentional.

A one-shot timer expires once and remains disarmed. It is appropriate for debounce checks, transmission deadlines, and fault detection.

### 4. Periodic: one-second heartbeat example

Declare `m_heartbeatTimer` in the AO and construct it with `HEARTBEAT_SIG`, tick rate 0. In the QM `Running` entry action:

```cpp
static constexpr std::uint32_t HEARTBEAT_TICKS = BSP::TICKS_PER_SEC;
// Constant belongs in the QM .cpp file template, outside the generated state handler.

m_heartbeatTimer.armX(HEARTBEAT_TICKS, HEARTBEAT_TICKS);
```

The first argument is the initial delay; the nonzero second argument is the recurring interval. Handle `HEARTBEAT` in the appropriate state; disarm in `Running` exit:

```cpp
m_heartbeatTimer.disarm();
```

This is an illustrative pattern, not a request to add a heartbeat to the current rain-gauge model.

**Fly N Shoot:** its 30 Hz game clock is a collaboration-level cadence, not merely a private timeout. With a 100 Hz QP tick, `100 / 30` is not an exact integer period. Select a suitable clock/tick strategy before encoding `GAME_TICK` as a fixed-period `QTimeEvt`.

### 5. Disarm, rearm, and late events

```cpp
m_checkTimer.disarm();             // stop future expirations
m_checkTimer.rearm(CHECK_TICKS);    // reset/start a one-shot countdown
```

`rearm(nTicks)` resets the countdown (and returns whether the timer was armed before the call). Use `armX()` for an initially disarmed timer; use `rearm()` when restarting a countdown. Do not arm an already armed timer with `armX()`.

**Important:** disarming a timer does not recall an expiry event already queued for the AO. A late timeout may therefore be dispatched after a state transition. Handle it harmlessly in the new state (or use an explicit generation/phase policy if the same signal can ambiguously refer to a newer timer cycle). A different state ignoring an irrelevant timeout is often sufficient; verify this for each HSM.

For TippingBucket, specify separately when the debounce timer is armed, when it is cancelled, and when the stuck-closed fault timer starts/stops. Do not let a generic `TIMEOUT` silently serve two different meanings.

## What “QSPY trace expected/checked” means

Write down a **predicted event sequence**, enable the necessary records, run the firmware, and compare observation against prediction. For a deliberately uncompleted Radio transmission:

1. Radio enters `Transmitting` and arms `m_txTimer` for five seconds.
2. The 100 Hz tick task advances tick rate zero.
3. The timer expires and QP posts `RADIO_TX_TIMEOUT_SIG` to Radio.
4. Radio later gets/dispatches that event and transitions to `Fault`.

For a successful transmission, expect `RADIO_TX_DONE_SIG`, disarm, and a transition out of `Transmitting`; **no subsequent timeout transition** should occur for that transmission. An already queued timeout still needs safe handling.

Our existing BSP enables HSM transition/entry/exit/initialisation records. These show state changes but do **not**, by themselves, prove arming, expiry, posting, or dispatch. Temporarily enable the relevant QP time-event and AO event-post/get trace record groups supported by the installed QP version; retain the QS buffer critical-section discipline and avoid indiscriminately enabling all records on a busy serial link. Consult the actual installed `qs.hpp` record names before editing filters. Use `QS_BOOT` or a narrowly scoped user record if an explicit action marker is helpful.

Check timestamps using the BSP's `QS::onGetTime()` units (currently `millis()`), allowing for tick scheduling and AO queue latency. A five-second timer means five seconds of **QP ticks**, not a guarantee that the state transition is processed at precisely 5000 ms.

## Architecture: clocks in collaborations

**Proposed Collab extension; not implemented grammar.** A collaboration can depend on an explicit cadence (Fly N Shoot's 30 Hz game clock, periodic reporting, or a coordinated sleep deadline). The specification should capture the clock identity, cadence, emitted event, participants, and coordination semantics. The owning AO and its `QTimeEvt` remain implementation decisions in QM.

A private Radio transmission timeout or Bucket debounce interval need not become a separate collaboration participant unless its timing is part of an externally meaningful contract. Avoid treating every internal timer as a broadcast clock.

Open design question: should a collaboration clock deliver to multiple participants directly, or should one coordinating AO receive the tick and orchestrate them? Decide this in the Collab design before adding grammar.

## Current project checkpoints

- `model/model.qm` is authoritative for declarations, constructor initialisers, HSM actions, and embedded `.cpp` templates.
- `model/generated/` is generated output; never edit it as the source of truth.
- Keep deep sleep disabled during initial QSPY bring-up.
- A clean compile is not evidence that a timer was armed or its timeout handled.
