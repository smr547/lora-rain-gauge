#pragma once

// GENERATED from rain-gauge.collab; do not edit by hand.
// Regenerate with collabc.py.

#include "qpcpp.hpp"

enum AppSignals {
    // routes:
    //   BucketReedSwitchISR -> BucketSensorAO
    //   ControlAO -> BucketSensorAO
    BUCKET_SWITCH_CLOSING_SIG = QP::Q_USER_SIG,
    BUCKET_TIPPED_SIG,  // BucketSensorAO -> ControlAO
    BUCKET_SENSOR_BUSY_SIG,  // BucketSensorAO -> ControlAO
    BUCKET_SENSOR_IDLE_SIG,  // BucketSensorAO -> ControlAO
    RAIN_BUCKET_FAULT_SIG,  // BucketSensorAO -> ControlAO
    SEND_REPORT_SIG,  // ControlAO -> RadioAO
    RADIO_BUSY_SIG,  // RadioAO -> ControlAO
    RADIO_IDLE_SIG,  // RadioAO -> ControlAO
    RADIO_TX_DONE_SIG,  // RadioDIO0ISR -> RadioAO

    MAX_APP_SIG
};
