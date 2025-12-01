# Project Structure

## 📁 Directory Organization

```
MYFIESTA-IPTV-main/
│
├── main.py                    # 🚀 Main entry point - Run this!
│
├── src/                       # 📦 Source Code
│   ├── __init__.py
│   ├── main.py               # Main launcher logic
│   ├── server.py              # Flask web server
│   ├── credential_manager.py # Credential management
│   └── playwright_script.py  # Automated credential fetching
│
├── templates/                 # 🎨 Web Templates
│   └── index.html            # Web player interface
│
├── scripts/                   # 🛠️ Utility Scripts
│   ├── __init__.py
│   ├── quick_setup.py        # Quick credential setup helper
│   ├── test_server.py        # Server testing utility
│   └── create_test_credentials.py  # Test credentials creator
│
├── data/                      # 💾 Data Files (auto-created)
│   └── credentials.json      # Generated credentials (auto-created)
│
├── docs/                      # 📚 Documentation
│   └── README.md             # Detailed documentation
│
├── .gitignore                 # Git ignore rules
├── README.md                  # Main README
└── requirements.txt           # Python dependencies
```

## 🎯 Quick Start

**Run from project root:**
```bash
python main.py
```

## 📝 File Descriptions

### Root Level
- **main.py** - Main entry point that launches everything
- **README.md** - Quick start guide
- **requirements.txt** - Python package dependencies

### src/ - Source Code
- **main.py** - Main launcher that orchestrates credential fetching and server startup
- **server.py** - Flask web server with all API endpoints
- **credential_manager.py** - Handles credential loading, saving, and M3U playlist generation
- **playwright_script.py** - Automated browser script to fetch credentials from myfiestatrial.com

### templates/ - Web Interface
- **index.html** - Beautiful web player interface with status dashboard

### scripts/ - Utilities
- **quick_setup.py** - Helper to quickly create credentials.json
- **test_server.py** - Test script to verify server endpoints
- **create_test_credentials.py** - Create test credentials for development

### data/ - Data Storage
- **credentials.json** - Auto-generated file containing IPTV credentials (gitignored)

### docs/ - Documentation
- **README.md** - Detailed documentation and troubleshooting guide

## 🔄 Migration Notes

All file paths have been updated to work with the new structure:
- Credentials are stored in `data/credentials.json`
- Templates are in `templates/`
- All imports have been updated
- Entry point is `main.py` in the root directory

