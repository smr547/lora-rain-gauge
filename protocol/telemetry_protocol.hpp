
#ifndef TELEMETRY_PROTOCOL_HPP
#define TELEMETRY_PROTOCOL_HPP

#include <cstddef>
#include <cstdint>

namespace Telemetry {

// Existing E1 wire-protocol identifiers
constexpr std::uint8_t MAGIC       = 0x53;
constexpr std::uint8_t VERSION     = 2U;
constexpr std::uint8_t MSG_REPORT  = 1U;

// Existing E1 packet layout.
//
// This is a wire-format structure: do not reorder fields or add
// application data without deliberately changing the protocol.
//
// The bucket counters in SendReportEvt are not yet represented here.

#pragma pack(push, 1)

struct TelemetryPacket {
    std::uint8_t  magic;
    std::uint8_t  version;
    std::uint8_t  node_id;
    std::uint8_t  msg_type;

    std::uint32_t seq;
    std::uint32_t uptime_ms;

    std::int16_t  temp_c_x100;
    std::uint16_t supply_mv;
    std::uint16_t battery_mv;

    std::uint8_t  wake_reason;

    std::uint16_t crc;
};

#pragma pack(pop)

static_assert(sizeof(TelemetryPacket) == 21U,
              "Unexpected telemetry packet layout");

static_assert(offsetof(TelemetryPacket, crc) == 19U,
              "Unexpected CRC field offset");

// CRC-16/CCITT-FALSE:
// polynomial 0x1021, initial value 0xFFFF,
// no reflection, no final XOR.
//
// The CRC covers all packet bytes preceding the crc field.

inline std::uint16_t crc16(
    std::uint8_t const *data,
    std::size_t length
) {
    std::uint16_t crc = 0xFFFFU;

    for (std::size_t i = 0U; i < length; ++i) {
        crc ^= static_cast<std::uint16_t>(data[i]) << 8U;

        for (unsigned bit = 0U; bit < 8U; ++bit) {
            crc = (crc & 0x8000U)
                ? static_cast<std::uint16_t>((crc << 1U) ^ 0x1021U)
                : static_cast<std::uint16_t>(crc << 1U);
        }
    }

    return crc;
}

inline void updateCrc(TelemetryPacket &packet) {
    packet.crc = crc16(
        reinterpret_cast<std::uint8_t const *>(&packet),
        offsetof(TelemetryPacket, crc)
    );
}

inline bool hasValidCrc(TelemetryPacket const &packet) {
    return packet.crc == crc16(
        reinterpret_cast<std::uint8_t const *>(&packet),
        offsetof(TelemetryPacket, crc)
    );
}

} // namespace Telemetry

#endif // TELEMETRY_PROTOCOL_HPP
