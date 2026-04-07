import sys

TS_PACKET_SIZE = 188
SYNC_BYTE = 0x47

def clean_ts(input_file, output_file):
    # Open the input TS file in binary mode and the output file for writing
    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()  # read the entire file into memory
        i = 0
        total_packets = 0

        # Iterate through the file byte by byte
        while i < len(data):
            # Check if the current byte is the TS sync byte
            if data[i] == SYNC_BYTE:
                # Check if a full 188-byte packet can fit from this position
                if i + TS_PACKET_SIZE <= len(data):
                    # Write the 188-byte packet to the output file
                    f_out.write(data[i:i+TS_PACKET_SIZE])
                    total_packets += 1
                    # Move index forward by one full packet
                    i += TS_PACKET_SIZE
                else:
                    # Not enough bytes left for a full packet, stop processing
                    break
            else:
                # Current byte is not a sync byte, move to the next byte
                i += 1

    # Print summary of extracted packets
    print(f"Done. {total_packets} full TS packets extracted to '{output_file}'.")


if __name__ == "__main__":
    # Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python clean_ts.py input.ts output.ts")
        sys.exit(1)

    # Run the clean_ts function with input and output file paths
    clean_ts(sys.argv[1], sys.argv[2])

    # ---------
    # HOW TO RUN
    # ---------
    # On linux
    # python3 ts_clean_up.py original.ts clean.ts
    #
    # On Windows
    # python ts_clean_up.py original.ts clean.ts    


