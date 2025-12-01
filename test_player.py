"""
TEST SCRIPT - Manual credential input for testing web player
This is ONLY for testing - does not affect the main code
"""
import json
import os
from datetime import datetime

# Get credentials from user
print("="*70)
print("TEST MODE - Manual Credential Input")
print("="*70)
print("Enter credentials manually to test the web player:")
print()

username = input("Username: ").strip()
password = input("Password: ").strip()
email = input("Email (optional): ").strip() or "test@example.com"
url = input("URL (default: http://trial.ifiesta.net): ").strip() or "http://trial.ifiesta.net"

# Create credentials file in data directory
os.makedirs("data", exist_ok=True)
credentials_file = os.path.join("data", "credentials.json")

credentials = {
    "email": email,
    "username": username,
    "password": password,
    "url": url,
    "last_update": datetime.now().isoformat(),
    "used": False
}

# Save to file
with open(credentials_file, "w", encoding="utf-8") as f:
    json.dump(credentials, f, indent=2)

print()
print("✅ Credentials saved to:", credentials_file)
print()
print("Now you can:")
print("  1. Start the server: python main.py")
print("  2. Or if server is running, click 'Refresh Now' in the web interface")
print("  3. Open http://localhost:5000 to test the web player")
print()
print("="*70)

