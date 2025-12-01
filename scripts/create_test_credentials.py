"""Helper script to create a test credentials.json file"""
import json
from datetime import datetime

# You can manually enter credentials here if you have them
# Or run playwright_script.py to fetch new ones

credentials = {
    "email": "test@example.com",  # Replace with actual email
    "username": "TV-20606476456216",  # Replace with actual username
    "password": "471009765320",  # Replace with actual password
    "url": "http://trial.ifiesta.net",
    "last_update": datetime.now().isoformat(),
    "used": False
}

# Save to credentials.json
with open("credentials.json", "w", encoding="utf-8") as f:
    json.dump(credentials, f, indent=2)

print("✅ Created credentials.json file")
print(f"   Username: {credentials['username']}")
print(f"   Password: {credentials['password']}")
print("\n⚠️  Note: These are placeholder credentials.")
print("   To get real credentials, run: python playwright_script.py")
print("   (Make sure API quota is available or use manual mode)")

