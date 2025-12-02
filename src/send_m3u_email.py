"""
Script principal para buscar credenciais, gerar M3U e enviar por email
"""
import os
import sys
from datetime import datetime

# Adicionar diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.auto_update import fetch_credentials_automated
from src.m3u_generator import M3UGenerator
from src.email_sender import EmailSender


def main():
    """Função principal"""
    print("\n" + "="*70)
    print("📧 SISTEMA DE ENVIO DE PLAYLIST M3U POR EMAIL")
    print("="*70)
    print(f"⏰ Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*70 + "\n")
    
    # 1. Buscar novas credenciais
    print("📡 Passo 1: Buscando novas credenciais...")
    print("-" * 70)
    
    if not fetch_credentials_automated():
        print("❌ Falha ao buscar credenciais")
        return False
    
    print("✅ Credenciais obtidas com sucesso!\n")
    
    # 2. Gerar URL M3U
    print("🔗 Passo 2: Gerando URL M3U...")
    print("-" * 70)
    
    m3u_gen = M3UGenerator()
    m3u_url = m3u_gen.generate_m3u_url()
    
    if not m3u_url:
        print("❌ Falha ao gerar URL M3U")
        return False
    
    credentials_info = m3u_gen.get_credentials_info()
    
    print("✅ URL M3U gerada!\n")
    
    # 3. Enviar email
    print("📧 Passo 3: Enviando email...")
    print("-" * 70)
    
    email_sender = EmailSender()
    
    if not email_sender.send_m3u_email(m3u_url, credentials_info):
        print("❌ Falha ao enviar email")
        return False
    
    print("\n" + "="*70)
    print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
    print("="*70)
    print(f"📧 Email enviado com link M3U")
    print(f"🔗 Link: {m3u_url[:80]}...")
    print(f"⏰ Próxima execução: Em 48 horas")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Processo interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

