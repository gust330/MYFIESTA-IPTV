import time
from playwright.sync_api import sync_playwright

OUTPUT_FILE = "registos_fiesta.txt"


def guardar_resultados(email, code, username, password):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"Email: {email}\n")
        f.write(f"Código: {code}\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {password}\n")
        f.write("-" * 50 + "\n\n")


def gerar_email(page):
    page.goto("https://emailnator.com/")
    page.wait_for_load_state("networkidle")

    page.click("text=Single-use Domains")
    page.check("input[value='gmail.com']")

    page.click("button:has-text('Generate')")
    page.wait_for_timeout(1800)

    email = page.input_value("#email")
    print("EMAIL GERADO:", email)
    return email


def obter_codigo(page):
    page.click("text=Inbox")

    while True:
        try:
            page.wait_for_selector("tbody tr", timeout=3500)
            break
        except:
            print("À espera do código...")
            page.click("text=Refresh")
            time.sleep(2)

    page.click("tbody tr")

    page.wait_for_selector("iframe")
    frame = page.frame_locator("iframe").frame()

    body_text = frame.locator("body").text_content()
    digits = [c for c in body_text if c.isdigit()]
    code = "".join(digits[:6])

    print("CÓDIGO:", code)
    return code


def registar_e_extrair(page, email, code):
    page.goto("https://myfiestatrial.com/")
    page.wait_for_load_state("networkidle")

    page.fill("input[placeholder='Enter your email']", email)
    page.click("button:has-text('Generate Access')")

    page.wait_for_selector("input[type='text']")
    caixas = page.locator("input[type='text']")

    for i, digito in enumerate(code):
        caixas.nth(i).fill(digito)

    page.click("button:has-text('Validate')")
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    username_btn = page.locator("button:below(:text('Username'))")
    username_btn.click()
    username = page.evaluate("navigator.clipboard.readText()")

    password_btn = page.locator("button:below(:text('Password'))")
    password_btn.click()
    password = page.evaluate("navigator.clipboard.readText()")

    print("USERNAME:", username)
    print("PASSWORD:", password)

    return username, password


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    email = gerar_email(page)
    code = obter_codigo(page)
    username, password = registar_e_extrair(page, email, code)

    guardar_resultados(email, code, username, password)

    browser.close()
