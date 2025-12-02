"""
Email Sender - Envia emails com link M3U
"""
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional


class EmailSender:
    """Gerencia envio de emails com links M3U"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializar EmailSender
        
        Args:
            config_file: Caminho para arquivo de configuração de email
        """
        if config_file is None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(BASE_DIR, "data", "email_config.json")
        
        self.config_file = config_file
        self.config = None
        self.load_config()
    
    def load_config(self) -> bool:
        """Carregar configuração de email"""
        try:
            if not os.path.exists(self.config_file):
                print(f"⚠️  Arquivo de configuração não encontrado: {self.config_file}")
                print("   Criando arquivo de exemplo...")
                self.create_example_config()
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            required_fields = ['smtp_server', 'smtp_port', 'email', 'password', 'to_email']
            for field in required_fields:
                if field not in self.config:
                    print(f"❌ Campo obrigatório '{field}' não encontrado na configuração")
                    return False
            
            print(f"✅ Configuração de email carregada")
            print(f"   De: {self.config['email']}")
            print(f"   Para: {self.config['to_email']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {e}")
            return False
    
    def create_example_config(self):
        """Criar arquivo de configuração de exemplo"""
        example_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "seu_email@gmail.com",
            "password": "sua_senha_app",  # Use senha de app do Gmail
            "to_email": "destino@gmail.com",
            "use_tls": True
        }
        
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Arquivo de exemplo criado: {self.config_file}")
        print("   Edite o arquivo com suas configurações de email")
    
    def send_m3u_email(self, m3u_url: str, credentials_info: dict) -> bool:
        """
        Enviar email com link M3U
        
        Args:
            m3u_url: URL do arquivo M3U
            credentials_info: Informações das credenciais (username, password, url, email)
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.config:
            print("❌ Configuração de email não carregada")
            return False
        
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = self.config['to_email']
            msg['Subject'] = f"IPTV - Nova Playlist M3U - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            # Corpo do email
            body = f"""
Olá!

Sua nova playlist IPTV está pronta!

📺 LINK M3U (pronto para VLC):
{m3u_url}

📋 INFORMAÇÕES DAS CREDENCIAIS:
   • Username: {credentials_info.get('username', 'N/A')}
   • Password: {credentials_info.get('password', 'N/A')}
   • URL: {credentials_info.get('url', 'N/A')}
   • Email usado: {credentials_info.get('email', 'N/A')}

📱 COMO USAR NO VLC:
   1. Abra o VLC Media Player
   2. Vá em: Mídia > Abrir Localização de Rede
   3. Cole o link M3U acima
   4. Clique em Reproduzir

💡 DICA: Você também pode salvar o link como favorito no VLC para acesso rápido.

⏰ Próxima atualização: Em 48 horas

---
Este é um email automático do sistema IPTV.
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Conectar e enviar
            print(f"\n📧 Enviando email para {self.config['to_email']}...")
            
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            
            if self.config.get('use_tls', True):
                server.starttls()
            
            server.login(self.config['email'], self.config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email enviado com sucesso!")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Erro de autenticação. Verifique email e senha.")
            print("   Para Gmail, use uma 'Senha de App' em vez da senha normal:")
            print("   https://myaccount.google.com/apppasswords")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
            import traceback
            traceback.print_exc()
            return False

