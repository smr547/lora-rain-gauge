# QM/QP-C++ Embedded Application Cheat Sheet

> **Purpose:** A practical build recipe for a small embedded application
> modelled in Quantum Leaps QM and implemented with QP/C++.
>
> This is a working engineering note, not a substitute for the QP
> documentation. It records the application-construction pattern so that
> the many small pieces needed to turn a collaboration model into a
> working embedded system are not rediscovered for every project.

## 0. Start with the collaboration diagram

The **collaboration diagram is the starting point for the application**.

Before opening QM to construct individual HSMs, define the system-level
collaboration: the Active Objects, external interrupt/service
participants, and the signals/events exchanged between them.

For the rain gauge, the current collaboration diagram defines:

``` text
BucketReedSwitchISR
        |
        | BUCKET_SWITCH_CLOSING
        v
BucketSensorAO <--------------------> ControlAO <----------------> RadioAO
                 BUCKET_TIPPED         |          SEND_REPORT
                 BUCKET_SENSOR_BUSY    |          RADIO_BUSY
                 BUCKET_SENSOR_IDLE    |          RADIO_IDLE
                 RAIN_BUCKET_FAULT     |
                                       |
                 BUCKET_SWITCH_CLOSING |
                 <---------------------+
```

The source collaboration model currently identifies:

-   `BucketReedSwitchISR`
-   `BucketSensorAO`
-   `ControlAO`
-   `RadioAO`

and these inter-object signals:

``` text
BucketReedSwitchISR -> BucketSensorAO
    BUCKET_SWITCH_CLOSING

BucketSensorAO -> ControlAO
    BUCKET_TIPPED
    BUCKET_SENSOR_BUSY
    BUCKET_SENSOR_IDLE
    RAIN_BUCKET_FAULT

ControlAO -> BucketSensorAO
    BUCKET_SWITCH_CLOSING

ControlAO -> RadioAO
    SEND_REPORT

RadioAO -> ControlAO
    RADIO_BUSY
    RADIO_IDLE
```

The collaboration diagram deliberately does **not** need to show signals
that are purely local implementation details of an individual HSM.

### What to extract from the collaboration diagram

Before constructing the QM model, turn the collaboration into a
checklist:

``` text
□ Active Objects identified
□ ISRs / external event sources identified
□ Signals crossing AO boundaries identified
□ Direction/source/destination of each signal identified
□ Published versus directly-posted signals decided
□ Signals local to an HSM left to that HSM's design
□ Hardware-facing interactions identified for the BSP
```

The collaboration model therefore acts as the bridge between **system
architecture** and the individual **HSM designs**.

Do not start by inventing classes and source files. Start by asking:

> Who collaborates with whom, and what information crosses each
> boundary?

------------------------------------------------------------------------



## Known-good implementation baseline

For the rain-gauge application, use `smr547/qp-lab/blinky-button` as the
known-good implementation baseline for the ESP32/QP/C++ toolchain.

The roles of the two principal references are different:

``` text
Dining Philosophers
    -> reference for QP patterns and framework idioms

qp-lab/blinky-button
    -> known-good ESP32/QP/C++/QM/PlatformIO implementation pattern

lora-rain-gauge
    -> application-specific architecture and behaviour
```

The baseline currently records:

``` text
PlatformIO platform: espressif32@^6.6.0
Framework:           Arduino-ESP32
QP port:             vChavezB/qpcpp_esp32 / QPESP32 0.2.1
QP/C++ basis:        7.2.2
QM:                  5.2.5
Tracing:             Q_SPY enabled
QP core affinity:    QP_CPU_NUM=1
```

Do not casually change these versions or build assumptions during initial
bring-up. First reproduce the known-good arrangement, then make deviations
explicit and test them independently.

### Lessons captured in `platformio.ini`

The `blinky-button/platformio.ini` file is part of the engineering baseline,
not disposable boilerplate. In particular it demonstrates:

``` ini
platform = espressif32@^6.6.0
framework = arduino
```

This means that the application is built with PlatformIO while still using the
Arduino-ESP32 framework underneath.

QP integration settings include:

``` ini
-D QP_CPU_NUM=1
-D CONFIG_QP_IDLE_YIELD
-D Q_SPY
-D CORE_DEBUG_LEVEL=0
-Isrc/generated
-Isrc
```

and the source filter separates handwritten and QM-generated code:

``` ini
build_src_filter =
    +<src/*.cpp>
    +<src/generated/*.cpp>
```

The baseline also contains both a generic ESP32 environment and a LilyGO
environment, demonstrating that the same QP application infrastructure has
already been exercised on the LilyGO family.

Machine-specific upload/monitor device names and debugger settings should be
reviewed rather than copied blindly.


## 1. Map the collaboration into the QM application

For the rain-gauge application, the QM model will initially contain the
whole application:

``` text
QM model
│
├── Signals
│
├── Events
│
├── Control
│   └── QActive
│       ├── attributes
│       ├── time events
│       └── state machine
│
├── TippingBucket / BucketSensor
│   └── QActive
│       ├── attributes
│       ├── time events
│       └── state machine
│
├── Radio
│   └── QActive
│       ├── attributes
│       ├── time events
│       └── state machine
│
└── BSP
```

The exact generated file arrangement is a project decision, but expect
responsibilities corresponding roughly to:

``` text
Control.hpp / Control.cpp
TippingBucket.hpp / TippingBucket.cpp
Radio.hpp / Radio.cpp
BSP.hpp / BSP.cpp
main.cpp
```

### Naming consistency

Choose one name for each architectural participant and use it
consistently through:

``` text
collaboration model
        ↓
QM package/class
        ↓
AO instance
        ↓
C++ source
        ↓
QSPY dictionaries/traces
```

If the collaboration says `BucketSensorAO` but the implementation is
called `TippingBucketAO`, explicitly record that mapping rather than
allowing the names to drift accidentally.

------------------------------------------------------------------------

## 2. Define the application signals

Create the application signal enumeration from the collaboration diagram
first.

Conceptually:

``` cpp
enum AppSignals {
    TIMEOUT_SIG = QP::Q_USER_SIG,   // local ControlAO signal

    BUCKET_SWITCH_CLOSING,
    BUCKET_TIPPED,
    BUCKET_SENSOR_BUSY,
    BUCKET_SENSOR_IDLE,
    RAIN_BUCKET_FAULT,

    SEND_REPORT,

    RADIO_BUSY,
    RADIO_IDLE,

    MAX_PUB_SIG
};
```

The precise ordering and use of `MAX_PUB_SIG` depends on the chosen
publish/subscribe design.

### Signal checklist

``` text
□ Add every inter-AO signal from the collaboration model
□ Add HSM-local signals required by each AO
□ Identify time-event signals
□ Decide which signals are published
□ Decide which signals are directly posted
□ Keep semantic names independent of physical GPIO details
```

A useful rule is:

> Signals describe things that happened or information being
> communicated; they should not expose another AO's internal
> state-machine implementation.

For example, `BUCKET_SENSOR_BUSY` is an interface statement. It does not
require `ControlAO` to know which internal `BucketSensorAO` state caused
it.

------------------------------------------------------------------------

## 3. Active Object recipe

For **each Active Object**:

``` text
□ Define class derived from QP::QActive
□ Define private attributes
□ Define QTimeEvt members
□ Define the HSM
□ Define the constructor
□ Construct time events in the constructor
□ Define one statically allocated AO instance
□ Export an opaque QActive pointer where required
□ Allocate event queue storage
□ Assign a unique AO priority at start()
□ Start the AO from application startup
□ Add QSPY object/signal dictionaries
```

### Instance / opaque-pointer pattern

The QP examples commonly separate:

``` text
Control             class/type
l_control           actual statically allocated object
AO_Control          externally visible QActive interface
```

Conceptually:

``` cpp
namespace Control {

class Control : public QP::QActive {
    // ...
};

static Control l_control;

QP::QActive * const AO_Control = &l_control;

} // namespace Control
```

Follow the exact idiom required by the QP/C++ version being used.

The point is that other application components need not know the
concrete implementation of `Control`; they can interact through the QP
Active Object interface.

### AO priorities and startup assignment

The HSM describes behaviour; the QP priority belongs to the **running AO
instance** and is supplied as the first argument of `QActive::start()`.
Higher numeric QP priorities take precedence over lower ones. Each registered
AO needs its own unique QP priority; priorities are not assigned to states
or individual events.

The known-good `qp-lab/blinky-button/src/main.cpp` starts Blinky at priority
1 and Button at priority 2:

``` cpp
AO_Blinky->start(1U, blinkyQueueSto, Q_DIM(blinkyQueueSto),
                 nullptr, stack_size);
AO_Button->start(2U, buttonQueueSto, Q_DIM(buttonQueueSto),
                 nullptr, stack_size);
```

Keep application priority constants together rather than scattering literals:

``` cpp
enum : std::uint8_t {
    CONTROL_PRIO = 1U,
    RADIO_PRIO = 2U,
    BUCKET_SENSOR_PRIO = 3U
};
```

These rain-gauge values are **proposed**, not yet measured or fixed. The
BucketSensorAO is the candidate highest-priority application AO because it
recognizes time-sensitive physical events. Confirm the ordering during HIL
testing, including radio activity and bursty switch events.

Do not confuse QP AO priorities with ESP32 GPIO interrupt priorities or the
FreeRTOS priorities of independently created tick/QSPY tasks. The ISR posts an
event; the AO subsequently dispatches it. High priority does not compensate
for insufficient queue capacity or a sleep-entry race.

------------------------------------------------------------------------

## 4. Private AO state and bitmaps

Keep state owned by an AO inside that AO.

For example, `ControlAO` tracks whether collaborating AOs are busy:

``` cpp
private:
    std::uint8_t m_busyMask {0U};
```

Possible masks:

``` cpp
static constexpr std::uint8_t TIPPING_BUCKET_BUSY = (1U << 0);
static constexpr std::uint8_t RADIO_BUSY          = (1U << 1);
```

Useful bitmap primitives:

``` cpp
m_busyMask |= TIPPING_BUCKET_BUSY;     // set bit
m_busyMask &= ~TIPPING_BUCKET_BUSY;    // clear bit

if ((m_busyMask & RADIO_BUSY) != 0U) {
    // RadioAO is busy
}

if (m_busyMask == 0U) {
    // all participating AOs are idle
}
```

For the rain gauge, `ControlAO` may permit deep sleep only when the
relevant busy bits are all clear.

------------------------------------------------------------------------

## 5. Event types, storage, queues and lifetime

### Static events: the default for payload-free notifications

An immutable `QEvt` can be created once and posted repeatedly:

``` cpp
static QP::QEvt const bucketClosingEvt {
    BUCKET_SWITCH_CLOSING, 0U, 0U
};
```

Our known-good `qp-lab/blinky-button/src/bsp.cpp` posts such a static event
from its GPIO ISR using the ESP32 port's `POST_FROM_ISR` API. The ISR
allocates no event object. Multiple queued occurrences can point to the same
immutable event; **each occurrence still consumes a queue slot**.

Do not mutate a static event's payload after posting it: queued pointers
would then observe overwritten data if another occurrence arrived.

### Typed events with payloads

For a payload, define a C++ type derived from `QP::QEvt`:

``` cpp
struct RainReportEvt : public QP::QEvt {
    std::uint32_t tipCount;
    std::uint32_t uptimeMs;
};

struct FaultEvt : public QP::QEvt {
    std::uint16_t faultCode;
};
```

An event type defines layout, while the signal identifies its meaning.
Several signals may share one payload type when appropriate. A payload
does **not** intrinsically require dynamic allocation: a suitably immutable,
long-lived typed event can also be static. The issue is whether each
outstanding occurrence needs its own independent payload snapshot.

### QP fixed-block event pools

QP's `Q_NEW` allocates a dynamic event from an **application-registered,
fixed-block event pool**, not a fresh general-purpose heap allocation per
event. The pool's backing storage can be static.

Our known-good `qp-lab/blinky-button/src/main.cpp` already contains:

``` cpp
static QF_MPOOL_EL(QEvt) smlPoolSto[10];

// during setup(), after QF::init() and before event allocation:
QP::QF::poolInit(smlPoolSto, sizeof(smlPoolSto),
                 sizeof(smlPoolSto[0]));
```

An illustrative payload allocation (requires a registered pool with blocks
large enough for `RainReportEvt`):

``` cpp
auto *e = Q_NEW(RainReportEvt, SEND_REPORT);
e->tipCount = currentTipCount;
e->uptimeMs = currentUptime;
AO_Radio->POST(e, nullptr);
```

The framework manages recycling of pooled events after dispatch; when an
event is shared with multiple recipients it tracks outstanding references.
Treat the payload as immutable once posted or published. Do not manually
`delete` a QP pooled event.

**Pools are grouped by block size, not by event subclass.** Five event
types do not imply five pools. A pool can serve any event type that fits
its block size. Register multiple pools in ascending block-size order;
QP selects a suitably sized pool. Use `QF_MPOOL_EL(EventType)` for
appropriately aligned backing storage, and check actual `sizeof` values
on the target compiler rather than relying on illustrative byte counts.

``` cpp
// Illustrative only: choose sizes and capacities after reviewing event types.
static QF_MPOOL_EL(RainReportEvt) smallPoolSto[16];
static QF_MPOOL_EL(DiagnosticEvt) largePoolSto[4];

QP::QF::poolInit(smallPoolSto, sizeof(smallPoolSto),
                 sizeof(smallPoolSto[0]));
QP::QF::poolInit(largePoolSto, sizeof(largePoolSto),
                 sizeof(largePoolSto[0]));
```

Pool capacity limits the number of **simultaneously outstanding event
objects**, not the lifetime number of events generated. Exhaustion is
still possible and must be handled according to the selected QP allocation
API and application fault policy. Size pools for worst-case outstanding
events, including queueing and fan-out, with explicit margin.

### AO queue storage is not event-pool storage

``` cpp
static QP::QEvt const *bucketQueueSto[20]; // event pointers in AO queue
static QF_MPOOL_EL(RainReportEvt) reportPoolSto[8]; // event objects
```

A static event consumes queue entries but no pool blocks. A pooled event
consumes a pool block while outstanding and a queue entry while queued.
Review both capacities under HIL burst testing.

### Rain-gauge allocation policy

- Statically allocate AO instances, AO queue storage, timers and event-pool
  backing storage.
- Prefer immutable static `QEvt` objects for `BUCKET_SWITCH_CLOSING`,
  BUSY/IDLE and other payload-free notifications.
- Use a typed event when a receiver needs a payload. Choose static storage
  only if its lifetime and immutability are safe; otherwise use a bounded
  QP pool for independent snapshots.
- Avoid general-purpose heap allocation in application event-handling and
  ISR paths. Use only the port-supported ISR-safe posting mechanism.
- Decide whether `BUCKET_TIPPED` and `SEND_REPORT` need immutable count/
  report snapshots or can remain payload-free notifications; do not assume
  shared mutable AO state is safe.
- Before ESP32 deep sleep, commit accepted tips to retained state and
  resolve in-flight work. Neither static allocation nor a QP pool makes
  queued events survive a deep-sleep reset.

### Event checklist

``` text
□ Is the event payload-free, or does it require a typed payload?
□ Is a static immutable event safe for repeated occurrences?
□ If pooled, is the block large enough and the pool registered at startup?
□ Are pools registered in ascending block-size order?
□ Are queue depth and outstanding pool-block count separately bounded?
□ Is ownership clear after POST/PUBLISH, including multiple subscribers?
□ Is ISR posting compatible with the ESP32 QP port?
□ Can an in-flight event be lost at deep sleep, and is required state retained?
□ Are pool/queue exhaustion and burst behaviour covered by HIL tests?
```

------------------------------------------------------------------------

## 6. Time-event recipe

A `QTimeEvt` normally belongs to the AO that receives its expiry signal.

For example, `ControlAO` can own a recurring timer that periodically
asks whether the processor may sleep:

``` cpp
QP::QTimeEvt m_sleepTimer;
```

Construct it with:

``` text
owner  = ControlAO
signal = TIMEOUT_SIG
```

Then arm it for the required interval and periodicity.

For the current design:

``` text
every 10 seconds
       ↓
TIMEOUT_SIG
       ↓
ControlAO RUNNING
       ↓
m_busyMask == 0 ?
     /       \
   yes        no
    |          |
SLEEPING    remain RUNNING
```

### QM guarded-transition reminder

In QM 5.2.5, conditional transition logic is represented using
transition/choice segments.

A useful pattern is:

1.  create an internal transition for `TIMEOUT_SIG`;
2.  leave its square end unattached;
3.  attach a **Choice Segment** to that endpoint;
4.  put the guard on the choice segment;
5.  route the guarded segment to the target state.

For example:

``` cpp
m_busyMask == 0U
```

If the guarded path is not enabled, the AO remains in `RUNNING` without
an unnecessary exit/re-entry transition.

### Timer checklist

``` text
□ QTimeEvt declared as AO member
□ Constructed with correct AO owner
□ Correct signal assigned
□ Tick rate understood
□ One-shot versus periodic chosen
□ Arm point defined
□ Disarm/rearm behaviour defined
□ QSPY trace expected/checked
```

------------------------------------------------------------------------

## 7. Board Support Package boundary

Keep hardware-specific details behind the BSP.

``` text
BSP.hpp
    declarations used by application/HSM code

BSP.cpp
    ESP32 / LilyGO / GPIO / LoRa / deep-sleep implementation
```

The application should ideally say things such as:

``` cpp
BSP::bucketIsClosed();
BSP::enterDeepSleep();
```

rather than containing direct ESP32 register/GPIO/sleep calls throughout
the HSMs.

Conceptually:

``` text
        QP application / HSMs
                 |
                 v
             BSP API
                 |
                 v
      ESP32 / LilyGO / LoRa
```

### BSP checklist

``` text
□ GPIO setup
□ interrupt setup
□ LoRa/radio hardware setup
□ deep-sleep/wakeup configuration
□ clocks/ticks required by QP
□ QSPY transport
□ diagnostic LEDs/serial support if required
□ application-facing hardware queries/actions
```

------------------------------------------------------------------------

## 8. ISR recipe

The ISR is an architectural participant when it introduces events into
the Active Object system.

For the rain gauge:

``` text
Bucket reed switch
        ↓
BucketReedSwitchISR
        ↓
BUCKET_SWITCH_CLOSING
        ↓
BucketSensorAO
        ↓
physical-event recognition / debounce HSM
```

The key rule is:

> **The ISR detects hardware; the Active Object interprets behaviour.**

Do not put the tipping-bucket state machine into the ISR.

### ISR checklist

``` text
□ ISR source identified in collaboration diagram
□ ISR kept short
□ Correct QP ISR-safe event-posting API used
□ ISR/QP port requirements observed
□ No unnecessary sensor-domain logic in ISR
□ QSPY instrumentation added where appropriate
```

The exact posting idiom must match the particular QP/C++ and ESP32 port
versions used by the project.

------------------------------------------------------------------------

## 9. HSM construction

Each AO's HSM elaborates behaviour that is intentionally *not* all
present in the collaboration diagram.

The collaboration gives:

``` text
who talks to whom
and
which externally visible signals cross the boundary
```

The HSM adds:

``` text
states
local signals
guards
timers
entry/exit actions
internal transitions
fault handling
```

For `BucketSensorAO`, remember that the goal is not merely generic
switch debounce. It is recognition of a credible physical tipping-bucket
cycle.

The processor may wake partway through the physical event, so HSM
initialization must account for the wake reason and current reed-switch
state.

------------------------------------------------------------------------

## 10. Application startup recipe

The startup sequence is easy to underestimate because the QP examples
compress a lot of framework setup into a small amount of code.

For this project, follow the proven `qp-lab/blinky-button/src/main.cpp`
PlatformIO/Arduino pattern. The source file is still named `main.cpp`, but the
Arduino framework provides the process entry point and the application defines
`setup()` and `loop()`.

An important port-specific lesson from the baseline is that, with the
`vChavezB/qpcpp_esp32` port currently in use, `QF::run()` returns after it
creates the AO FreeRTOS tasks and performs their initial transitions. Therefore
`loop()` must continue to yield to the FreeRTOS scheduler; do not assume that
`QF::run()` never returns.

Use an explicit checklist:

``` text
setup()
 |
 ├── BSP initialization
 ├── QF initialization
 ├── application/static event initialization
 ├── queue storage allocation
 ├── start ControlAO
 ├── start BucketSensorAO
 ├── start RadioAO
 ├── establish subscriptions
 ├── establish QSPY dictionaries
 ├── enable/establish hardware event sources
 ├── create/start QP tick task
 └── QF::run()

loop()
 |
 └── yield to FreeRTOS scheduler
```

### For each AO start

Record:

``` text
□ AO pointer
□ priority
□ queue storage
□ queue length
□ initial event if any
□ stack parameters if applicable to the port
```

Do not rely on remembering these arguments from one project to the next.

------------------------------------------------------------------------

## 11. QSPY instrumentation

Treat QSPY as part of the application design rather than as an
afterthought.

``` text
□ QS object dictionary for each AO
□ QS signal dictionaries
□ time-event visibility
□ ISR-generated event visibility
□ useful user records
□ meaningful object names
```

A real tipping event should eventually tell a coherent story:

``` text
deep sleep
    ↓
bucket wake / GPIO activity
    ↓
BUCKET_SWITCH_CLOSING
    ↓
BucketSensorAO recognizes physical cycle
    ↓
BUCKET_TIPPED
    ↓
ControlAO updates count/state
    ↓
SEND_REPORT
    ↓
RadioAO BUSY
    ↓
transmit
    ↓
RadioAO IDLE
    ↓
BucketSensorAO IDLE
    ↓
TIMEOUT_SIG
    ↓
ControlAO confirms m_busyMask == 0
    ↓
deep sleep
```

A good QSPY trace is an executable explanation of the collaboration and
HSM behaviour.

------------------------------------------------------------------------

## 12. Deep-sleep lifecycle

Deep sleep is part of the architecture, not merely a BSP optimization.

The application repeatedly loses ordinary processor state and
reconstructs its logical state after wake.

Distinguish explicitly:

``` text
ordinary RAM        lost across deep sleep/reset as applicable
RTC-retained state  survives ESP32 deep sleep
NVS / flash         survives reset and power loss
base-station state  external to the node
```

For every item of state, ask:

``` text
□ Does it need to survive deep sleep?
□ Does it need to survive reset?
□ Does it need to survive complete power loss?
□ Can it be reconstructed from another source?
```

### Bucket wake

Most real bucket tips are expected to occur while the processor is
asleep.

The processor therefore may wake **in the middle of a physical
bucket-tip cycle**.

Initialization must not assume that the reed switch is open or that the
AO observed the original closing edge while running.

Conceptually:

``` text
deep sleep
    ↓
reed switch closes
    ↓
wake source asserted
    ↓
processor wakes
    ↓
QP application/HSM initialized
    ↓
current switch state + wake reason examined
    ↓
BucketSensorAO continues recognition of the physical event
```

The measured Davis tipping bucket holds the reed contact closed long
enough that this can be tested with substantial timing margin, but the
actual wake-to-application latency should be measured.

------------------------------------------------------------------------

## 13. Sleep coordination

`ControlAO` owns the policy for putting the processor to sleep.

Collaborating AOs report whether they are busy:

``` text
BucketSensorAO ---- BUCKET_SENSOR_BUSY/IDLE ----\
                                                  > ControlAO busy bitmap
RadioAO ------------ RADIO_BUSY/IDLE ------------/
```

`ControlAO` periodically receives `TIMEOUT_SIG`.

Only when:

``` cpp
m_busyMask == 0U
```

may it proceed toward `SLEEPING`.

This avoids `ControlAO` reaching inside other Active Objects to inspect
their internal states.

### Sleep-race review

Before production use, explicitly review the interval between:

``` text
ControlAO decides all AOs are idle
                ↓
processor actually enters deep sleep
```

A new hardware event or AO activity must not be lost in that window.

Do not hide this issue inside BSP code; make the chosen synchronization
behaviour explicit in the model/design.

------------------------------------------------------------------------

## 14. Radio AO

`RadioAO` should own radio-operation sequencing rather than exposing
radio implementation details to `ControlAO`.

The current collaboration provides:

``` text
ControlAO -> RadioAO
    SEND_REPORT

RadioAO -> ControlAO
    RADIO_BUSY
    RADIO_IDLE
```

This gives `ControlAO` enough information to coordinate sleep without
knowing RadioLib/SX1276 details.

As protocol implementation develops, keep the boundary clear:

``` text
sensor/HSM state
      ↓
application report request
      ↓
RadioAO
      ↓
protocol encoder / radio driver
      ↓
LoRa hardware
```

------------------------------------------------------------------------

## 15. Source-generation and repository discipline

The initial strategy is to keep the application sources together in the
QM model while the architecture is small and being learned.

Recommended repository location:

``` text
rain-gauge-node/
├── model/
│   ├── README.md
│   └── <application>.qm
├── src/
│   ├── main.cpp
│   ├── bsp.cpp
│   └── generated/
├── include/
└── test/

docs/
└── development/
    └── QM-QPC-CHEATSHEET.md
```

Keep handwritten platform/application glue in `src/*.cpp` and QM-generated
sources in `src/generated/`, following the proven `blinky-button` pattern.

The exact generated-source layout can be decided after the QM generation
pattern has settled.

### QM invocation

The project should provide a small wrapper under `tools/` rather than
requiring developers to remember a machine-specific command such as:

``` text
~/qm525/bin/qm.sh
```

For example:

``` text
./tools/qm rain-gauge-node/model/BucketAO.qm
```

with the wrapper defaulting to QM 5.2.5 and permitting the installation
path to be overridden by an environment variable.

The repository should record the expected QM version but should not
contain QM itself.

------------------------------------------------------------------------

## 16. First-build checklist

When starting a new embedded QP application from a collaboration
diagram:

``` text
ARCHITECTURE
□ Draw/update collaboration diagram
□ Identify AOs
□ Identify ISRs/external participants
□ Identify inter-AO signals and directions
□ Decide post versus publish relationships

QM MODEL
□ Create packages/classes for AOs
□ Add signal enumeration
□ Add event types/instances
□ Add AO private members
□ Add timers
□ Construct each HSM
□ Add guards/actions
□ Add opaque AO interfaces/instances as required

PLATFORM
□ Define BSP.hpp
□ Implement BSP.cpp
□ Configure GPIO
□ Configure ISRs
□ Configure QP tick/time events
□ Configure radio
□ Configure deep sleep/wake sources

APPLICATION
□ Allocate AO queues
□ Assign priorities
□ Start AOs
□ Establish subscriptions
□ Add static/dynamic event handling
□ Add protocol/report integration

OBSERVABILITY
□ Add QS dictionaries
□ Verify QSPY transport
□ Trace timer expiry
□ Trace ISR-to-AO event flow
□ Trace BUSY/IDLE coordination
□ Trace real bucket tip
□ Trace radio transaction
□ Trace sleep/wake cycle

ROBUSTNESS
□ Test bounce
□ Test duplicate hardware activity
□ Test wake while contact already closed
□ Test radio busy during sleep timeout
□ Test bucket activity during radio activity
□ Test sleep-entry race
□ Test reset/deep-sleep retained state
□ Test QSPY trace against expected collaboration
```

------------------------------------------------------------------------

## 17. The mental model

The process can be remembered as a progression:

``` text
Requirements
     ↓
Collaboration
     ↓
AOs + ISRs + inter-object signals
     ↓
Individual HSMs
     ↓
Events + timers + AO instances
     ↓
BSP + ISRs + hardware
     ↓
Application startup / QF integration
     ↓
QSPY observation
     ↓
Real hardware tests
```

QP greatly improves the structure of an embedded application, but it
does not make the surrounding embedded-system engineering disappear.

That is precisely why this recipe exists.

**The collaboration diagram tells us the architecture.\
The HSMs tell us the behaviour.\
The BSP connects that model to the hardware.\
QSPY lets us see whether the running system tells the same story.**
