"""Quick test script to verify server is working"""
import requests
import json

base_url = "http://localhost:5000"

print("Testing server endpoints...\n")

# Test status
print("1. Testing /status endpoint...")
try:
    response = requests.get(f"{base_url}/status", timeout=5)
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    print(f"   ✅ Status endpoint works")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Testing /debug endpoint...")
try:
    response = requests.get(f"{base_url}/debug", timeout=5)
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2, default=str)}")
    print(f"   ✅ Debug endpoint works")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n3. Testing /refresh endpoint...")
try:
    response = requests.get(f"{base_url}/refresh", timeout=5)
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    print(f"   ✅ Refresh endpoint works")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n4. Testing /credentials endpoint...")
try:
    response = requests.get(f"{base_url}/credentials", timeout=5)
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    print(f"   ✅ Credentials endpoint works")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n5. Testing /playlist.m3u endpoint...")
try:
    response = requests.get(f"{base_url}/playlist.m3u", timeout=5)
    print(f"   Status Code: {response.status_code}")
    print(f"   Content preview: {response.text[:200]}")
    print(f"   ✅ Playlist endpoint works")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("Test complete!")

