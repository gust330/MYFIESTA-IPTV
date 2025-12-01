# MyFiesta IPTV - Automated IPTV Streaming Solution

A fully automated solution that fetches IPTV credentials and serves them through a web interface.

## Quick Start

**Just run one command:**

```bash
python main.py
```

That's it! The script will:
1. ✅ Automatically fetch credentials from myfiestatrial.com
2. ✅ Start the web server
3. ✅ Make everything available at http://localhost:5000

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install flask playwright apscheduler
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

3. **Run the main script:**
   ```bash
   python main.py
   ```

## Usage

### Automatic Mode (Recommended)
```bash
python main.py
```

The script will:
- Prompt you for an email address (manual mode)
- Automatically register and fetch credentials
- Start the web server
- Open http://localhost:5000 in your browser

### Manual Credential Fetching
If you want to fetch credentials separately:
```bash
python playwright_script.py
```

### Server Only
If credentials already exist:
```bash
python server.py
```

## Features

- 🚀 **Fully Automated** - One command does everything
- 🌐 **Web Interface** - Beautiful web player at http://localhost:5000
- 📱 **IPTV Compatible** - Works with VLC, IPTV Smarters, etc.
- 🔄 **Auto-Refresh** - Automatically refreshes credentials every 48 hours
- 📋 **M3U Playlist** - Download or stream the playlist directly

## Web Interface

Once the server is running, access:

- **Main Player**: http://localhost:5000
- **Playlist**: http://localhost:5000/playlist.m3u
- **Status API**: http://localhost:5000/status
- **Credentials API**: http://localhost:5000/credentials

## Configuration

### Manual vs API Mode

Edit `playwright_script.py`:
```python
MANUAL_MODE = True  # Set to False to use API (requires RapidAPI key)
```

### API Configuration

If using API mode, set your RapidAPI key in `playwright_script.py`:
```python
RAPIDAPI_KEY = "your-api-key-here"
```

## Troubleshooting

### "Credentials file not found"
- Run `python main.py` to fetch new credentials

### "API quota exceeded"
- Use manual mode (set `MANUAL_MODE = True`)
- Or wait for quota to reset

### Server won't start
- Make sure port 5000 is not in use
- Check that all dependencies are installed

### Credentials not loading
- Check `credentials.json` exists
- Verify the file format is valid JSON
- Try clicking "Refresh Now" in the web interface

## File Structure

```
MYFIESTA-IPTV-main/
├── main.py              # Main launcher (run this!)
├── server.py            # Flask web server
├── playwright_script.py # Credential fetching script
├── credential_manager.py # Credential management
├── templates/
│   └── index.html      # Web player interface
├── credentials.json    # Generated credentials (auto-created)
└── README.md           # This file
```

## Requirements

- Python 3.7+
- Flask
- Playwright
- APScheduler
- Internet connection

## License

This project is for educational purposes only.
