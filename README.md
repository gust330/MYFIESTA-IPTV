# MYFIESTA IPTV — Automated Credential & M3U Renewal Service 📺

> **Automated headless pipeline that rotates IPTV trial credentials every 48 hours, formats live M3U playlist endpoints, and delivers fresh streaming links to your inbox for seamless playback in VLC Media Player.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](#requirements)
[![Automation](https://img.shields.io/badge/Automation-Playwright%20Headless-45ba4b.svg?logo=playwright&logoColor=white)](#architecture)
[![Scheduler](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20(48h%20Cron)-orange.svg?logo=githubactions&logoColor=white)](#automated-github-actions-deployment)
[![Delivery](https://img.shields.io/badge/Delivery-SMTP%20Email-informational.svg)](#email-configuration)
[![Playback](https://img.shields.io/badge/Player-VLC%20Media%20Player-FF8800.svg?logo=vlc-media-player&logoColor=white)](#playing-in-vlc)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## Overview

IPTV trial playlists typically expire within 48 hours, requiring manual account re-registration, disposable email handling, credential extraction, and playlist URL reconstruction.

**MYFIESTA IPTV** completely automates this maintenance loop. Operating headlessly via Playwright and temporary disposable inbox APIs, it generates credentials on schedule, builds the valid M3U stream URL, and dispatches an automated notification email directly to the user.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MYFIESTA IPTV AUTOMATION LOOP                   │
├────────────────────────────────┬───────────────────────────────────────┤
│  [📬] Disposable Email API     │  [🎭] Headless Playwright Engine      │
│  · RapidAPI / Gmailnator       │  · Headless Chromium browser          │
│  · Temporary @gmail mailbox    │  · Automates portal trial forms       │
│  · Instant verification grab   │  · Captures host, user & pass tokens  │
├────────────────────────────────┴───────────────────────────────────────┤
│                     [⚡] M3U Playlist Generator                         │
│  Constructs: http://{host}:{port}/get.php?username={u}&password={p}&...│
├────────────────────────────────┬───────────────────────────────────────┤
│  [📧] SMTP Email Dispatcher    │  [🎬] Direct Playback (VLC)           │
│  · Secure TLS transport        │  · One-click network stream import    │
│  · Formatted HTML mailer       │  · Zero manual credential renewal     │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## Key Features

- **Autonomous Web Automation**: Employs Playwright (`src/playwright_script.py`) to bypass manual form filling and account creation flows.
- **Dynamic M3U Link Builder**: Formats authenticated HLS/MPEG-TS playlist links compatible with VLC, Kodi, or IPTV smart TV players.
- **Automated Scheduling**: Runs locally as a continuous background daemon (`src/email_scheduler.py`) or serverlessly on a 48-hour GitHub Actions schedule.
- **Multi-Provider SMTP Support**: Pre-configured for Gmail (App Passwords) and Microsoft Outlook.

---

## Playing in VLC Media Player

Once you receive your renewal email with the active M3U link:

1. Launch **VLC Media Player**.
2. Press `Ctrl + N` (or navigate to **Media → Open Network Stream...**).
3. Paste the M3U link received in your inbox.
4. Click **Play** (`Enter`).
5. *Tip:* Press `Ctrl + L` to view the full channel playlist and filter by category.

---

## Installation & Setup

### Requirements

- **Python 3.8+** (Python 3.10+ recommended)
- **Playwright** with Chromium binaries
- A **RapidAPI Key** for disposable inbox verification ([Gmailnator API](https://rapidapi.com/johndevz/api/gmailnator))
- An **SMTP Email Account** (e.g., Gmail with App Password)

### 1. Local Setup

```bash
# Clone the repository
git clone https://github.com/gust330/MYFIESTA-IPTV.git
cd MYFIESTA-IPTV

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 2. Configuration

Run the interactive setup helper:

```bash
python scripts/setup_email.py
```

This writes your credentials to `data/config.json`:

```json
{
  "email_config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "receiver_email": "destination@gmail.com"
  }
}
```

Configure your RapidAPI key in `src/playwright_script.py` or via environment variable `RAPIDAPI_KEY`.

### 3. Execution

```bash
# Run a one-time test cycle (fetch credentials -> generate M3U -> send email)
python -m src.send_m3u_email

# Or run the local 48-hour scheduler daemon
python -m src.email_scheduler
```

---

## Automated GitHub Actions Deployment (Recommended)

To run the renewal service 24/7 in the cloud with zero hosting costs:

1. Push the repository to GitHub.
2. In **Settings → Secrets and variables → Actions**, add:
   - `RAPIDAPI_KEY`
   - `SMTP_SERVER` (*e.g., `smtp.gmail.com`*)
   - `SMTP_PORT` (*e.g., `587`*)
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECEIVER_EMAIL`
3. The included workflow (`.github/workflows/iptv-renewal.yml`) will run automatically every 48 hours and can also be triggered manually under **Actions → IPTV Auto Renewal → Run workflow**.

---

## Project Structure

```
MYFIESTA-IPTV/
├── src/
│   ├── send_m3u_email.py       # Orchestration script (fetch + format + dispatch)
│   ├── playwright_script.py    # Headless credential automation
│   ├── m3u_generator.py        # M3U stream URL formatting
│   ├── email_sender.py         # SMTP email delivery client
│   └── email_scheduler.py      # Local recurring 48-hour timer
├── scripts/
│   ├── setup_email.py          # Interactive CLI configuration wizard
│   ├── setup_render.sh         # Render.com deployment script
│   └── setup_windows_task.ps1  # Windows Task Scheduler automation
├── data/                       # Local JSON cache & credentials (git-ignored)
├── DEPLOYMENT_GUIDE.md         # Detailed cloud hosting walk-through
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Author & Disclaimer

Engineered by **Gustavo Teixeira** ([@gust330](https://github.com/gust330)).  
This project is provided for educational and automation demonstration purposes.
