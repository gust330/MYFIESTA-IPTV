# MyFiesta IPTV - Automated IPTV Streaming Solution

A fully automated Python application that fetches IPTV credentials from myfiestatrial.com and serves them through a beautiful web interface with channel selection, categories, and streaming capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Web Interface](#web-interface)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)
- [Requirements](#requirements)

## 🎯 Overview

MyFiesta IPTV is an automated solution that:

1. **Automatically fetches credentials** from myfiestatrial.com using browser automation
2. **Serves IPTV streams** through a web interface with full channel list
3. **Organizes channels** by categories for easy navigation
4. **Provides M3U playlist** for use with external IPTV players (VLC, IPTV Smarters, etc.)
5. **Auto-refreshes credentials** every 48 hours to maintain access

## ✨ Features

### Core Functionality
- 🤖 **Fully Automated** - One command fetches credentials and starts the server
- 🌐 **Web Player Interface** - Beautiful, modern web interface with channel selection
- 📺 **Channel List** - Full channel list organized by categories
- 🔍 **Search & Filter** - Search channels by name or filter by category
- 📋 **M3U Playlist** - Download or stream M3U playlist for external players
- 🔄 **Auto-Refresh** - Automatically refreshes credentials every 48 hours
- 📁 **Organized Codebase** - Clean, maintainable folder structure

### Anti-Detection Features
- 🥷 **Stealth Mode** - Browser automation with anti-detection measures
- 🎭 **Human-like Behavior** - Random delays, realistic typing, hover actions
- 🔒 **Fingerprint Masking** - Hides automation indicators
- 🎲 **Random User Agents** - Rotates browser fingerprints

### Web Player Features
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎬 **Multiple Player Support** - Video.js with HLS.js fallback
- ⚡ **Fast Channel Switching** - Instant channel selection
- 📊 **Status Dashboard** - Real-time server and credential status
- 🔑 **Credential Management** - View and manage credentials

## 📁 Project Structure

```
MYFIESTA-IPTV-main/
│
├── main.py                    # 🚀 Main entry point - Run this!
│
├── src/                       # 📦 Source Code
│   ├── __init__.py
│   ├── main.py               # Main launcher orchestrator
│   ├── server.py             # Flask web server with API endpoints
│   ├── credential_manager.py # Credential loading, saving, M3U generation
│   └── playwright_script.py # Browser automation for credential fetching
│
├── templates/                 # 🎨 Web Templates
│   └── index.html            # Web player interface with channel list
│
├── scripts/                   # 🛠️ Utility Scripts
│   ├── __init__.py
│   ├── quick_setup.py        # Quick credential setup helper
│   ├── test_server.py        # Server endpoint testing utility
│   └── create_test_credentials.py  # Test credentials creator
│
├── data/                      # 💾 Data Files (auto-created)
│   └── credentials.json       # Generated credentials (gitignored)
│
├── docs/                      # 📚 Documentation
│   └── README.md              # Detailed documentation
│
├── test_player.py            # 🧪 Test script for manual credential input
├── PROJECT_STRUCTURE.md      # Project structure documentation
├── .gitignore                # Git ignore rules
├── README.md                 # This file
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection
- A valid email address (for manual mode)

### Installation

1. **Clone or download the repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

That's it! The application will:
- Prompt you for an email address
- Automatically fetch credentials (takes 2-5 minutes)
- Start the web server
- Display the URL: http://localhost:5000

## 🔄 How It Works

### 1. Credential Fetching Process

The application uses Playwright (headless browser automation) to:

1. **Navigate** to myfiestatrial.com
2. **Enter email** address (manual input or API-generated)
3. **Click "Generate Access"** button
4. **Wait for verification code**:
   - **Manual Mode**: Prompts you to enter the 6-digit code from your email
   - **API Mode**: Automatically fetches code from temporary email service
5. **Enter verification code** in 6 separate input boxes
6. **Click "Validate"** button
7. **Extract credentials** from the page (username and password)
8. **Save credentials** to `data/credentials.json`

### 2. Server Operation

The Flask server:

1. **Loads credentials** from `data/credentials.json` on startup
2. **Monitors file changes** (auto-reloads when credentials are updated)
3. **Serves web interface** at http://localhost:5000
4. **Fetches channel list** from Xtream Codes API
5. **Parses M3U playlist** to extract all channels and categories
6. **Serves M3U playlist** for download or streaming
7. **Auto-refreshes** credentials every 48 hours

### 3. Web Interface

The web interface:

1. **Fetches channel list** from `/channels` API endpoint
2. **Organizes channels** by category (Movies, Sports, News, etc.)
3. **Displays channel list** in sidebar with search and filter
4. **Allows channel selection** - click any channel to play
5. **Streams content** using Video.js with HLS.js fallback
6. **Shows status** - server status, credential availability, channel count

## 📖 Usage Guide

### Basic Usage

**Run everything in one command:**
```bash
python main.py
```

This will:
1. Check if credentials exist and are valid
2. If not, fetch new credentials automatically
3. Start the web server
4. Display access URL

### Manual Credential Testing

To test with manually provided credentials:
```bash
python test_player.py
```

Enter your credentials when prompted, then start the server.

### Server Only Mode

If credentials already exist and you just want to start the server:
```bash
cd src
python server.py
```

### Fetch Credentials Only

To only fetch credentials without starting the server:
```bash
cd src
python playwright_script.py
```

## ⚙️ Configuration

### Manual vs API Mode

Edit `src/playwright_script.py`:

```python
MANUAL_MODE = True  # Set to True for manual email entry, False for API
```

**Manual Mode (Recommended):**
- You provide your own email address
- You manually enter the verification code
- No API quota limits
- More reliable

**API Mode:**
- Automatically generates temporary email
- Automatically fetches verification code
- Requires RapidAPI key with quota
- Fully automated (no user input needed)

### API Configuration

If using API mode, configure your RapidAPI key in `src/playwright_script.py`:

```python
RAPIDAPI_KEY = "your-rapidapi-key-here"
RAPIDAPI_HOST = "gmailnator.p.rapidapi.com"
```

### Server Configuration

Edit `src/server.py` to change:

```python
REFRESH_INTERVAL_HOURS = 48  # How often to refresh credentials
CREDENTIALS_FILE = "data/credentials.json"  # Credentials file path
```

### Port Configuration

Default port is 5000. To change, edit `src/server.py`:

```python
app.run(host='0.0.0.0', port=5000, ...)  # Change port number
```

## 🌐 Web Interface

### Main Features

**Channel List Sidebar:**
- All channels organized by category
- Expandable/collapsible categories
- Search box to find channels
- Category filter dropdown
- Channel count display

**Video Player:**
- Full-featured video player
- Playback controls
- Channel information display
- Error messages with troubleshooting

**Status Bar:**
- Server status indicator
- Total channel count
- Refresh button
- Real-time updates

### Accessing the Interface

Once the server is running:

- **Main Interface**: http://localhost:5000
- **M3U Playlist**: http://localhost:5000/playlist.m3u
- **Status API**: http://localhost:5000/status
- **Channels API**: http://localhost:5000/channels
- **Credentials API**: http://localhost:5000/credentials
- **Debug Info**: http://localhost:5000/debug

## 🔌 API Endpoints

### GET `/`
Returns the main web player interface (HTML)

### GET `/playlist.m3u`
Returns the M3U playlist file with all channels
- **Content-Type**: `application/x-mpegurl`
- **Usage**: Download or use in IPTV players

### GET `/channels`
Returns parsed channel list as JSON
```json
{
  "channels": [...],
  "categories": [...],
  "channels_by_category": {...},
  "total_channels": 1234
}
```

### GET `/status`
Returns server status as JSON
```json
{
  "status": "active",
  "last_refresh": "2025-12-01T18:24:50",
  "next_refresh": "2025-12-03T18:24:50",
  "error": null,
  "credentials_available": true
}
```

### GET `/credentials`
Returns current credentials (username, password, URL)
- **Note**: Only available if credentials are loaded

### GET `/refresh`
Manually triggers credential reload from file
- **Returns**: Success/error status

### GET `/debug`
Returns debug information about server state

## 🔧 Troubleshooting

### Credentials Issues

**"Credentials file not found"**
- Run `python main.py` to fetch new credentials
- Or use `python test_player.py` to manually enter credentials

**"Credentials already used"**
- Credentials are marked as used after first playlist generation
- Run `python main.py` again to fetch new credentials
- The system will automatically fetch new ones when needed

**"User is not allowed"**
- The website may be detecting automation
- Try waiting longer between attempts
- Use a different email address
- The anti-detection measures should help, but some restrictions may apply

### Server Issues

**"Port 5000 already in use"**
- Stop other applications using port 5000
- Or change the port in `src/server.py`

**"Server won't start"**
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (needs 3.7+)
- Check for error messages in console

**"Credentials not loading"**
- Verify `data/credentials.json` exists
- Check file format is valid JSON
- Click "Refresh Now" button in web interface
- Check server console for error messages

### Playback Issues

**"Playback error" or "Stream not playing"**
- Some streams may be geo-blocked or require specific codecs
- Try selecting a different channel
- Check browser console (F12) for detailed errors
- Try a different browser (Chrome, Firefox, Edge)
- Some streams may require CORS headers or proxy

**"Format not supported"**
- The stream format may not be supported by your browser
- Try downloading the M3U playlist and using VLC or another IPTV player
- Some channels may use proprietary formats

### Browser Automation Issues

**"Timeout waiting for element"**
- The website structure may have changed
- Check screenshots in project root for debugging
- Increase timeout values in `src/playwright_script.py`

**"Could not extract credentials"**
- The page structure may have changed
- Check screenshots to see what the page looks like
- Verify the website is accessible

## 🔬 Technical Details

### Browser Automation

The application uses Playwright for browser automation with:

- **Stealth Mode**: Disables automation detection flags
- **Realistic Fingerprinting**: Random user agents, realistic headers
- **Human-like Behavior**: Random delays, character-by-character typing
- **Anti-Detection Scripts**: Hides webdriver property, mocks browser APIs

### Credential Storage

Credentials are stored in JSON format:
```json
{
  "email": "user@example.com",
  "username": "TV-123456789",
  "password": "987654321",
  "url": "http://trial.ifiesta.net",
  "last_update": "2025-12-01T18:24:50.824183",
  "used": false
}
```

### M3U Playlist Generation

The system:
1. Fetches full M3U playlist from Xtream Codes API
2. Parses channels with metadata (name, logo, category)
3. Serves parsed data via `/channels` endpoint
4. Provides raw M3U via `/playlist.m3u` endpoint

### File Monitoring

The server monitors `data/credentials.json` for changes:
- **Watchdog** (if installed): Real-time file watching
- **Polling** (fallback): Checks every 3 seconds
- Automatically reloads credentials when file changes

### Stream Playback

The web player uses:
1. **Video.js** - Primary player with HLS support
2. **HLS.js** - Fallback for HLS streams
3. **Native HTML5** - Final fallback for browser compatibility

## 📋 Requirements

### Python Packages

```
flask>=2.0.0
playwright>=1.40.0
apscheduler>=3.10.0
```

Install with:
```bash
pip install -r requirements.txt
```

### System Requirements

- **Python**: 3.7 or higher
- **Browser**: Chromium (installed via Playwright)
- **OS**: Windows, macOS, or Linux
- **RAM**: Minimum 2GB recommended
- **Internet**: Required for credential fetching and streaming

### Browser Installation

After installing Python packages, install Playwright browsers:

```bash
playwright install chromium
```

## 🎓 How the Components Work Together

### 1. Main Launcher (`main.py`)

The entry point that:
- Checks dependencies
- Calls credential fetching
- Starts the server
- Handles errors gracefully

### 2. Credential Fetcher (`src/playwright_script.py`)

Browser automation script that:
- Opens headless browser
- Navigates to registration page
- Handles email input and verification
- Extracts username and password
- Saves to JSON file

### 3. Credential Manager (`src/credential_manager.py`)

Manages credential lifecycle:
- Loads credentials from JSON
- Saves credentials to JSON
- Generates M3U playlists
- Marks credentials as used
- Validates credential format

### 4. Web Server (`src/server.py`)

Flask application that:
- Serves web interface
- Provides API endpoints
- Monitors credential file
- Fetches and parses channel lists
- Handles streaming requests

### 5. Web Interface (`templates/index.html`)

Frontend application that:
- Fetches channel list
- Displays organized channel list
- Handles channel selection
- Manages video playback
- Shows status information

## 🔐 Security Notes

- **Credentials Storage**: Credentials are stored locally in `data/credentials.json`
- **Git Ignore**: Credentials file is excluded from version control
- **Network Access**: Server binds to `0.0.0.0` (accessible on network)
- **No Authentication**: Web interface has no authentication (local use only)
- **API Keys**: RapidAPI key is hardcoded (consider using environment variables)

## 🐛 Known Issues

1. **Stream Playback**: Some streams may not play in web browser due to:
   - Codec compatibility
   - CORS restrictions
   - Geo-blocking
   - Stream format limitations

2. **Website Detection**: The target website may detect automation and block requests

3. **API Quota**: RapidAPI free tier has daily quota limits

## 💡 Tips & Best Practices

1. **Use Manual Mode**: More reliable than API mode
2. **Check Screenshots**: If automation fails, check screenshot files for debugging
3. **External Players**: For best compatibility, use the M3U playlist with VLC or IPTV Smarters
4. **Network Access**: Change `host='0.0.0.0'` to `host='127.0.0.1'` for local-only access
5. **Credential Refresh**: Credentials expire after 48 hours, system auto-refreshes

## 📝 License

This project is for educational purposes only. Use responsibly and in accordance with the terms of service of the websites involved.

## 🤝 Contributing

This is a personal project. Feel free to fork and modify for your own use.

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review browser console errors (F12)
3. Check server console output
4. Review screenshot files for debugging

---

**Made with ❤️ for automated IPTV streaming**
