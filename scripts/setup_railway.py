"""
Script auxiliar para configurar o projeto no Railway.app
Gera os arquivos necessários para deployment
"""
import os
import json

def create_railway_files():
    """Cria arquivos necessários para Railway"""
    
    # 1. Criar Procfile (se não existir)
    procfile_path = "Procfile"
    if not os.path.exists(procfile_path):
        with open(procfile_path, 'w') as f:
            f.write("worker: python -m src.email_scheduler\n")
        print("✅ Procfile criado")
    else:
        print("ℹ️  Procfile já existe")
    
    # 2. Criar runtime.txt (especifica versão do Python)
    runtime_path = "runtime.txt"
    if not os.path.exists(runtime_path):
        with open(runtime_path, 'w') as f:
            f.write("python-3.11\n")  # Ajuste conforme necessário
        print("✅ runtime.txt criado")
    else:
        print("ℹ️  runtime.txt já existe")
    
    # 3. Criar .railwayignore (opcional)
    railwayignore_path = ".railwayignore"
    ignore_patterns = [
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".env",
        "venv/",
        "env/",
        ".git/",
        "screenshot_*.png",
        "*.log"
    ]
    
    if not os.path.exists(railwayignore_path):
        with open(railwayignore_path, 'w') as f:
            f.write("\n".join(ignore_patterns))
        print("✅ .railwayignore criado")
    else:
        print("ℹ️  .railwayignore já existe")
    
    # 4. Criar railway.json (configuração)
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python -m src.email_scheduler",
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    railway_json_path = "railway.json"
    if not os.path.exists(railway_json_path):
        with open(railway_json_path, 'w') as f:
            json.dump(railway_config, f, indent=2)
        print("✅ railway.json criado")
    else:
        print("ℹ️  railway.json já existe")
    
    print("\n" + "="*70)
    print("✅ ARQUIVOS PARA RAILWAY CRIADOS!")
    print("="*70)
    print("\n📋 Próximos passos:")
    print("1. Acesse https://railway.app")
    print("2. Crie uma nova conta/projeto")
    print("3. Conecte seu repositório GitHub")
    print("4. Configure a variável de ambiente RAPIDAPI_KEY")
    print("5. Deploy!")
    print("\n💡 Dica: Configure também o email antes:")
    print("   python scripts/setup_email.py")
    print("="*70 + "\n")

if __name__ == "__main__":
    create_railway_files()

