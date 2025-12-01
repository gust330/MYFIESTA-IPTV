import time
import http.client
import json
import re
import os
from playwright.sync_api import sync_playwright
from datetime import datetime


class CredentialManager:
    """Manages IPTV credentials from myfiestatrial.com"""
    
    def __init__(self, rapidapi_key=None, manual_mode=False):
        self.manual_mode = manual_mode
        self.rapidapi_key = rapidapi_key or "f179a4e9dfmsh4031a8907ab8e64p172111jsnc505667cefae"
        self.rapidapi_host = "gmailnator.p.rapidapi.com"
        self.credentials = None
        self.last_update = None
        self.used = False
        
    def generate_email(self):
        """Generate email using Emailnator API"""
        conn = http.client.HTTPSConnection(self.rapidapi_host)
        
        payload = json.dumps({"options": [1, 2, 3]})
        
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.rapidapi_host,
            'Content-Type': "application/json"
        }
        
        conn.request("POST", "/generate-email", payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        response = json.loads(data.decode("utf-8"))
        print("DEBUG - API Response:", response)
        
        # Try to extract email from response
        email = None
        if isinstance(response.get("email"), list):
            email = response.get("email", [None])[0]
        elif isinstance(response.get("email"), str):
            email = response.get("email")
        
        if not email:
            raise Exception(f"Failed to generate email. API Response: {response}")
        
        print("EMAIL GERADO:", email)
        conn.close()
        return email
    
    def get_verification_code(self, email):
        """Fetch verification code from email using Emailnator API"""
        conn = http.client.HTTPSConnection(self.rapidapi_host)
        
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.rapidapi_host,
            'Content-Type': "application/json"
        }
        
        print("Waiting for verification code...")
        
        # Poll inbox until we get a message
        message_id = None
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            payload = json.dumps({"email": email, "limit": 10})
            
            conn.request("POST", "/inbox", payload, headers)
            res = conn.getresponse()
            data = res.read()
            
            inbox_response = json.loads(data.decode("utf-8"))
            
            # Check if we have messages
            if inbox_response and len(inbox_response) > 0:
                message_id = inbox_response[0].get("messageID")
                if message_id:
                    print(f"Message received! ID: {message_id}")
                    break
            
            print(f"Attempt {attempt + 1}/{max_attempts}...")
            time.sleep(3)
            attempt += 1
        
        if not message_id:
            raise Exception("Timeout: Could not get verification code")
        
        # Fetch the message content
        conn.request("GET", f"/messageid?id={message_id}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        message_content = data.decode("utf-8")
        
        # Extract 6-digit code from message
        code_match = re.search(r'\b(\d{6})\b', message_content)
        if code_match:
            code = code_match.group(1)
        else:
            # Fallback: get first 6 digits
            digits = re.findall(r'\d', message_content)
            code = "".join(digits[:6])
        
        print("CODE:", code)
        conn.close()
        return code
    
    def get_manual_code(self):
        """Manually enter verification code"""
        print("\n" + "="*50)
        print("MANUAL MODE: Check your email inbox")
        print("="*50)
        
        while True:
            code = input("Enter the 6-digit verification code: ").strip()
            
            if len(code) == 6 and code.isdigit():
                print(f"Code entered: {code}")
                return code
            else:
                print("Invalid code! Please enter exactly 6 digits.")
    
    def register_and_extract(self, page, email):
        """Register on the website and extract credentials"""
        print("Navigating to myfiestatrial.com...")
        page.goto("https://myfiestatrial.com/", timeout=60000)
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(2)
        
        # Enter the email and submit
        print(f"Entering email: {email}")
        email_input = page.wait_for_selector("input[placeholder='Enter your email']", timeout=10000)
        email_input.fill(email)
        print("Email entered successfully")
        
        # Click Generate Access button
        print("Looking for Generate Access button...")
        try:
            button = page.wait_for_selector("button:has-text('Generate Access')", timeout=5000)
            button.click()
            print("Clicked 'Generate Access' button")
        except Exception as e:
            print(f"Failed with first selector: {e}")
            button = page.locator("button").filter(has_text="Generate Access").first
            button.click()
            print("Clicked button using alternative selector")
        
        time.sleep(3)
        
        # Wait for verification code input boxes
        print("Waiting for verification code input boxes...")
        try:
            page.wait_for_selector("input[type='text']", timeout=15000)
            print("Verification code input boxes appeared")
        except Exception as e:
            print(f"Error waiting for input boxes: {e}")
            page.wait_for_selector("input", timeout=15000)
        
        # Get verification code
        if self.manual_mode:
            print("MANUAL MODE: Waiting for you to enter the code...")
            code = self.get_manual_code()
        else:
            print("API MODE: Fetching code from inbox...")
            code = self.get_verification_code(email)
        
        print(f"Entering verification code: {code}")
        
        # Enter the verification code
        time.sleep(1)
        input_boxes = page.locator("input[type='text']").all()
        
        if len(input_boxes) < 6:
            print(f"Warning: Found only {len(input_boxes)} input boxes, expected 6")
            input_boxes = page.locator("input").all()
            print(f"Found {len(input_boxes)} input boxes with alternative selector")
        
        if len(code) != 6:
            raise Exception(f"Invalid code length: {len(code)}, expected 6 digits")
        
        print(f"Found {len(input_boxes)} input boxes")
        
        # Fill each input box with one digit
        for i in range(min(6, len(input_boxes))):
            digit = code[i]
            print(f"Entering digit {i+1}: {digit}")
            input_boxes[i].click()
            time.sleep(0.2)
            input_boxes[i].fill("")
            input_boxes[i].type(digit, delay=100)
            time.sleep(0.3)
        
        print("All digits entered successfully")
        time.sleep(1)
        
        # Click Validate button
        print("Clicking Validate button...")
        try:
            page.click("button:has-text('Validate')", timeout=5000)
            print("Validate button clicked")
        except Exception as e:
            print(f"Error clicking Validate button: {e}")
            raise
        
        # Wait for page to respond
        print("Waiting for page to load after validation...")
        try:
            page.wait_for_load_state("networkidle", timeout=45000)
            time.sleep(2)
            print("Page loaded successfully")
        except Exception as e:
            print(f"Timeout waiting for page load: {e}")
            print("Continuing anyway to try extracting credentials...")
        
        # Extract username
        print("Attempting to extract credentials...")
        try:
            username_btn = page.locator("button:below(:text('Username'))").first
            username_btn.wait_for(timeout=10000)
            username_btn.click()
            time.sleep(0.5)
            username = page.evaluate("navigator.clipboard.readText()")
            print("USERNAME:", username)
        except Exception as e:
            print(f"Error extracting username: {e}")
            username = "ERROR_EXTRACTING_USERNAME"
        
        # Extract password
        try:
            password_btn = None
            password = None
            
            # Try multiple strategies
            strategies = [
                lambda: page.locator("button:below(:text('Password'))").first,
                lambda: page.locator("button:has-text('Password')").first,
                lambda: page.locator("text=Password").locator("..").locator("button").first,
            ]
            
            for i, strategy in enumerate(strategies):
                try:
                    btn = strategy()
                    btn.wait_for(timeout=3000, state="visible")
                    password_btn = btn
                    print(f"Found password button using strategy {i+1}")
                    break
                except Exception as e:
                    print(f"Strategy {i+1} failed: {str(e)[:100]}")
            
            # Fallback: find all copy buttons
            if not password_btn:
                all_buttons = page.locator("button").all()
                print(f"Found {len(all_buttons)} total buttons on page")
                
                copy_buttons = []
                for i, btn in enumerate(all_buttons):
                    try:
                        text = btn.inner_text(timeout=1000)
                        is_visible = btn.is_visible()
                        
                        if is_visible and (not text or "copy" in text.lower() or len(text) < 3):
                            copy_buttons.append((i, btn))
                    except:
                        pass
                
                print(f"Found {len(copy_buttons)} potential copy buttons")
                
                if len(copy_buttons) >= 2:
                    password_btn = copy_buttons[1][1]
                    print(f"Using button index {copy_buttons[1][0]} as password button")
                elif len(copy_buttons) == 1:
                    password_btn = copy_buttons[0][1]
                    print(f"Using button index {copy_buttons[0][0]} as password button")
            
            # Click password button
            if password_btn:
                print("Clicking password button...")
                password_btn.click(timeout=5000)
                time.sleep(0.5)
                password = page.evaluate("navigator.clipboard.readText()")
                print("PASSWORD:", password)
            else:
                print("Could not find password button with any strategy")
                password = "ERROR_NO_PASSWORD_BUTTON_FOUND"
                
        except Exception as e:
            print(f"Error extracting password: {e}")
            password = "ERROR_EXTRACTING_PASSWORD"
        
        return username, password
    
    def delete_old_credentials(self, filepath=None):
        """Delete old credentials file before fetching new ones"""
        if filepath is None:
            import os
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(BASE_DIR, "data", "credentials.json")
        """Delete old credentials file before fetching new ones"""
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Deleted old credentials file: {filepath}")
            except Exception as e:
                print(f"Warning: Could not delete old credentials file: {e}")
    
    def mark_as_used(self):
        """Mark current credentials as used (one-time use)"""
        self.used = True
        if self.credentials:
            self.credentials['used'] = True
            print("Credentials marked as USED (one-time use)")
    
    def is_used(self):
        """Check if credentials have been used"""
        return self.used or (self.credentials and self.credentials.get('used', False))
    
    def fetch_credentials(self):
        """Main method to fetch new credentials - always deletes old ones first"""
        print("\n" + "="*60)
        print("FETCHING NEW CREDENTIALS")
        print("="*60)
        
        # Always delete old credentials before fetching new ones
        self.delete_old_credentials()
        self.credentials = None
        self.last_update = None
        self.used = False
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Grant clipboard permissions
            context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
            page = context.new_page()
            
            # Generate or get email
            if self.manual_mode:
                print("MANUAL MODE ENABLED")
                email = input("Please enter the email you want to use: ").strip()
                while not email:
                    print("Email cannot be empty.")
                    email = input("Please enter the email you want to use: ").strip()
                print(f"Using email: {email}")
            else:
                print("API MODE: Generating email...")
                email = self.generate_email()
            
            # Register and extract credentials
            username, password = self.register_and_extract(page, email)
            
            browser.close()
        
        # Store credentials (marked as unused initially)
        self.credentials = {
            'email': email,
            'username': username,
            'password': password,
            'url': 'http://trial.ifiesta.net',
            'used': False
        }
        self.last_update = datetime.now()
        self.used = False
        
        print("\n" + "="*60)
        print("CREDENTIALS FETCHED SUCCESSFULLY")
        print("="*60)
        print(f"Email: {email}")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"URL: {self.credentials['url']}")
        print(f"Last Update: {self.last_update}")
        print("="*60 + "\n")
        
        return self.credentials
    
    def generate_m3u_playlist(self):
        """Generate M3U playlist from current credentials (marks them as used)"""
        if not self.credentials:
            raise Exception("No credentials available. Call fetch_credentials() first.")
        
        # Mark credentials as used when generating playlist (one-time use)
        if not self.is_used():
            self.mark_as_used()
            self.save_credentials()  # Save the used flag
        
        username = self.credentials['username']
        password = self.credentials['password']
        url = self.credentials['url']
        
        # M3U playlist format for Xtream Codes
        # Use m3u8 output for HLS streams (better browser compatibility)
        # The URL format is: http://server:port/get.php?username=XXX&password=YYY&type=m3u_plus&output=m3u8
        playlist_url = f"{url}/get.php?username={username}&password={password}&type=m3u_plus&output=m3u8"
        
        # Try to fetch the actual M3U content from the API
        try:
            import urllib.request
            import urllib.error
            
            print(f"Fetching full channel list from: {playlist_url}")
            req = urllib.request.Request(playlist_url)
            req.add_header('User-Agent', 'MyFiesta-IPTV/1.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                m3u_content = response.read().decode('utf-8')
                print(f"✅ Fetched {len(m3u_content)} bytes of playlist data")
                return m3u_content
        except Exception as e:
            print(f"⚠️  Could not fetch full playlist: {e}")
            print("   Returning direct URL instead")
            # Fallback to direct URL
            m3u_content = f"""#EXTM3U
#EXTINF:-1,MyFiesta IPTV Stream
{playlist_url}
"""
            return m3u_content
    
    def save_credentials(self, filepath=None):
        """Save credentials to JSON file"""
        if filepath is None:
            import os
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(BASE_DIR, "data", "credentials.json")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        """Save credentials to JSON file"""
        if not self.credentials:
            raise Exception("No credentials to save")
        
        data = {
            **self.credentials,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Credentials saved to {filepath}")
    
    def load_credentials(self, filepath=None):
        """Load credentials from JSON file"""
        if filepath is None:
            import os
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(BASE_DIR, "data", "credentials.json")
        """Load credentials from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required fields
            required_fields = ['email', 'username', 'password', 'url']
            for field in required_fields:
                if field not in data:
                    print(f"Error: Missing required field '{field}' in {filepath}")
                    return None
            
            self.credentials = {
                'email': data['email'],
                'username': data['username'],
                'password': data['password'],
                'url': data['url'],
                'used': data.get('used', False)
            }
            
            if data.get('last_update'):
                try:
                    self.last_update = datetime.fromisoformat(data['last_update'])
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Could not parse last_update timestamp: {e}")
                    self.last_update = datetime.now()
            else:
                self.last_update = datetime.now()
            
            self.used = data.get('used', False)
            
            # If credentials are already used, we still return them but warn
            # The server will handle fetching new ones if needed
            if self.used:
                print(f"⚠️  Warning: Credentials in {filepath} are marked as USED.")
                print(f"   They may still work, but you might want to fetch new ones.")
                # Don't delete - let the user decide
                # return None
            
            print(f"Credentials loaded from {filepath}")
            print(f"  Username: {self.credentials['username']}")
            print(f"  Password: {self.credentials['password']}")
            print(f"  URL: {self.credentials['url']}")
            print(f"  Used: {self.used}")
            return self.credentials
        except FileNotFoundError:
            print(f"No credentials file found at {filepath}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {filepath}: {e}")
            return None
        except Exception as e:
            print(f"Error loading credentials from {filepath}: {e}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == "__main__":
    # Test the credential manager
    manager = CredentialManager(manual_mode=False)
    credentials = manager.fetch_credentials()
    
    # Save credentials
    manager.save_credentials()
    
    # Generate M3U playlist
    m3u_content = manager.generate_m3u_playlist()
    
    # Save playlist
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print("\nPlaylist saved to playlist.m3u")
