"""
MyFiesta IPTV - Main Launcher
Automatically fetches credentials and starts the server in one go
"""
import os
import sys
import time
import json
from datetime import datetime

# Import server components
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from server import (
    app, load_credentials_from_file, credential_manager, status,
    setup_file_monitoring, scheduler, reset_status, CREDENTIALS_FILE
)

def check_dependencies():
    """Check if required packages are installed"""
    required = {
        'flask': 'Flask',
        'playwright': 'playwright',
        'apscheduler': 'APScheduler'
    }
    missing = []
    
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        if 'playwright' in missing:
            print("   Then run: playwright install chromium")
        return False
    
    return True

def fetch_credentials_integrated():
    """Fetch credentials by running the playwright script functions"""
    print("\n" + "="*70)
    print("STEP 1: FETCHING CREDENTIALS")
    print("="*70)
    
    # Check if valid credentials already exist
    if os.path.exists(CREDENTIALS_FILE):
        try:
            if load_credentials_from_file():
                if credential_manager.credentials and not credential_manager.is_used():
                    print("✅ Valid credentials already exist!")
                    print(f"   Username: {credential_manager.credentials['username']}")
                    print(f"   Last Update: {credential_manager.last_update}")
                    return True
        except Exception as e:
            print(f"⚠️  Existing credentials invalid: {e}")
    
    # Import playwright script components
    import playwright_script
    
    print("Starting credential fetch process...")
    print("(This may take 2-5 minutes)")
    print("-" * 70)
    
    try:
        # Delete old credentials first (as the script does)
        if os.path.exists(CREDENTIALS_FILE):
            try:
                os.remove(CREDENTIALS_FILE)
                print("🗑️  Deleted old credentials file")
            except Exception as e:
                print(f"⚠️  Could not delete old file: {e}")
        
        # Run the main playwright script logic
        # We'll execute it by importing and calling the main flow
        from playwright.sync_api import sync_playwright
        
        # Get email (manual mode)
        MANUAL_MODE = getattr(playwright_script, 'MANUAL_MODE', True)
        
        if MANUAL_MODE:
            print("\n📧 MANUAL MODE: Email required")
            email = input("Enter your email address: ").strip()
            while not email:
                print("Email cannot be empty.")
                email = input("Enter your email address: ").strip()
        else:
            print("📧 API MODE: Generating email...")
            email = playwright_script.gerar_email()
        
        print(f"\n✅ Using email: {email}")
        print("⏳ Starting browser automation...")
        
        # Run the registration and extraction
        with sync_playwright() as p:
            # Launch browser with stealth settings
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials'
                ]
            )
            
            # Create context with realistic settings
            context = browser.new_context(
                permissions=["clipboard-read", "clipboard-write", "geolocation"],
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US",
                timezone_id="America/New_York",
                geolocation={"latitude": 40.7128, "longitude": -74.0060}
            )
            
            # Add script to hide webdriver property
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Mock chrome object
                window.chrome = {
                    runtime: {}
                };
            """)
            
            page = context.new_page()
            
            # Register and extract credentials
            # This function handles code fetching internally (manual or API mode)
            code, username, password = playwright_script.registar_e_extrair(page, email)
            
            browser.close()
        
        # Save credentials
        if username and password and not username.startswith("ERROR") and not password.startswith("ERROR"):
            playwright_script.guardar_resultados(email, code, username, password)
            
            # Wait a moment for file to be written
            time.sleep(1)
            
            # Verify credentials were saved
            if os.path.exists(CREDENTIALS_FILE):
                if load_credentials_from_file():
                    print("\n✅ Credentials fetched and saved successfully!")
                    print(f"   Username: {username}")
                    print(f"   Password: {password}")
                    return True
                else:
                    print("\n❌ Credentials file created but failed to load")
                    return False
            else:
                print("\n❌ Credentials file was not created")
                return False
        else:
            print("\n❌ Failed to extract valid credentials")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during credential fetch: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_server_integrated():
    """Start the Flask server with proper initialization"""
    print("\n" + "="*70)
    print("STEP 2: STARTING SERVER")
    print("="*70)
    
    # Reset status
    reset_status()
    
    # Load credentials
    print("\n[STARTUP] Loading credentials...")
    if not load_credentials_from_file():
        print("❌ Cannot start server: No valid credentials")
        return False
    
    # Setup file monitoring
    setup_file_monitoring()
    
    # Schedule periodic refresh
    scheduler.add_job(
        func=load_credentials_from_file,
        trigger='interval',
        hours=47,  # Refresh 1 hour before 48h expiry
        id='periodic_refresh',
        replace_existing=True
    )
    
    scheduler.start()
    
    print("\n" + "="*70)
    print("✅ SERVER READY")
    print("="*70)
    print("🌐 Access the web player at:")
    print("   Local:    http://localhost:5000")
    print("   Network:  http://<your-ip>:5000")
    print("\n📋 Available endpoints:")
    print("   /              - Web player interface")
    print("   /playlist.m3u  - M3U playlist file")
    print("   /status        - Server status (JSON)")
    print("   /credentials   - Current credentials (JSON)")
    print("   /refresh       - Refresh credentials")
    print("="*70)
    print("\n💡 Press Ctrl+C to stop the server\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        return True
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point - does everything in one go"""
    print("\n" + "="*70)
    print("🎬 MYFIESTA IPTV - AUTOMATED LAUNCHER")
    print("="*70)
    print("This script will:")
    print("  1. Fetch credentials automatically")
    print("  2. Start the web server")
    print("  3. Make everything available at http://localhost:5000")
    print("="*70)
    
    # Check dependencies
    print("\n[CHECK] Verifying dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        sys.exit(1)
    print("✅ All dependencies installed")
    
    # Fetch credentials
    if not fetch_credentials_integrated():
        print("\n" + "="*70)
        print("❌ FAILED TO FETCH CREDENTIALS")
        print("="*70)
        print("\nPossible reasons:")
        print("  • Internet connection issues")
        print("  • API quota exceeded (use manual mode)")
        print("  • Website structure changed")
        print("  • Browser automation failed")
        print("\nYou can try:")
        print("  • Run playwright_script.py manually to debug")
        print("  • Check your internet connection")
        print("  • Wait and try again later")
        sys.exit(1)
    
    # Start server
    start_server_integrated()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
