"""Quick setup script - creates credentials.json from existing credentials or runs playwright script"""
import json
import os
import sys
from datetime import datetime

def create_credentials_file(username, password, email="manual@example.com"):
    """Create credentials.json file"""
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_file = os.path.join(BASE_DIR, "data", "credentials.json")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(credentials_file), exist_ok=True)
    
    credentials = {
        "email": email,
        "username": username,
        "password": password,
        "url": "http://trial.ifiesta.net",
        "last_update": datetime.now().isoformat(),
        "used": False
    }
    
    with open(credentials_file, "w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2)
    
    print("✅ Created credentials.json")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    return True

if __name__ == "__main__":
    print("="*60)
    print("QUICK SETUP - Create credentials.json")
    print("="*60)
    
    if len(sys.argv) >= 3:
        # Use command line arguments
        username = sys.argv[1]
        password = sys.argv[2]
        email = sys.argv[3] if len(sys.argv) > 3 else "manual@example.com"
        create_credentials_file(username, password, email)
    else:
        print("\nOption 1: Enter credentials manually")
        print("Option 2: Run playwright script to fetch new credentials")
        print("\nFor Option 1, run:")
        print("  python quick_setup.py <username> <password> [email]")
        print("\nFor Option 2, run:")
        print("  python playwright_script.py")
        print("  (It will prompt you for an email in manual mode)")
        print("\n" + "="*60)

