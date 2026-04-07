#!/usr/bin/env python3
"""
MPEG-2 TS Sync Byte Validator
Checks if 0x47 sync bytes appear at correct positions (every 188 bytes).
"""

import sys
import os
import argparse

TS_PACKET_SIZE = 188
SYNC_BYTE = 0x47


def format_time(packet_index: int, bitrate_mbps: float) -> str:
    packets_per_second = (bitrate_mbps * 1_000_000) / (TS_PACKET_SIZE * 8)
    seconds = packet_index / packets_per_second
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def validate(filepath: str, bitrate_mbps: float, show_ok: bool):
    file_size = os.path.getsize(filepath)
    total_packets = file_size // TS_PACKET_SIZE
    leftover = file_size % TS_PACKET_SIZE

    print(f"\n  {'='*54}")
    print(f"  TS Sync Byte Validator")
    print(f"  {'='*54}")
    print(f"  File          : {filepath}")
    print(f"  Size          : {file_size:,} bytes")
    print(f"  Total packets : {total_packets:,}  (@ {TS_PACKET_SIZE} bytes each)")
    if leftover:
        print(f"  ⚠  Leftover   : {leftover} bytes at end of file (incomplete packet)")
    print(f"  {'='*54}\n")

    # --- Check 1: first byte of file must be 0x47
    with open(filepath, "rb") as f:
        first_byte = f.read(1)

    if not first_byte:
        print("  Error: file is empty.")
        sys.exit(1)

    if first_byte[0] == SYNC_BYTE:
        print(f"  ✅  First byte is 0x47 — stream starts correctly\n")
    else:
        print(f"  ❌  First byte is 0x{first_byte[0]:02X} — expected 0x47!")
        print(f"      Stream does NOT start with a valid sync byte.\n")

    # --- Check 2: every packet must start with 0x47
    errors: list[tuple[int, int, int]] = []  # (packet_index, file_offset, actual_byte)
    ok_count = 0

    with open(filepath, "rb") as f:
        packet_index = 0
        while True:
            raw = f.read(TS_PACKET_SIZE)
            if len(raw) < TS_PACKET_SIZE:
                break

            expected_offset = packet_index * TS_PACKET_SIZE

            if raw[0] == SYNC_BYTE:
                ok_count += 1
                if show_ok:
                    print(f"  ✅  pkt {packet_index:>10,}  offset {expected_offset:>12,}  0x47 OK")
            else:
                errors.append((packet_index, expected_offset, raw[0]))

            packet_index += 1

    # --- Report
    print(f"  Packets checked : {total_packets:,}")
    print(f"  ✅  Valid       : {ok_count:,}")
    print(f"  ❌  Invalid     : {len(errors):,}\n")

    if not errors:
        print(f"  ✅  All sync bytes are correct — TS structure is valid.\n")
        return

    print(f"  Sync byte errors found:\n")
    print(f"  {'#':<7} {'Packet index':<15} {'File offset':<15} {'Found':<8} {'Approx. time'}")
    print(f"  {'-'*7} {'-'*15} {'-'*15} {'-'*8} {'-'*14}")

    for i, (pkt_idx, offset, byte) in enumerate(errors, 1):
        t = format_time(pkt_idx, bitrate_mbps)
        print(
            f"  {i:<7} {pkt_idx:<15,} {offset:<15,} "
            f"0x{byte:02X}     {t}"
        )

    print(f"\n  {'='*54}")
    print(f"  Total sync errors: {len(errors):,} / {total_packets:,} packets")
    print(f"  {'='*54}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate MPEG-2 TS sync byte (0x47) positions"
    )
    parser.add_argument("file", help="Path to .ts file")
    parser.add_argument(
        "--bitrate", type=float, default=19.2, metavar="Mbit/s",
        help="Mux bitrate for time estimation (default: 19.2)"
    )
    parser.add_argument(
        "--show-ok", action="store_true",
        help="Also print every valid packet (verbose, slow on large files)"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    validate(args.file, args.bitrate, args.show_ok)


if __name__ == "__main__":
    main()