#!/usr/bin/env python3
"""tiny‑telealert – watch a file or run a command and push a Telegram message.

Usage examples:
  python telealert.py --watch ./log.txt
  python telealert.py --cmd "pytest -q"

Environment variables (required for Telegram API):
  TELE_TOKEN   – Bot token from @BotFather
  TELE_CHAT_ID – Chat ID to receive the message
"""

import argparse
import os
import sys
import time
import subprocess
import json
import urllib.request

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

if not TELE_TOKEN or not TELE_CHAT_ID:
    sys.stderr.write("[error] TELE_TOKEN and TELE_CHAT_ID must be set in the environment.\n")
    sys.exit(1)

API_URL = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"


def send_telegram(message: str) -> None:
    """Send *message* to the configured Telegram chat."""
    payload = json.dumps({"chat_id": TELE_CHAT_ID, "text": message, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(API_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode()
            # Telegram returns JSON with ok:true on success
            if "\"ok\":true" not in data:
                sys.stderr.write(f"[warning] Telegram API responded unexpectedly: {data}\n")
    except Exception as exc:
        sys.stderr.write(f"[error] Failed to send Telegram message: {exc}\n")


def watch_file(path: str, timeout: int = 0) -> None:
    """Poll *path* every 5 seconds and alert on modification.
    If *timeout* > 0, stop after that many seconds.
    """
    if not os.path.isfile(path):
        sys.stderr.write(f"[error] File '{path}' does not exist.\n")
        sys.exit(1)
    last_mtime = os.path.getmtime(path)
    start = time.time()
    send_telegram(f"👀 Watching *{path}* for changes…")
    while True:
        time.sleep(5)
        if not os.path.isfile(path):
            send_telegram(f"⚠️ File *{path}* disappeared.")
            break
        cur_mtime = os.path.getmtime(path)
        if cur_mtime != last_mtime:
            send_telegram(f"✅ File *{path}* changed at {time.ctime(cur_mtime)}.")
            break
        if timeout and (time.time() - start) > timeout:
            send_telegram(f"⏱️ Watch timeout reached for *{path}*.")
            break


def run_command(command: str, timeout: int = 0) -> None:
    """Execute *command* and send a Telegram message when it finishes.
    Returns exit code in the alert.  *timeout* is passed to subprocess.run.
    """
    send_telegram(f"🚀 Running command: `{command}`")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        status = "✅ Success" if result.returncode == 0 else f"❌ Failure (code {result.returncode})"
        # Truncate long output for the message, but attach full logs as a side‑effect if you like.
        out_preview = (result.stdout[:500] + "…") if len(result.stdout) > 500 else result.stdout
        send_telegram(f"{status}\n```
{out_preview}
```")
    except subprocess.TimeoutExpired:
        send_telegram(f"⏰ Command timed out after {timeout}s: `{command}`")
    except Exception as exc:
        send_telegram(f"⚠️ Exception while running command: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="tiny‑telealert – file watcher / command notifier for Telegram")
    parser.add_argument("--watch", metavar="FILE", help="Path to a file to monitor for changes.")
    parser.add_argument("--cmd", metavar="COMMAND", help="Shell command to execute and notify on completion.")
    parser.add_argument("--timeout", type=int, default=0, help="Optional timeout in seconds (0 = no timeout).")
    args = parser.parse_args()

    if args.watch:
        watch_file(args.watch, timeout=args.timeout)
    elif args.cmd:
        run_command(args.cmd, timeout=args.timeout)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
