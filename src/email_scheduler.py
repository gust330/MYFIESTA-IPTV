"""
Scheduler para enviar email com M3U a cada 48 horas
"""
import schedule
import time
import sys
import os

# Adicionar diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.send_m3u_email import main


def run_scheduled_task():
    """Executar tarefa agendada"""
    print("\n" + "="*70)
    print("⏰ EXECUTANDO TAREFA AGENDADA")
    print("="*70)
    
    try:
        main()
    except Exception as e:
        print(f"❌ Erro na tarefa agendada: {e}")
        import traceback
        traceback.print_exc()


def start_scheduler():
    """Iniciar scheduler"""
    print("\n" + "="*70)
    print("📅 SCHEDULER DE EMAIL IPTV")
    print("="*70)
    print("\n✅ Scheduler configurado para executar a cada 48 horas")
    print("   Primeira execução: Imediata")
    print("   Próximas execuções: A cada 48 horas")
    print("\n⚠️  Mantenha este terminal aberto")
    print("   Pressione Ctrl+C para parar")
    print("="*70 + "\n")
    
    # Executar imediatamente na primeira vez
    run_scheduled_task()
    
    # Agendar para executar a cada 48 horas
    schedule.every(48).hours.do(run_scheduled_task)
    
    # Loop principal
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    except KeyboardInterrupt:
        print("\n\n👋 Scheduler parado")
        sys.exit(0)


if __name__ == "__main__":
    start_scheduler()

