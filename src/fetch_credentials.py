"""
Wrapper para buscar credenciais automaticamente
"""
import os
import sys
from playwright.sync_api import sync_playwright

# Adicionar diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.playwright_script import (
    gerar_email, 
    registar_e_extrair, 
    guardar_resultados, 
    delete_old_credentials,
    MANUAL_MODE
)


def fetch_credentials_automated() -> bool:
    """
    Busca credenciais IPTV automaticamente usando Playwright
    
    Returns:
        bool: True se as credenciais foram obtidas com sucesso, False caso contrário
    """
    try:
        # Delete old credentials first
        delete_old_credentials()
        
        # Generate email
        if MANUAL_MODE:
            print("⚠️  MANUAL MODE está ativado. Use API MODE para automação.")
            return False
        
        print("📧 Gerando email temporário...")
        email = gerar_email()
        
        if not email:
            print("❌ Falha ao gerar email")
            return False
        
        # Fetch credentials using Playwright
        print("🌐 Iniciando navegador...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
            page = context.new_page()
            
            try:
                print("🔐 Registrando e extraindo credenciais...")
                code, username, password = registar_e_extrair(page, email)
                
                if not username or not password or username.startswith("ERROR") or password.startswith("ERROR"):
                    print("❌ Falha ao extrair credenciais válidas")
                    browser.close()
                    return False
                
                # Save credentials
                guardar_resultados(email, code, username, password)
                print("✅ Credenciais salvas com sucesso!")
                
                browser.close()
                return True
                
            except Exception as e:
                print(f"❌ Erro durante a busca de credenciais: {e}")
                import traceback
                traceback.print_exc()
                browser.close()
                return False
                
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return False

