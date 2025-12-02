"""
Script de configuração de email
"""
import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "data", "email_config.json")


def setup_email():
    """Configurar email interativamente"""
    print("\n" + "="*70)
    print("📧 CONFIGURAÇÃO DE EMAIL")
    print("="*70)
    print("\nEste script vai configurar o envio de emails com links M3U.\n")
    
    # Verificar se já existe configuração
    if os.path.exists(CONFIG_FILE):
        print("⚠️  Já existe uma configuração de email.")
        resposta = input("Deseja sobrescrever? (s/N): ").strip().lower()
        if resposta != 's':
            print("❌ Configuração cancelada")
            return
    
    print("\n📋 Por favor, forneça as seguintes informações:\n")
    
    # SMTP Server
    print("1. Servidor SMTP:")
    print("   Gmail: smtp.gmail.com")
    print("   Outlook: smtp-mail.outlook.com")
    print("   Outro: (digite o servidor)")
    smtp_server = input("   Servidor SMTP: ").strip()
    if not smtp_server:
        smtp_server = "smtp.gmail.com"
    
    # SMTP Port
    print("\n2. Porta SMTP:")
    print("   Gmail: 587 (TLS) ou 465 (SSL)")
    print("   Outlook: 587 (TLS)")
    smtp_port = input("   Porta (padrão 587): ").strip()
    if not smtp_port:
        smtp_port = 587
    else:
        smtp_port = int(smtp_port)
    
    # Email
    print("\n3. Seu email (remetente):")
    email = input("   Email: ").strip()
    
    # Password
    print("\n4. Senha:")
    print("   ⚠️  IMPORTANTE:")
    print("   • Para Gmail: Use 'Senha de App' (não a senha normal)")
    print("   • Obter em: https://myaccount.google.com/apppasswords")
    print("   • Para Outlook: Pode usar senha normal ou senha de app")
    password = input("   Senha: ").strip()
    
    # Destinatário
    print("\n5. Email destinatário (onde receber os links M3U):")
    to_email = input("   Email destinatário: ").strip()
    
    # Use TLS
    print("\n6. Usar TLS? (recomendado para Gmail/Outlook)")
    use_tls = input("   Usar TLS? (S/n): ").strip().lower()
    use_tls = use_tls != 'n'
    
    # Criar configuração
    config = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "email": email,
        "password": password,
        "to_email": to_email,
        "use_tls": use_tls
    }
    
    # Salvar
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("✅ CONFIGURAÇÃO SALVA!")
    print("="*70)
    print(f"📁 Arquivo: {CONFIG_FILE}")
    print(f"📧 De: {email}")
    print(f"📧 Para: {to_email}")
    print("\n💡 Para testar, execute:")
    print("   python -m src.send_m3u_email")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        setup_email()
    except KeyboardInterrupt:
        print("\n\n👋 Configuração cancelada")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

