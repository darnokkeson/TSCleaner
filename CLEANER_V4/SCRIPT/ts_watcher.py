import os
import sys
import time
import subprocess

# -------------------------------------------------------
# ts_watcher.py
# Scans the root folder for new .ts files, waits until
# each file is fully exported (stable size), then calls
# ts_clean_up.py. Tracks processed files in memory so
# no file is ever processed twice.
# -------------------------------------------------------

CHECK_INTERVAL = 5        # seconds between folder scans
SIZE_CHECK_INTERVAL = 5   # seconds between file size checks

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_root_dir():
    # Root is two levels up from CLEANER\SCRIPT\
    script_dir = get_script_dir()
    cleaner_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(cleaner_dir)
    return root_dir

def wait_for_stable_size(filepath):
    """Block until file size stops changing."""
    while True:
        size1 = os.path.getsize(filepath)
        time.sleep(SIZE_CHECK_INTERVAL)
        size2 = os.path.getsize(filepath)
        if size1 == size2:
            return

def sanitize_name(name):
    """Replace spaces with underscores in filename."""
    return name.replace(" ", "_")

def main():
    root_dir = get_root_dir()
    script_dir = get_script_dir()
    clean_up_script = os.path.join(script_dir, "ts_clean_up.py")
    python_exe = sys.executable

    print()
    print("  ============================================")
    print("   TS Cleaner - usuwanie zbednych metadanych")
    print("  ============================================")
    print(f"  Folder     : {root_dir}")
    print(f"  Python     : {python_exe}")
    print(f"  Skrypt     : {clean_up_script}")
    print("  ============================================")
    print("  Nacisnij Ctrl+C aby zatrzymac")
    print("  ============================================")
    print()

    if not os.path.exists(clean_up_script):
        print(f"  [BLAD] Nie znaleziono skryptu: {clean_up_script}")
        print("  Upewnij sie, ze plik ts_clean_up.py istnieje w folderze CLEANER\\SCRIPT.")
        sys.exit(1)

    # In-memory set of already processed file paths
    processed = set()
    waiting_shown = False
    total_done = 0      # cumulative counter across all rounds

    while True:
        # Scan for .ts files, skip _clean files and already processed ones
        new_files = []
        for fname in os.listdir(root_dir):
            if not fname.lower().endswith(".ts"):
                continue
            if "_clean" in fname.lower():
                continue
            full_path = os.path.join(root_dir, fname)
            if full_path in processed:
                continue
            new_files.append((fname, full_path))

        if not new_files:
            if not waiting_shown:
                print("  [OCZEKIWANIE] Brak nowych plikow .ts. Sprawdzanie co 5 sekund...")
                waiting_shown = True
            time.sleep(CHECK_INTERVAL)
            continue

        # New files found - reset waiting message flag
        waiting_shown = False

        for fname, full_path in new_files:
            name, ext = os.path.splitext(fname)
            clean_name = sanitize_name(name)
            output_fname = f"{clean_name}_clean{ext}"
            output_path = os.path.join(root_dir, output_fname)

            # Wait until file size is stable (export finished)
            wait_for_stable_size(full_path)

            # Mark as processed immediately to prevent re-queuing
            processed.add(full_path)
            total_done += 1

            print(f"  ------------------------------------------")
            print(f"  [{total_done}] Wejscie : {fname}")
            print(f"  [{total_done}] Wyjscie : {output_fname}")
            print(f"  ------------------------------------------")

            # Call ts_clean_up.py
            result = subprocess.run(
                [python_exe, clean_up_script, full_path, output_path]
            )

            if result.returncode != 0:
                print(f"  [{total_done}] [BLAD] Nie udalo sie przetworzyc: {fname}")
                total_done -= 1
            else:
                print(f"  [{total_done}] [OK] Gotowe: {output_fname}")
            print()

        print("  ============================================")
        print(f"  Lacznie przetworzono: {total_done} plikow")
        print("  ============================================")
        print()

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("  [STOP] Program zatrzymany przez uzytkownika.")
        sys.exit(0)