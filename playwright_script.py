import time
import http.client
import json
import re
from playwright.sync_api import sync_playwright

OUTPUT_FILE = "registos_fiesta.txt"

# Configuration
MANUAL_MODE = False  # Set to True to manually enter email, False to use API


# API Configuration
RAPIDAPI_KEY = "f179a4e9dfmsh4031a8907ab8e64p172111jsnc505667cefae"
RAPIDAPI_HOST = "gmailnator.p.rapidapi.com"


def guardar_resultados(email, code, username, password):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Email: {email}\n")
        f.write(f"Código: {code}\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {password}\n")
        f.write("URL: http://trial.ifiesta.net\n")
        f.write("-" * 50 + "\n\n")


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
    page.goto("https://myfiestatrial.com/", timeout=60000)
    page.wait_for_load_state("load", timeout=60000)
    time.sleep(2)  # Give page time to fully render

    # Enter the email and submit
    print(f"Entering email: {email}")
    page.screenshot(path="screenshot_before_email.png")
    
    # Wait for and fill email input
    email_input = page.wait_for_selector("input[placeholder='Enter your email']", timeout=10000)
    email_input.fill(email)
    print("Email entered successfully")
    
    # Click Generate Access button
    print("Looking for Generate Access button...")
    page.screenshot(path="screenshot_before_click.png")
    
    # Try different selectors for the button
    try:
        button = page.wait_for_selector("button:has-text('Generate Access')", timeout=5000)
        button.click()
        print("Clicked 'Generate Access' button")
    except Exception as e:
        print(f"Failed with first selector: {e}")
        # Try alternative selector
        button = page.locator("button").filter(has_text="Generate Access").first
        button.click()
        print("Clicked button using alternative selector")
    
    time.sleep(3)  # Wait for page to respond
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
    
    # Fill each input box with one digit
    for i in range(min(6, len(input_boxes))):
        digit = code[i]
        print(f"Entering digit {i+1}: {digit}")
        
        # Click to focus the input box first
        input_boxes[i].click()
        time.sleep(0.2)
        
        # Clear any existing content
        input_boxes[i].fill("")
        
        # Type the digit
        input_boxes[i].type(digit, delay=100)
        time.sleep(0.3)
    
    print("All digits entered successfully")
    time.sleep(1)  # Give the page time to process
    page.screenshot(path="screenshot_code_entered.png")

    # Click Validate button
    print("Clicking Validate button...")
    try:
        page.click("button:has-text('Validate')", timeout=5000)
        print("Validate button clicked")
    except Exception as e:
        print(f"Error clicking Validate button: {e}")
        page.screenshot(path="screenshot_validate_error.png")
        raise
    
    # Wait for page to respond after validation
    print("Waiting for page to load after validation...")
    try:
        page.wait_for_load_state("networkidle", timeout=45000)
        time.sleep(2)
        page.screenshot(path="screenshot_after_validate.png")
        print("Page loaded successfully")
    except Exception as e:
        print(f"Timeout waiting for page load: {e}")
        page.screenshot(path="screenshot_timeout.png")
        print("Continuing anyway to try extracting credentials...")
    
    # Try to extract username and password
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
        page.screenshot(path="screenshot_username_error.png")
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
            time.sleep(0.5)
            password = page.evaluate("navigator.clipboard.readText()")
            print("PASSWORD:", password)
        else:
            print("Could not find password button with any strategy")
            page.screenshot(path="screenshot_no_password_btn.png")
            password = "ERROR_NO_PASSWORD_BUTTON_FOUND"
            
    except Exception as e:
        print(f"Error extracting password: {e}")
        page.screenshot(path="screenshot_password_error.png")
        password = "ERROR_EXTRACTING_PASSWORD"

    return code, username, password


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Generate email first
    if MANUAL_MODE:
        print("MANUAL MODE ENABLED")
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
