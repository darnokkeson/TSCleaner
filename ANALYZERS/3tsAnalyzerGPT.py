import sys

TS_PACKET_SIZE = 188
SYNC_BYTE = 0x47

def pts_to_time(pts):
    seconds = pts / 90000
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def extract_pts(packet):
    payload_unit_start = (packet[1] >> 6) & 1
    adaptation_field_control = (packet[3] >> 4) & 3

    offset = 4

    if adaptation_field_control in (2, 3):
        adaptation_length = packet[4]
        offset += 1 + adaptation_length

    if payload_unit_start and offset + 14 < len(packet):
        if packet[offset:offset+3] == b'\x00\x00\x01':
            pts_dts_flags = (packet[offset+7] >> 6) & 3
            if pts_dts_flags & 2:
                pts = (
                    ((packet[offset+9] >> 1) << 30) |
                    ((packet[offset+10] << 22) | ((packet[offset+11] >> 1) << 15)) |
                    ((packet[offset+12] << 7) | (packet[offset+13] >> 1))
                )
                return pts
    return None

def analyze_ts(filename):
    pid_cc = {}
    last_pts = None
    packet_index = 0
    missing_packets = 0

    with open(filename, "rb") as f:
        while True:
            packet = f.read(TS_PACKET_SIZE)
            if len(packet) != TS_PACKET_SIZE:
                break

            if packet[0] != SYNC_BYTE:
                packet_index += 1
                continue

            pid = ((packet[1] & 0x1F) << 8) | packet[2]
            cc = packet[3] & 0x0F

            pts = extract_pts(packet)
            if pts is not None:
                last_pts = pts

            if pid in pid_cc:
                expected = (pid_cc[pid] + 1) % 16

                if cc != expected:
                    diff = (cc - expected) % 16
                    missing_packets += diff

                    if last_pts:
                        time_str = pts_to_time(last_pts)
                    else:
                        time_str = "unknown"

                    print(
                        f"Missing {diff} packet(s) at packet {packet_index}, "
                        f"PID {pid}, time {time_str}"
                    )

            pid_cc[pid] = cc
            packet_index += 1

    print("\n===== SUMMARY =====")
    print(f"Total missing packets: {missing_packets}")
    print(f"Total packets analyzed: {packet_index}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ts_analyzer.py file.ts")
        sys.exit(1)

    analyze_ts(sys.argv[1])
