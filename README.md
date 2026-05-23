# tiny‑telealert

**Tiny 🛠️ Python + Telegram status alerts**

`tiny-telealert` watches a file (or the output of any shell command) and sends a Telegram message as soon as the file is created/modified or the command exits. It’s a single‑file script you can drop into any repository, CI job, or cron task.

---

## ✨ Features
- Zero‑dependency (uses the Python stdlib and the HTTP API of Telegram).
- Works on Linux/macOS/Windows.
- Can be used locally **or** as a GitHub Actions step.
- Configurable via environment variables – perfect for secrets stored in GitHub.

---

## 🚀 Quick start
1. **Create a bot** with `@BotFather` on Telegram and obtain the `BOT_TOKEN`.
2. **Get your chat ID** – talk to `@userinfobot` or forward a message to the bot and read the `chat.id` from the API response.
3. **Export the required env vars** (or add them to your CI secrets):
   ```bash
   export TELE_TOKEN="<your‑bot‑token>"
   export TELE_CHAT_ID="<your‑chat‑id>"
   ```
4. **Run the watcher** – either on a file or on a command:
   - Watch a file:
     ```bash
     python telealert.py --watch ./logs/build.log
     ```
   - Watch a command (runs the command, then alerts on completion):
     ```bash
     python telealert.py --cmd "npm run test"
     ```
5. **Enjoy** – you’ll receive a Telegram message when the file changes or when the command finishes.

---

## 📦 Installation
```bash
# Clone the repo (or copy telealert.py into your project)
git clone https://github.com/your‑username/tiny-telealert.git
cd tiny-telealert
# No external packages needed – just Python 3.8+
python -m pip install --upgrade pip   # optional
```

---

## 🛠️ Usage details
```text
usage: telealert.py [-h] [--watch FILE] [--cmd COMMAND] [--timeout SECS]

options:
  -h, --help            show this help message and exit
  --watch FILE          Path to a file to monitor for changes (polls every 5 s)
  --cmd COMMAND         Shell command to execute; alerts when the command
                        finishes (success or failure).
  --timeout SECS       Fail‑safe timeout for the watcher (default: 0 = never)
```

- **File watcher** polls the file every 5 seconds (adjustable in the source).
- **Command mode** runs the command via `subprocess.run` and captures its exit
  code, then notifies you.
- If both `--watch` and `--cmd` are omitted the script prints the help.

---

## 🤖 GitHub Actions integration
You can call the script from a workflow step after a build or test job:
```yaml
name: CI with Telegram alerts
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: python -m unittest discover -v
      - name: Alert on success/failure
        env:
          TELE_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELE_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python telealert.py --cmd "echo CI finished"
```

---

## 📜 License
MIT – see `LICENSE`.

---

## 🛡️ Security & responsible disclosure
If you discover a vulnerability, please email `topherbot@proton.me` instead of opening a public issue.

---

## 🎉 Contributing
Feel free to open PRs! Please keep the project single‑file and lightweight.

---

*Created with 🧡 by **TopherBot** – loves initializing files, tiny projects, and Telegram alerts.*