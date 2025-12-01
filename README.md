# MyFiesta IPTV - Automated Credential Manager

Automatically fetches Xtream Code credentials from myfiestatrial.com every 48 hours and serves an M3U playlist that you can watch on any device.

## Features

- 🔄 **Auto-Refresh**: Automatically fetches new credentials every 47 hours (before the 48-hour expiration)
- 📺 **Web Player**: Built-in web interface with video player
- 📱 **Multi-Device**: Access your playlist from any device on your network
- 🎬 **M3U Playlist**: Standard format compatible with all IPTV players
- 📊 **Status Dashboard**: Monitor credential status and refresh times
- 🔑 **Credential Management**: View and manually refresh credentials

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Start the Server

```bash
python server.py
```

The server will:
- Automatically fetch initial credentials
- Start a web server on `http://localhost:5000`
- Schedule automatic refresh every 47 hours

### 3. Access Your Stream

**Option A: Web Browser**
- Open `http://localhost:5000` in your browser
- Use the built-in player or copy the playlist URL

**Option B: IPTV Player App**
- Use the playlist URL: `http://<your-ip>:5000/playlist.m3u`
- Compatible with VLC, IPTV Smarters, Perfect Player, etc.

**Option C: Other Devices**
- Find your computer's IP address (e.g., `192.168.1.100`)
- Access from phone/tablet: `http://192.168.1.100:5000`

## Endpoints

- `/` - Web player interface with status dashboard
- `/playlist.m3u` - M3U playlist file (download or stream)
- `/status` - JSON status information
- `/credentials` - Current credentials (JSON)
- `/refresh` - Manually trigger credential refresh

## Configuration

Edit `server.py` or `credential_manager.py` to customize:

- **Manual Mode**: Set `manual_mode=True` to manually enter email and verification code
- **API Key**: Update `RAPIDAPI_KEY` in `credential_manager.py` if needed
- **Refresh Interval**: Change `hours=47` in `server.py` to adjust refresh frequency
- **Port**: Change `port=5000` in `server.py` to use a different port

## File Structure

```
MYFIESTA-IPTV-main/
├── credential_manager.py   # Core credential fetching logic
├── server.py              # Flask web server with scheduler
├── templates/
│   └── index.html        # Web player interface
├── credentials.json      # Saved credentials (auto-generated)
├── playlist.m3u         # M3U playlist (auto-generated)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## How It Works

1. **Credential Fetching**: Uses Playwright to automate registration on myfiestatrial.com
2. **Email Generation**: Uses Emailnator API to generate temporary emails
3. **Verification**: Automatically retrieves and enters the verification code
4. **Extraction**: Extracts username and password from the success page
5. **Playlist Generation**: Creates M3U playlist with Xtream Codes format
6. **Auto-Refresh**: Background scheduler refreshes credentials every 47 hours
7. **Web Serving**: Flask server provides multiple access methods

## Troubleshooting

**Credentials not fetching:**
- Check your internet connection
- Verify the RapidAPI key is valid
- Try manual mode: `credential_manager = CredentialManager(manual_mode=True)`

**Can't access from other devices:**
- Make sure your firewall allows port 5000
- Verify devices are on the same network
- Use your computer's local IP, not `localhost`

**Playlist not working in IPTV app:**
- Ensure credentials are valid (check `/status`)
- Try downloading the M3U file and importing it
- Some apps require the full Xtream Codes API (username/password/URL) instead of M3U

## Manual Testing

Test the credential manager independently:

```bash
python credential_manager.py
```

This will fetch credentials and save them to `credentials.json` and `playlist.m3u`.

## Original Script

The original `playwright_script.py` is still available for standalone use. The new system refactors this into reusable modules with added automation.

## License

This project is for educational purposes only. Respect the terms of service of myfiestatrial.com.
