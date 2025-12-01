from flask import Flask, Response, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

# Handle both package and direct imports
try:
    from .credential_manager import CredentialManager
except ImportError:
    from credential_manager import CredentialManager
from datetime import datetime, timedelta
import os
import threading
import time
import json

# Try to import watchdog for file watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Configuration
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "data", "credentials.json")
REFRESH_INTERVAL_HOURS = 48

# Ensure data directory exists
os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Make these available for import
__all__ = [
    'app', 'load_credentials_from_file', 'credential_manager', 'status',
    'setup_file_monitoring', 'scheduler', 'reset_status', 'CREDENTIALS_FILE'
]

# Global instances
credential_manager = CredentialManager(manual_mode=True)
scheduler = BackgroundScheduler()
refresh_lock = threading.Lock()
file_observer = None

# Status tracking - initialize fresh
status = {
    'last_refresh': None,
    'next_refresh': None,
    'status': 'initializing',  # initializing, active, error, refreshing
    'error': None
}

def reset_status():
    """Reset status to initial state"""
    global status
    status = {
        'last_refresh': None,
        'next_refresh': None,
        'status': 'initializing',
        'error': None
    }


def load_credentials_from_file():
    """Load credentials from JSON file and update status"""
    global status
    
    with refresh_lock:
        try:
            print(f"\n[{datetime.now()}] Loading credentials from {CREDENTIALS_FILE}...")
            print(f"   File exists: {os.path.exists(CREDENTIALS_FILE)}")
            
            # Clear any previous errors first
            status['error'] = None
            status['status'] = 'refreshing'
            
            # Check if file exists
            if not os.path.exists(CREDENTIALS_FILE):
                status['status'] = 'error'
                status['error'] = f"Credentials file not found: {CREDENTIALS_FILE}"
                print(f"❌ ERROR: {status['error']}")
                return False
            
            # Read and validate file first
            try:
                with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    print(f"   File size: {len(file_content)} bytes")
                    print(f"   File preview: {file_content[:100]}...")
            except Exception as e:
                status['status'] = 'error'
                status['error'] = f"Cannot read credentials file: {str(e)}"
                print(f"❌ ERROR: {status['error']}")
                return False
            
            # Load credentials using credential_manager
            print("   Calling credential_manager.load_credentials()...")
            loaded = credential_manager.load_credentials(CREDENTIALS_FILE)
            
            if not loaded:
                status['status'] = 'error'
                status['error'] = "Failed to load credentials. File may be invalid or credentials are already used."
                print(f"❌ ERROR: {status['error']}")
                print(f"   credential_manager.credentials: {credential_manager.credentials}")
                print(f"   credential_manager.used: {credential_manager.used}")
                return False
            
            # Verify credentials were actually loaded
            if not credential_manager.credentials:
                status['status'] = 'error'
                status['error'] = "Credentials manager returned None"
                print(f"❌ ERROR: {status['error']}")
                return False
            
            # Success - update status
            status['status'] = 'active'
            status['error'] = None  # Explicitly clear error
            
            if credential_manager.last_update:
                status['last_refresh'] = credential_manager.last_update
            else:
                status['last_refresh'] = datetime.now()
            
            status['next_refresh'] = status['last_refresh'] + timedelta(hours=REFRESH_INTERVAL_HOURS)
            
            print(f"✅ Credentials loaded successfully!")
            print(f"   Username: {credential_manager.credentials['username']}")
            print(f"   Password: {'*' * len(credential_manager.credentials['password'])}")
            print(f"   URL: {credential_manager.credentials['url']}")
            print(f"   Used: {credential_manager.credentials.get('used', False)}")
            print(f"   Last Update: {status['last_refresh']}")
            print(f"   Next Refresh: {status['next_refresh']}")
            
            return True
            
        except Exception as e:
            status['status'] = 'error'
            status['error'] = f"Error loading credentials: {str(e)}"
            print(f"❌ EXCEPTION: {status['error']}")
            import traceback
            traceback.print_exc()
            return False


def check_file_changes():
    """Poll for file changes (fallback if watchdog not available)"""
    try:
        if os.path.exists(CREDENTIALS_FILE):
            current_mtime = os.path.getmtime(CREDENTIALS_FILE)
            if not hasattr(check_file_changes, 'last_mtime'):
                check_file_changes.last_mtime = current_mtime
                return
            
            if current_mtime > check_file_changes.last_mtime:
                check_file_changes.last_mtime = current_mtime
                print(f"[{datetime.now()}] File change detected (polling). Reloading credentials...")
                load_credentials_from_file()
    except Exception as e:
        print(f"Error checking file changes: {e}")


class CredentialsFileHandler(FileSystemEventHandler):
    """Watchdog handler for credentials.json file changes"""
    
    def on_modified(self, event):
        if event.src_path.endswith(CREDENTIALS_FILE) or event.src_path.endswith(os.path.basename(CREDENTIALS_FILE)):
            print(f"\n[{datetime.now()}] File change detected. Reloading credentials...")
            time.sleep(0.3)  # Small delay to ensure file write is complete
            load_credentials_from_file()


def setup_file_monitoring():
    """Setup file monitoring (watchdog or polling)"""
    global file_observer
    
    if WATCHDOG_AVAILABLE:
        try:
            event_handler = CredentialsFileHandler()
            file_observer = Observer()
            # Watch the data directory
            data_dir = os.path.dirname(CREDENTIALS_FILE)
            file_observer.schedule(event_handler, path=data_dir, recursive=False)
            file_observer.start()
            print("✅ File watching enabled (watchdog)")
        except Exception as e:
            print(f"⚠️  Could not start file watcher: {e}")
            print("   Falling back to polling...")
            scheduler.add_job(
                func=check_file_changes,
                trigger='interval',
                seconds=3,
                id='file_polling',
                replace_existing=True
            )
    else:
        print("⚠️  Watchdog not available. Using polling (every 3 seconds)")
        scheduler.add_job(
            func=check_file_changes,
            trigger='interval',
            seconds=3,
            id='file_polling',
            replace_existing=True
        )


# Flask Routes
@app.route('/')
def index():
    """Main page with player and status"""
    return render_template('index.html')


@app.route('/playlist.m3u')
def playlist():
    """Serve the M3U playlist"""
    try:
        # Reload credentials if missing
        if not credential_manager.credentials:
            print("Credentials missing. Reloading...")
            load_credentials_from_file()
        
        if not credential_manager.credentials:
            return Response(
                "#EXTM3U\n# No credentials available. Please run main.py to generate credentials.",
                status=503,
                mimetype='application/x-mpegurl'
            )
        
        # Generate playlist (marks credentials as used only on first use)
        # Even if marked as used, try to generate playlist - credentials might still work
        m3u_content = credential_manager.generate_m3u_playlist()
        
        return Response(
            m3u_content,
            mimetype='application/x-mpegurl',
            headers={
                'Content-Disposition': 'attachment; filename=playlist.m3u',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
    except Exception as e:
        return Response(
            f"#EXTM3U\n# Error: {str(e)}",
            status=500,
            mimetype='application/x-mpegurl'
        )


@app.route('/stream')
def proxy_stream():
    """Proxy stream to handle CORS issues"""
    try:
        import urllib.request
        from flask import request
        
        stream_url = request.args.get('url')
        if not stream_url:
            return Response("Missing url parameter", status=400)
        
        # Validate URL is from our credentials
        if not credential_manager.credentials:
            return Response("No credentials", status=503)
        
        # Fetch and proxy the stream
        req = urllib.request.Request(stream_url)
        req.add_header('User-Agent', 'MyFiesta-IPTV/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return Response(
                response.read(),
                mimetype=response.headers.get('Content-Type', 'video/mp2t'),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'no-cache'
                }
            )
    except Exception as e:
        return Response(f"Stream error: {str(e)}", status=500)


@app.route('/channels')
def get_channels():
    """Get parsed channel list with categories"""
    try:
        import urllib.request
        import re
        
        # Reload credentials if missing
        if not credential_manager.credentials:
            load_credentials_from_file()
        
        if not credential_manager.credentials:
            return jsonify({'error': 'No credentials available'}), 503
        
        username = credential_manager.credentials['username']
        password = credential_manager.credentials['password']
        url = credential_manager.credentials['url']
        
        playlist_url = f"{url}/get.php?username={username}&password={password}&type=m3u_plus&output=ts"
        
        # Fetch the M3U playlist
        req = urllib.request.Request(playlist_url)
        req.add_header('User-Agent', 'MyFiesta-IPTV/1.0')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            m3u_content = response.read().decode('utf-8')
        
        # Parse M3U to extract channels
        channels = []
        categories = set()
        current_channel = None
        
        for line in m3u_content.split('\n'):
            line = line.strip()
            
            # Parse EXTINF line: #EXTINF:-1 tvg-id="..." tvg-name="..." tvg-logo="..." group-title="Category",Channel Name
            if line.startswith('#EXTINF:'):
                # Extract metadata
                tvg_id = re.search(r'tvg-id="([^"]*)"', line)
                tvg_name = re.search(r'tvg-name="([^"]*)"', line)
                tvg_logo = re.search(r'tvg-logo="([^"]*)"', line)
                group_title = re.search(r'group-title="([^"]*)"', line)
                channel_name = line.split(',')[-1] if ',' in line else ''
                
                current_channel = {
                    'id': tvg_id.group(1) if tvg_id else '',
                    'name': channel_name or (tvg_name.group(1) if tvg_name else ''),
                    'logo': tvg_logo.group(1) if tvg_logo else '',
                    'category': group_title.group(1) if group_title else 'Uncategorized',
                    'url': None
                }
                
                if current_channel['category']:
                    categories.add(current_channel['category'])
            
            # Next line after EXTINF is the stream URL
            elif line and (line.startswith('http://') or line.startswith('https://')) and current_channel:
                current_channel['url'] = line
                channels.append(current_channel)
                current_channel = None
        
        # Organize by category
        channels_by_category = {}
        for channel in channels:
            cat = channel['category']
            if cat not in channels_by_category:
                channels_by_category[cat] = []
            channels_by_category[cat].append(channel)
        
        return jsonify({
            'channels': channels,
            'categories': sorted(list(categories)),
            'channels_by_category': channels_by_category,
            'total_channels': len(channels)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def get_status():
    """Get current server status"""
    return jsonify({
        'status': status['status'],
        'last_refresh': status['last_refresh'].isoformat() if status['last_refresh'] else None,
        'next_refresh': status['next_refresh'].isoformat() if status['next_refresh'] else None,
        'error': status['error'],
        'credentials_available': credential_manager.credentials is not None and not credential_manager.is_used()
    })


@app.route('/credentials')
def get_credentials():
    """Get current credentials"""
    if not credential_manager.credentials or credential_manager.is_used():
        return jsonify({'error': 'No credentials available'}), 503
    
    return jsonify({
        'username': credential_manager.credentials['username'],
        'password': credential_manager.credentials['password'],
        'url': credential_manager.credentials['url'],
        'last_update': credential_manager.last_update.isoformat() if credential_manager.last_update else None
    })


@app.route('/refresh', methods=['GET', 'POST'])
def refresh():
    """Manually trigger credential refresh"""
    print(f"\n[REFRESH] Manual refresh triggered at {datetime.now()}")
    print(f"[REFRESH] Status before: {status}")
    
    # Clear any previous errors
    status['error'] = None
    status['status'] = 'refreshing'
    
    success = load_credentials_from_file()
    
    print(f"[REFRESH] Status after: {status}")
    print(f"[REFRESH] Success: {success}")
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Credentials reloaded successfully',
            'status': status['status'],
            'credentials_available': credential_manager.credentials is not None
        })
    else:
        return jsonify({
            'success': False,
            'error': status['error'],
            'status': status['status']
        }), 500


@app.route('/debug')
def debug():
    """Debug endpoint"""
    return jsonify({
        'status': status,
        'file_exists': os.path.exists(CREDENTIALS_FILE),
        'credentials_loaded': credential_manager.credentials is not None,
        'credentials_used': credential_manager.is_used() if credential_manager.credentials else None,
        'watchdog_available': WATCHDOG_AVAILABLE
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("MYFIESTA IPTV SERVER")
    print("="*70)
    
    # Reset status to ensure clean state
    reset_status()
    
    # Load credentials on startup
    print("\n[STARTUP] Initializing...")
    print(f"[STARTUP] Current status: {status}")
    load_credentials_from_file()
    print(f"[STARTUP] Status after load: {status}")
    
    # Setup file monitoring
    setup_file_monitoring()
    
    # Schedule periodic refresh
    scheduler.add_job(
        func=load_credentials_from_file,
        trigger='interval',
        hours=REFRESH_INTERVAL_HOURS - 1,  # Refresh 1 hour before expiry
        id='periodic_refresh',
        replace_existing=True
    )
    
    scheduler.start()
    
    print("\n" + "="*70)
    print("SERVER READY")
    print("="*70)
    print(f"🌐 Local:    http://localhost:5000")
    print(f"🌐 Network: http://<your-ip>:5000")
    print(f"\n📋 Endpoints:")
    print(f"   /              - Web player")
    print(f"   /playlist.m3u  - M3U playlist")
    print(f"   /status        - Status (JSON)")
    print(f"   /credentials   - Credentials (JSON)")
    print(f"   /refresh       - Refresh credentials")
    print(f"   /debug         - Debug info")
    print("="*70 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        if file_observer:
            file_observer.stop()
            file_observer.join()
        scheduler.shutdown()
        print("\n👋 Server stopped")
