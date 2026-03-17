#!/usr/bin/env python3
"""
Simple MPEG-2 TS Packet Loss Analyzer
- Detects dropped packets via Continuity Counter (CC)
- No PID breakdown, no PCR
- Time is estimated from packet index + assumed mux bitrate
"""

import sys
import os
import argparse

TS_PACKET_SIZE = 188
SYNC_BYTE = 0x47


def cc_diff(expected: int, got: int) -> int:
    if got >= expected:
        return got - expected
    return (16 - expected) + got


def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def analyze(filepath: str, bitrate_mbps: float):
    file_size = os.path.getsize(filepath)
    total_packets = file_size // TS_PACKET_SIZE

    if total_packets == 0:
        print("Error: file too small or not a TS file.")
        sys.exit(1)

    bits_per_packet    = TS_PACKET_SIZE * 8
    packets_per_second = (bitrate_mbps * 1_000_000) / bits_per_packet
    total_duration     = total_packets / packets_per_second

    print(f"\n  File              : {filepath}")
    print(f"  Size              : {file_size:,} bytes")
    print(f"  Packets in file   : {total_packets:,}")
    print(f"  Assumed bitrate   : {bitrate_mbps} Mbit/s")
    print(f"  Estimated duration: {format_time(total_duration)}")
    print(f"  (use --bitrate to override, e.g. --bitrate 38.4)\n")

    last_cc: dict[int, int] = {}
    drops: list[tuple[int, int]] = []  # (packet_index, dropped_count)
    total_dropped = 0
    packet_index = 0

    with open(filepath, "rb") as f:
        while True:
            raw = f.read(TS_PACKET_SIZE)
            if len(raw) < TS_PACKET_SIZE:
                break

            if raw[0] != SYNC_BYTE:
                packet_index += 1
                continue

            header      = int.from_bytes(raw[0:4], "big")
            pid         = (header >> 8) & 0x1FFF
            has_payload = (header >> 4) & 0x01
            cc          = header & 0x0F
            tei         = (header >> 23) & 0x01
            has_adapt   = (header >> 5) & 0x01

            # Skip null packets, error packets, packets without payload
            if pid == 0x1FFF or tei or not has_payload:
                packet_index += 1
                continue

            # Check discontinuity indicator — legal CC jump, not a drop
            disc_flag = False
            if has_adapt and len(raw) > 5 and raw[4] > 0:
                disc_flag = bool((raw[5] >> 7) & 0x01)

            if pid in last_cc and not disc_flag:
                expected = (last_cc[pid] + 1) % 16
                if cc != expected:
                    dropped = cc_diff(expected, cc)
                    if 0 < dropped < 16:
                        drops.append((packet_index, dropped))
                        total_dropped += dropped

            last_cc[pid] = cc
            packet_index += 1

    # ── Report ──────────────────────────────────────────────
    if not drops:
        print("  ✅  No packet loss detected!\n")
        return

    print(f"  ⛔  Drop events           : {len(drops)}")
    print(f"  ⛔  Total dropped packets : {total_dropped:,}\n")

    col_n    = 6
    col_time = 16
    col_pkt  = 14
    col_drop = 7

    header_line = (
        f"  {'#':<{col_n}} {'Approx. time':<{col_time}} "
        f"{'Packet index':<{col_pkt}} {'Dropped':<{col_drop}}"
    )
    sep_line = (
        f"  {'-'*col_n} {'-'*col_time} "
        f"{'-'*col_pkt} {'-'*col_drop}"
    )
    print(header_line)
    print(sep_line)

    for i, (pkt_idx, count) in enumerate(drops, 1):
        t = pkt_idx / packets_per_second
        print(
            f"  {i:<{col_n}} {format_time(t):<{col_time}} "
            f"{pkt_idx:<{col_pkt},} {count:<{col_drop}}"
        )

    print(f"\n  {'='*52}")
    print(f"  Total dropped: {total_dropped:,} packets in {len(drops)} event(s)")
    print(f"  {'='*52}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Simple MPEG-2 TS packet loss analyzer"
    )
    parser.add_argument("file", help="Path to .ts file")
    parser.add_argument(
        "--bitrate", type=float, default=19.2,
        metavar="Mbit/s",
        help="Assumed mux bitrate in Mbit/s (default: 19.2)"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    analyze(args.file, args.bitrate)


if __name__ == "__main__":
    main()
