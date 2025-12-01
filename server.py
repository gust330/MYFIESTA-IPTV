from flask import Flask, Response, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from credential_manager import CredentialManager
from datetime import datetime, timedelta
import os
import threading

app = Flask(__name__)

# Global credential manager
credential_manager = CredentialManager(manual_mode=True)
scheduler = BackgroundScheduler()
refresh_lock = threading.Lock()

# Status tracking
status = {
    'last_refresh': None,
    'next_refresh': None,
    'status': 'initializing',
    'error': None
}


def refresh_credentials():
    """Background task to refresh credentials"""
    global status
    
    with refresh_lock:
        try:
            print("\n" + "="*60)
            print(f"SCHEDULED REFRESH - {datetime.now()}")
            print("="*60)
            
            status['status'] = 'refreshing'
            status['error'] = None
            
            # Fetch new credentials
            credential_manager.fetch_credentials()
            
            # Save credentials
            credential_manager.save_credentials()
            
            # Update status
            status['last_refresh'] = datetime.now()
            status['next_refresh'] = datetime.now() + timedelta(hours=48)
            status['status'] = 'active'
            
            print(f"Next refresh scheduled for: {status['next_refresh']}")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"ERROR during credential refresh: {e}")
            status['status'] = 'error'
            status['error'] = str(e)


def initialize_credentials():
    """Initialize credentials on startup"""
    global status
    
    print("Initializing credentials...")
    
    # Try to load existing credentials
    loaded = credential_manager.load_credentials()
    
    if loaded:
        print("Loaded existing credentials")
        
        # Check if credentials are still valid (less than 48 hours old)
        if credential_manager.last_update:
            age = datetime.now() - credential_manager.last_update
            if age < timedelta(hours=48):
                print(f"Credentials are still valid (age: {age})")
                status['last_refresh'] = credential_manager.last_update
                status['next_refresh'] = credential_manager.last_update + timedelta(hours=48)
                status['status'] = 'active'
                return
            else:
                print(f"Credentials are expired (age: {age}), fetching new ones...")
        else:
            print("No timestamp found, fetching new credentials...")
    else:
        print("No existing credentials found, fetching new ones...")
    
    # Fetch new credentials
    refresh_credentials()


@app.route('/')
def index():
    """Main page with player and status"""
    return render_template('index.html')


@app.route('/playlist.m3u')
def playlist():
    """Serve the M3U playlist"""
    try:
        if not credential_manager.credentials:
            return Response("Credentials not available yet. Please wait...", 
                          status=503, 
                          mimetype='text/plain')
        
        m3u_content = credential_manager.generate_m3u_playlist()
        
        return Response(m3u_content, 
                       mimetype='application/x-mpegurl',
                       headers={
                           'Content-Disposition': 'attachment; filename=playlist.m3u',
                           'Cache-Control': 'no-cache'
                       })
    except Exception as e:
        return Response(f"Error generating playlist: {e}", 
                       status=500, 
                       mimetype='text/plain')


@app.route('/status')
def get_status():
    """Get current status as JSON"""
    return jsonify({
        'status': status['status'],
        'last_refresh': status['last_refresh'].isoformat() if status['last_refresh'] else None,
        'next_refresh': status['next_refresh'].isoformat() if status['next_refresh'] else None,
        'error': status['error'],
        'credentials_available': credential_manager.credentials is not None
    })


@app.route('/credentials')
def get_credentials():
    """Get current credentials (for debugging)"""
    if not credential_manager.credentials:
        return jsonify({'error': 'No credentials available'}), 503
    
    return jsonify({
        'username': credential_manager.credentials['username'],
        'password': credential_manager.credentials['password'],
        'url': credential_manager.credentials['url'],
        'last_update': credential_manager.last_update.isoformat() if credential_manager.last_update else None
    })


@app.route('/refresh')
def manual_refresh():
    """Manually trigger credential refresh"""
    try:
        refresh_credentials()
        return jsonify({'success': True, 'message': 'Credentials refreshed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Initialize credentials on startup
    initialize_credentials()
    
    # Schedule automatic refresh every 48 hours (using 47 hours to be safe)
    scheduler.add_job(
        func=refresh_credentials,
        trigger='interval',
        hours=47,
        id='credential_refresh',
        name='Refresh IPTV credentials every 47 hours',
        replace_existing=True
    )
    
    scheduler.start()
    
    print("\n" + "="*60)
    print("SERVER STARTING")
    print("="*60)
    print("Access the server at:")
    print("  - Local: http://localhost:5000")
    print("  - Network: http://<your-ip>:5000")
    print("\nEndpoints:")
    print("  - /              - Web player interface")
    print("  - /playlist.m3u  - M3U playlist file")
    print("  - /status        - Server status (JSON)")
    print("  - /credentials   - Current credentials (JSON)")
    print("  - /refresh       - Manual refresh trigger")
    print("="*60 + "\n")
    
    try:
        # Run Flask app
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\nServer stopped")
