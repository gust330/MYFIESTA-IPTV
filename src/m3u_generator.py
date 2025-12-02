"""
M3U Generator - Gera URL M3U a partir de credenciais
"""
import os
import json
from typing import Optional, Dict


class M3UGenerator:
    """Gera URL M3U para uso no VLC"""
    
    def __init__(self, credentials_file: Optional[str] = None):
        """
        Inicializar M3U Generator
        
        Args:
            credentials_file: Caminho para arquivo de credenciais
        """
        if credentials_file is None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            credentials_file = os.path.join(BASE_DIR, "data", "credentials.json")
        
        self.credentials_file = credentials_file
        self.credentials = None
    
    def load_credentials(self) -> bool:
        """Carregar credenciais do arquivo"""
        try:
            if not os.path.exists(self.credentials_file):
                print(f"❌ Arquivo de credenciais não encontrado: {self.credentials_file}")
                return False
            
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            required_fields = ['username', 'password', 'url']
            for field in required_fields:
                if field not in data:
                    print(f"❌ Campo obrigatório '{field}' não encontrado")
                    return False
            
            self.credentials = {
                'username': data['username'],
                'password': data['password'],
                'url': data['url'],
                'email': data.get('email', '')
            }
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar credenciais: {e}")
            return False
    
    def generate_m3u_url(self) -> Optional[str]:
        """
        Gerar URL M3U a partir das credenciais
        
        Returns:
            URL M3U completa ou None se falhar
        """
        if not self.credentials:
            if not self.load_credentials():
                return None
        
        username = self.credentials['username']
        password = self.credentials['password']
        url = self.credentials['url']
        
        # Formato Xtream Codes para M3U
        # type=m3u_plus: playlist com metadados
        # output=m3u8: formato HLS (melhor compatibilidade)
        m3u_url = f"{url}/get.php?username={username}&password={password}&type=m3u_plus&output=m3u8"
        
        print(f"✅ URL M3U gerada:")
        print(f"   {m3u_url[:80]}...")
        
        return m3u_url
    
    def get_credentials_info(self) -> Optional[Dict]:
        """Retornar informações das credenciais"""
        if not self.credentials:
            if not self.load_credentials():
                return None
        
        return self.credentials.copy()

