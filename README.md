TS Cleaner

Table of Contents

1. Overview
2. Features
3. Requirements
4. Installation
5. Usage
6. Project Structure
7. How It Works
8. Files Description
9. Configuration


Overview

TS Cleaner is an automated file processing tool designed to clean and validate MPEG Transport Stream (TS) files. The application continuously monitors a specified directory for new .ts files, waits for them to be fully written, and then processes them to remove metadata and extraneous data, outputting clean TS packets only.

The program is intended for use on Windows systems and includes an embedded Python interpreter for easy deployment without additional dependencies.


Features

- Automatic file monitoring and detection of new .ts files
- File stability detection (waits for export to complete before processing)
- Batch processing with progress tracking
- Filename sanitization (spaces replaced with underscores)
- Prevention of duplicate file processing
- Real-time console output with detailed processing information
- Safe interruption via Ctrl+C


Requirements

For Windows Batch Execution:
- Windows operating system
- Embedded Python executable (included in CLEANER/PYTHON_WIN/)

For Manual Python Execution:
- Python 3.6 or higher
- No external dependencies required


Installation

1. Ensure the directory structure is properly set up:
   
   ROOT/
   ├── DWUKLIK_ABY_CLEAN.bat
   ├── CLEANER/
   │   ├── PYTHON_WIN/
   │   │   └── python.exe
   │   └── SCRIPT/
   │       ├── ts_clean_up.py
   │       └── ts_watcher.py
   ├── film1.ts
   ├── nagranie.ts
   └── (other .ts files)

2. Place any .ts files to be processed in the same directory as the batch file.

3. Ensure PYTHON_WIN/python.exe is properly installed and executable.


Usage

Windows (Recommended):

Double-click DWUKLIK_ABY_CLEAN.bat to start the watcher. The program will:
- Display initialization information
- Print "[OCZEKIWANIE] Waiting for new .ts files"
- Process files as they appear
- Continue running until you press Ctrl+C

Command Line (Windows):

cmd> set PYTHON_EXE=path\to\python.exe
cmd> %PYTHON_EXE% CLEANER\SCRIPT\ts_watcher.py

Linux/macOS:

python3 SCRIPT/ts_watcher.py

The watcher will scan the parent directory of the SCRIPT folder for new .ts files.


Project Structure

CLEANER_V4/
├── README.md                     (this file)
├── DWUKLIK_ABY_CLEAN.bat        (Windows launcher script)
├── CLEANER/
│   ├── PYTHON_WIN/
│   │   └── python.exe            (embedded Python interpreter)
│   └── SCRIPT/
│       ├── ts_clean_up.py        (core cleaning algorithm)
│       └── ts_watcher.py         (file monitoring system)
├── film1.ts                      (example input files)
├── nagranie.ts
└── [processed outputs with _clean suffix]


How It Works

1. Watcher Initialization:
   - ts_watcher.py starts and scans the root directory
   - Displays configuration information (paths, Python version)
   - Enters continuous monitoring loop

2. File Detection:
   - Every 5 seconds, the watcher scans for files matching *.ts
   - Ignores files containing "_clean" in the filename
   - Ignores files already processed in the current session

3. Stability Checking:
   - When new files are detected, the watcher waits for file size stability
   - Checks file size every 5 seconds
   - Only proceeds when file size remains unchanged (indicates export completion)

4. Processing:
   - Passes the input file to ts_clean_up.py
   - Creates output file with "_clean" suffix in the same directory
   - Logs processing status and results

5. Output:
   - Original file: film1.ts becomes film1_clean.ts
   - Spaces in filenames are replaced with underscores
   - Original files are preserved


Files Description

DWUKLIK_ABY_CLEAN.bat

Windows batch file that serves as the main entry point.

Key Functions:
- Sets ROOT directory to the batch file location
- Defines paths to embedded Python and watcher script
- Validates that both Python executable and watcher script exist
- Launches ts_watcher.py with proper error handling
- Displays meaningful error messages in Polish if components are missing

ts_watcher.py

Main file monitoring and orchestration script.

Key Functions:
- get_root_dir(): Calculates the root directory from CLEANER\SCRIPT location
- wait_for_stable_size(): Blocks execution until target file size stabilizes
- sanitize_name(): Replaces spaces with underscores in filenames
- main(): Primary event loop that monitors, detects, and queues files for processing

Configuration:
- CHECK_INTERVAL = 5 seconds (directory scan frequency)
- SIZE_CHECK_INTERVAL = 5 seconds (file stability check frequency)

Processing Flow:
1. Scans root directory for .ts files
2. Filters out already-processed files and files containing "_clean"
3. Waits for file size stability
4. Calls ts_clean_up.py with input and output paths
5. Tracks cumulative count of successfully processed files
6. Sleeps before next scan

ts_clean_up.py

Core file processing script that removes extraneous data from TS streams.

Algorithm Overview:
- Reads input TS file in binary mode
- Scans byte-by-byte looking for TS packet synchronization byte (0x47)
- When sync byte is found, extracts 188-byte packet (standard TS packet size)
- Writes valid packets to output file
- Ignores any bytes between valid packets (metadata removal)

Key Constants:
- TS_PACKET_SIZE = 188 bytes (standard MPEG-TS packet size)
- SYNC_BYTE = 0x47 (packet synchronization marker)

Usage:
python ts_clean_up.py input.ts output.ts

Returns:
- Exit code 0 on success
- Exit code 1 on argument error


Configuration

Default Scanning Intervals:

Edit ts_watcher.py to adjust these values:

CHECK_INTERVAL = 5          # seconds between directory scans
SIZE_CHECK_INTERVAL = 5     # seconds between file size checks

File Filtering Rules:

Current filters exclude:
- Files without .ts extension
- Files containing "_clean" in filename
- Files already processed in current session

Output Naming:

Input file: filename.ts
Output file: filename_clean.ts (spaces converted to underscores)


Troubleshooting

"Nie znaleziono Pythona" (Python not found):
- Verify PYTHON_WIN\python.exe exists
- Check that the path in the batch file is correct
- Ensure the Python executable has proper permissions

"Nie znaleziono skryptu" (Script not found):
- Verify SCRIPT\ts_watcher.py and ts_clean_up.py exist
- Check directory structure matches the expected layout
- Ensure file permissions allow reading

No output or "OCZEKIWANIE" status:
- Verify .ts files are in the correct directory (same as .bat file)
- Check that the watcher has permission to read the directory
- Confirm .ts files are valid and not being continuously written

Processing fails silently:
- Check console output for [BLAD] error messages
- Verify input .ts file is valid MPEG-TS format
- Check disk space for output file creation
- Ensure write permissions in the output directory


License

This project is provided as-is for personal use.
