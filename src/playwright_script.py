import time
import http.client
import json
import re
import os
import sys
import argparse
import urllib.request
import urllib.error
import random
from playwright.sync_api import sync_playwright
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "registos_fiesta.txt")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "data", "credentials.json")

# Ensure data directory exists
os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)

# Configuration
MANUAL_MODE = True  # Set to True to manually enter email, False to use API


# API Configuration
RAPIDAPI_KEY = "f179a4e9dfmsh4031a8907ab8e64p172111jsnc505667cefae"
RAPIDAPI_HOST = "gmailnator.p.rapidapi.com"


def delete_old_credentials():
    """Delete old credentials file before fetching new ones"""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            os.remove(CREDENTIALS_FILE)
            print(f"Deleted old credentials file: {CREDENTIALS_FILE}")
        except Exception as e:
            print(f"Warning: Could not delete old credentials file: {e}")

def notify_server():
    """Notify the server that new credentials are available"""
    try:
        # Try to notify the server to refresh credentials
        url = "http://localhost:5000/refresh"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'playwright_script.py')
        
        try:
            with urllib.request.urlopen(req, timeout=2) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get('success'):
                    print("✅ Server notified successfully! Credentials are now available.")
                else:
                    print(f"⚠️ Server responded but refresh may have failed: {result.get('error', 'Unknown error')}")
        except urllib.error.URLError as e:
            # Server might not be running, that's okay
            print(f"ℹ️ Server not running or not accessible (this is okay if server isn't started yet): {e}")
        except Exception as e:
            print(f"⚠️ Could not notify server: {e}")
    except Exception as e:
        print(f"⚠️ Error notifying server: {e}")


def guardar_resultados(email, code, username, password):
    # Save to text file (original)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Email: {email}\n")
        f.write(f"Código: {code}\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {password}\n")
        f.write("URL: http://trial.ifiesta.net\n")
        f.write("-" * 50 + "\n\n")
    
    # Save to JSON for the server (new) - marked as unused initially
    try:
        from datetime import datetime
        import json
        
        data = {
            'email': email,
            'username': username,
            'password': password,
            'url': 'http://trial.ifiesta.net',
            'last_update': datetime.now().isoformat(),
            'used': False
        }
        
        with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("✅ Credentials saved to credentials.json for the server (marked as unused).")
        
        # Notify the server that new credentials are available
        print("\nNotifying server about new credentials...")
        notify_server()
        
    except Exception as e:
        print(f"Error saving JSON credentials: {e}")


def gerar_email():
    """Generate email using Emailnator API"""
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    
    payload = json.dumps({"options": [1, 2, 3]})
    
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST,
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


def obter_codigo(email):
    """Fetch verification code from email using Emailnator API"""
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST,
        'Content-Type': "application/json"
    }
    
    print("À espera do código...")
    
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
                print(f"Mensagem recebida! ID: {message_id}")
                break
        
        print(f"Tentativa {attempt + 1}/{max_attempts}...")
        time.sleep(3)
        attempt += 1
    
    if not message_id:
        raise Exception("Timeout: Não foi possível obter o código de verificação")
    
    # Fetch the message content
    conn.request("GET", f"/messageid?id={message_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    message_content = data.decode("utf-8")
    
    # Extract 6-digit code from message (look for 6 consecutive digits)
    code_match = re.search(r'\b(\d{6})\b', message_content)
    if code_match:
        code = code_match.group(1)
    else:
        # Fallback: get first 6 digits
        digits = re.findall(r'\d', message_content)
        code = "".join(digits[:6])
    
    print("CÓDIGO:", code)
    conn.close()
    return code


def obter_codigo_manual():
    """Manually enter verification code for testing"""
    print("\n" + "="*50)
    print("MANUAL MODE: Check your email inbox")
    print("="*50)
    
    while True:
        code = input("Enter the 6-digit verification code: ").strip()
        
        # Validate the code
        if len(code) == 6 and code.isdigit():
            print(f"Code entered: {code}")
            return code
        else:
            print("Invalid code! Please enter exactly 6 digits.")



def registar_e_extrair(page, email):
    """Register on the website and extract credentials"""
    print("Navigating to myfiestatrial.com...")
    
    # Add stealth measures - set realistic viewport and user agent
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    # Use a realistic user agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    ]
    import random
    user_agent = random.choice(user_agents)
    page.set_extra_http_headers({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    })
    
    # Clear cookies and storage first
    page.context.clear_cookies()
    
    # Navigate with realistic timing
    page.goto("https://myfiestatrial.com/", timeout=60000, wait_until="domcontentloaded")
    time.sleep(random.uniform(2, 4))  # Random delay to appear more human

    # Enter the email and submit with human-like behavior
    print(f"Entering email: {email}")
    page.screenshot(path="screenshot_before_email.png")
    
    # Wait for and fill email input with human-like typing
    email_input = page.wait_for_selector("input[placeholder='Enter your email']", timeout=10000)
    
    # Clear any existing content first
    email_input.click()
    time.sleep(random.uniform(0.3, 0.7))
    email_input.fill("")  # Clear
    time.sleep(random.uniform(0.2, 0.5))
    
    # Type email character by character to simulate human typing
    for char in email:
        email_input.type(char, delay=random.uniform(50, 150))
        time.sleep(random.uniform(0.05, 0.15))
    
    time.sleep(random.uniform(0.5, 1.0))  # Pause before clicking button
    print("Email entered successfully")
    
    # Click Generate Access button with human-like behavior
    print("Looking for Generate Access button...")
    page.screenshot(path="screenshot_before_click.png")
    
    # Move mouse to button area first (simulate human behavior)
    try:
        button = page.wait_for_selector("button:has-text('Generate Access')", timeout=5000)
        # Hover over button first
        button.hover()
        time.sleep(random.uniform(0.3, 0.7))
        # Click with slight delay
        button.click(delay=random.uniform(50, 150))
        print("Clicked 'Generate Access' button")
    except Exception as e:
        print(f"Failed with first selector: {e}")
        # Try alternative selector
        button = page.locator("button").filter(has_text="Generate Access").first
        button.hover()
        time.sleep(random.uniform(0.3, 0.7))
        button.click(delay=random.uniform(50, 150))
        print("Clicked button using alternative selector")
    
    # Random wait time to appear more human
    time.sleep(random.uniform(2.5, 4.0))
    page.screenshot(path="screenshot_after_click.png")

    # Wait for verification code input boxes to appear
    print("Waiting for verification code input boxes...")
    try:
        page.wait_for_selector("input[type='text']", timeout=15000)
        print("Verification code input boxes appeared, now fetching code from inbox...")
    except Exception as e:
        print(f"Error waiting for input boxes: {e}")
        page.screenshot(path="screenshot_error.png")
        print("Saved error screenshot. Trying alternative selectors...")
        # Try alternative selectors
        page.wait_for_selector("input", timeout=15000)
    
    
    # Now fetch the verification code from the inbox (API or manual mode)
    if MANUAL_MODE:
        print("MANUAL MODE: Waiting for you to enter the code...")
        code = obter_codigo_manual()
    else:
        print("API MODE: Fetching code from inbox...")
        code = obter_codigo(email)
    
    print(f"Entering verification code: {code}")
    
    # Enter the verification code - each digit in its own input box
    # First, let's find all the input boxes
    time.sleep(1)  # Give the page a moment to stabilize
    
    # Try to find the input boxes for the verification code
    input_boxes = page.locator("input[type='text']").all()
    
    if len(input_boxes) < 6:
        print(f"Warning: Found only {len(input_boxes)} input boxes, expected 6")
        # Try alternative selector
        input_boxes = page.locator("input").all()
        print(f"Found {len(input_boxes)} input boxes with alternative selector")
    
    # Ensure we have the code as a string with 6 digits
    if len(code) != 6:
        raise Exception(f"Invalid code length: {len(code)}, expected 6 digits")
    
    print(f"Found {len(input_boxes)} input boxes")
    
    # Fill each input box with one digit (human-like)
    for i in range(min(6, len(input_boxes))):
        digit = code[i]
        print(f"Entering digit {i+1}: {digit}")
        
        # Click to focus the input box first
        input_boxes[i].click()
        time.sleep(random.uniform(0.2, 0.4))
        
        # Clear any existing content
        input_boxes[i].fill("")
        time.sleep(random.uniform(0.1, 0.2))
        
        # Type the digit with random delay
        input_boxes[i].type(digit, delay=random.uniform(80, 150))
        time.sleep(random.uniform(0.2, 0.4))
    
    print("All digits entered successfully")
    time.sleep(1)  # Give the page time to process
    page.screenshot(path="screenshot_code_entered.png")

    # Click Validate button with human-like behavior
    print("Clicking Validate button...")
    try:
        validate_button = page.wait_for_selector("button:has-text('Validate')", timeout=5000)
        # Hover first, then click
        validate_button.hover()
        time.sleep(random.uniform(0.3, 0.6))
        validate_button.click(delay=random.uniform(50, 150))
        print("Validate button clicked")
    except Exception as e:
        print(f"Error clicking Validate button: {e}")
        page.screenshot(path="screenshot_validate_error.png")
        raise
    
    # Wait for page to respond after validation
    print("Waiting for page to load after validation...")
    print("This may take up to 90 seconds...")
    try:
        page.wait_for_load_state("networkidle", timeout=90000)  # Increased to 90 seconds
        time.sleep(3)  # Give extra time for credentials to appear
        page.screenshot(path="screenshot_after_validate.png")
        print("Page loaded successfully")
    except Exception as e:
        print(f"Timeout waiting for page load: {e}")
        page.screenshot(path="screenshot_timeout.png")
        print("Continuing anyway to try extracting credentials...")
        # Wait a bit more before trying to extract
        time.sleep(5)
    
    # Try to extract username and password
    print("Attempting to extract credentials...")
    
    # Take a screenshot first to see what we're working with
    page.screenshot(path="screenshot_before_extraction.png")
    
    username = None
    password = None
    
    # Try to extract username
    try:
        # Strategy 1: Try to find and click the username copy button
        print("Looking for username copy button...")
        print("Waiting up to 60 seconds for username to appear...")
        username_btn = page.locator("button:below(:text('Username'))").first
        username_btn.wait_for(timeout=60000)  # Increased to 60 seconds
        username_btn.click()
        time.sleep(2)  # Give clipboard more time to update
        username = page.evaluate("navigator.clipboard.readText()")
        print("USERNAME (from clipboard):", username)
    except Exception as e:
        print(f"Strategy 1 for username failed: {e}")
        # Strategy 2: Try to find username in page content
        try:
            print("Trying to extract username from page content...")
            # Look for text patterns that might contain username
            page_content = page.content()
            # Try to find username near "Username" label
            username_match = re.search(r'Username[:\s]+([^\s<]+)', page_content, re.IGNORECASE)
            if username_match:
                username = username_match.group(1).strip()
                print("USERNAME (from content):", username)
            else:
                # Try finding all buttons and their associated text
                username_elements = page.locator("text=/username/i").all()
                for elem in username_elements:
                    try:
                        parent = elem.locator("..")
                        # Look for input or text near username
                        nearby_text = parent.inner_text()
                        if nearby_text:
                            print(f"Found text near username: {nearby_text}")
                    except:
                        pass
        except Exception as e2:
            print(f"Strategy 2 for username failed: {e2}")
    
    if not username or username.startswith("ERROR"):
        print("Could not extract username, trying alternative methods...")
        page.screenshot(path="screenshot_username_error.png")
        # Try to find any copy buttons and click them to see what's in clipboard
        try:
            all_buttons = page.locator("button").all()
            print(f"Found {len(all_buttons)} buttons on page")
            for i, btn in enumerate(all_buttons):
                try:
                    btn_text = btn.inner_text(timeout=500)
                    is_visible = btn.is_visible()
                    print(f"Button {i}: '{btn_text}', visible={is_visible}")
                    # If button is near username text, try clicking it
                    if is_visible and (not btn_text or len(btn_text) < 5):
                        try:
                            btn.click()
                            time.sleep(0.5)
                            clipboard_text = page.evaluate("navigator.clipboard.readText()")
                            if clipboard_text and len(clipboard_text) > 3:
                                if not username:
                                    username = clipboard_text
                                    print(f"Found username from button {i}: {username}")
                                    break
                        except:
                            pass
                except:
                    pass
        except Exception as e:
            print(f"Alternative username extraction failed: {e}")
        
        if not username:
            username = "ERROR_EXTRACTING_USERNAME"
    
    try:
        # Try multiple strategies to find the password button
        password_btn = None
        password = None
        
        # Strategy 1: Original selector
        try:
            btn = page.locator("button:below(:text('Password'))").first
            btn.wait_for(timeout=3000, state="visible")
            password_btn = btn
            print("Found password button using strategy 1")
        except Exception as e:
            print(f"Strategy 1 failed: {str(e)[:100]}")
            password_btn = None
        
        # Strategy 2: Look for any button containing "Password" text
        if not password_btn:
            try:
                btn = page.locator("button:has-text('Password')").first
                btn.wait_for(timeout=3000, state="visible")
                password_btn = btn
                print("Found password button using strategy 2")
            except Exception as e:
                print(f"Strategy 2 failed: {str(e)[:100]}")
                password_btn = None
        
        # Strategy 3: Look for buttons near password text
        if not password_btn:
            try:
                btn = page.locator("text=Password").locator("..").locator("button").first
                btn.wait_for(timeout=3000, state="visible")
                password_btn = btn
                print("Found password button using strategy 3")
            except Exception as e:
                print(f"Strategy 3 failed: {str(e)[:100]}")
                password_btn = None
        
        # Strategy 4: Get all copy buttons on the page
        if not password_btn:
            try:
                # Take a screenshot to debug
                page.screenshot(path="screenshot_before_password_search.png")
                
                all_buttons = page.locator("button").all()
                print(f"Found {len(all_buttons)} total buttons on page")
                
                # Look for buttons that might be copy buttons (usually have icons)
                copy_buttons = []
                for i, btn in enumerate(all_buttons):
                    try:
                        text = btn.inner_text(timeout=1000)
                        is_visible = btn.is_visible()
                        print(f"Button {i}: text='{text}', visible={is_visible}")
                        
                        # If it's a visible button with no text or copy-like text
                        if is_visible and (not text or "copy" in text.lower() or len(text) < 3):
                            copy_buttons.append((i, btn))
                    except:
                        pass
                
                print(f"Found {len(copy_buttons)} potential copy buttons")
                
                # If we have at least 2 copy buttons, the second one is likely password
                if len(copy_buttons) >= 2:
                    password_btn = copy_buttons[1][1]  # Get the second copy button
                    print(f"Using button index {copy_buttons[1][0]} as password button")
                elif len(copy_buttons) == 1:
                    password_btn = copy_buttons[0][1]
                    print(f"Using button index {copy_buttons[0][0]} as password button")
                    
            except Exception as e:
                print(f"Strategy 4 failed: {e}")
                password_btn = None
        
        # If we found a button, click it
        if password_btn:
            print("Clicking password button...")
            password_btn.click(timeout=5000)
            time.sleep(1)  # Give clipboard more time to update
            try:
                password = page.evaluate("navigator.clipboard.readText()")
                print("PASSWORD (from clipboard):", password)
            except Exception as e:
                print(f"Failed to read from clipboard: {e}")
                password = None
        else:
            print("Could not find password button with any strategy")
            page.screenshot(path="screenshot_no_password_btn.png")
            password = None
        
        # Fallback: Try to extract password from page content or try all buttons
        if not password or password.startswith("ERROR"):
            print("Trying fallback methods to extract password...")
            try:
                # Try extracting from page content
                page_content = page.content()
                password_match = re.search(r'Password[:\s]+([^\s<]+)', page_content, re.IGNORECASE)
                if password_match:
                    password = password_match.group(1).strip()
                    print("PASSWORD (from content):", password)
                else:
                    # Try clicking all remaining copy buttons
                    all_buttons = page.locator("button").all()
                    print(f"Trying all {len(all_buttons)} buttons to find password...")
                    for i, btn in enumerate(all_buttons):
                        try:
                            btn_text = btn.inner_text(timeout=500)
                            is_visible = btn.is_visible()
                            if is_visible and (not btn_text or len(btn_text) < 5):
                                try:
                                    btn.click()
                                    time.sleep(0.5)
                                    clipboard_text = page.evaluate("navigator.clipboard.readText()")
                                    if clipboard_text and len(clipboard_text) > 3 and clipboard_text != username:
                                        password = clipboard_text
                                        print(f"Found password from button {i}: {password}")
                                        break
                                except:
                                    pass
                        except:
                            pass
            except Exception as e:
                print(f"Fallback password extraction failed: {e}")
            
            if not password or password.startswith("ERROR"):
                password = "ERROR_NO_PASSWORD_BUTTON_FOUND"
            
    except Exception as e:
        print(f"Error extracting password: {e}")
        page.screenshot(path="screenshot_password_error.png")
        password = "ERROR_EXTRACTING_PASSWORD"

    return code, username, password


# Main execution - only runs when script is executed directly
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Fetch MyFiesta IPTV credentials')
    parser.add_argument('--email', '-e', type=str, help='Email address to use for registration')
    args = parser.parse_args()

    # Always delete old credentials before running the script
    print("\n" + "="*60)
    print("DELETING OLD CREDENTIALS BEFORE FETCHING NEW ONES")
    print("="*60)
    delete_old_credentials()
    print("="*60 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Grant clipboard permissions for credential extraction
        context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = context.new_page()

        # Get email from command line or prompt
        if MANUAL_MODE:
            print("MANUAL MODE ENABLED")
            if args.email:
                email = args.email.strip()
                print(f"Using email from command line: {email}")
            else:
                email = input("Please enter the email you want to use: ").strip()
                while not email:
                    print("Email cannot be empty.")
                    email = input("Please enter the email you want to use: ").strip()
                print(f"Using email: {email}")
        else:
            print("API MODE: Generating email...")
            email = gerar_email()
        
        # Register and extract credentials (code fetching happens inside this function)
        code, username, password = registar_e_extrair(page, email)

        guardar_resultados(email, code, username, password)

        browser.close()
