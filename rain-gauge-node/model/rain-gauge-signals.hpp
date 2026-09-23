#pragma once

// GENERATED from rain-gauge.collab; do not edit by hand.
// Regenerate with collabc.py.

#include "qpcpp.hpp"

enum AppSignals {
    // routes:
    //   BucketReedSwitch -> TippingBucket
    //   Control -> TippingBucket
    BUCKET_SWITCH_CLOSING_SIG = QP::Q_USER_SIG,
    BUCKET_TIPPED_SIG,  // TippingBucket -> Control
    BUCKET_SENSOR_BUSY_SIG,  // TippingBucket -> Control
    BUCKET_SENSOR_IDLE_SIG,  // TippingBucket -> Control
    RAIN_BUCKET_FAULT_SIG,  // TippingBucket -> Control
    SEND_REPORT_SIG,  // Control -> Radio
    RADIO_BUSY_SIG,  // Radio -> Control
    RADIO_IDLE_SIG,  // Radio -> Control
    RADIO_TX_DONE_SIG,  // RadioDIO0 -> Radio

    MAX_APP_SIG
};
