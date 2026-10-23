import os
import subprocess
import time
from datetime import datetime

WATCH_DIR = r"D:\scangrade-ai"
PROXY = "http://127.0.0.1:8888"
DEBOUNCE_SECONDS = 4
CHECK_INTERVAL_SECONDS = 3

def run_git(args):
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=WATCH_DIR,
            capture_output=True,
            text=True,
            timeout=45
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def has_changes():
    code, stdout, _ = run_git(["status", "--porcelain"])
    return code == 0 and bool(stdout.strip())

def sync_to_github():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Detected file changes. Staging and committing...", flush=True)
    
    # Git add
    code, out, err = run_git(["add", "-A"])
    if code != 0:
        print(f"Error during git add: {err}", flush=True)
        return

    # Check if there is still something to commit
    code, status_out, _ = run_git(["status", "--porcelain"])
    if not status_out.strip():
        return

    # Git commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"chore: auto-sync file updates [{timestamp}]"
    code, out, err = run_git(["commit", "-m", commit_msg])
    if code != 0:
        print(f"Commit note: {out or err}", flush=True)
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Committed: '{commit_msg}'. Pushing to GitHub...", flush=True)

    # Git push via proxy
    code, out, err = run_git(["-c", f"http.proxy={PROXY}", "push", "origin", "main"])
    if code == 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Successfully pushed changes to GitHub (origin/main)!", flush=True)
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Push warning: {err or out}", flush=True)

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ScanGrade AI Auto-Sync Daemon Started.", flush=True)
    print(f"Watching: {WATCH_DIR}", flush=True)
    print(f"Target: origin/main via {PROXY}", flush=True)

    last_had_changes = False

    while True:
        try:
            if has_changes():
                # Debounce to allow multiple quick saves to settle
                time.sleep(DEBOUNCE_SECONDS)
                if has_changes():
                    sync_to_github()
            time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("Auto-Sync stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected monitor error: {e}", flush=True)
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
