#pragma once

// GENERATED from rain-gauge.collab; do not edit by hand.
// Regenerate with collabc.py.

#include "qpcpp.hpp"

enum AppSignals {
    CONSIDER_SLEEPING_SIG = QP::Q_USER_SIG,  // SleepTimer -> Control
    RADIO_TX_TIMEOUT_SIG,  // RadioTxTimer -> Radio
    // routes:
    //   BucketReedSwitch -> TippingBucket
    //   Control -> TippingBucket
    BUCKET_SWITCH_CLOSING_SIG,
    BUCKET_TIPPED_SIG,  // TippingBucket -> Control
    BUCKET_BUSY_SIG,  // TippingBucket -> Control
    BUCKET_IDLE_SIG,  // TippingBucket -> Control
    BUCKET_FAULT_SIG,  // TippingBucket -> Control
    SEND_HEALTH_REPORT_SIG,  // Control -> Radio
    SEND_RAIN_REPORT_SIG,  // Control -> Radio
    RADIO_BUSY_SIG,  // Radio -> Control
    RADIO_IDLE_SIG,  // Radio -> Control
    RADIO_TX_DONE_SIG,  // RadioDIO0 -> Radio

    MAX_APP_SIG
};
