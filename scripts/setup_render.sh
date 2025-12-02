#!/bin/bash
# Script para configurar o projeto no Render.com
# Execute este script antes de fazer deploy no Render

echo "=========================================="
echo "  CONFIGURAÇÃO PARA RENDER.COM"
echo "=========================================="
echo ""

# Criar render.yaml se não existir
if [ ! -f "render.yaml" ]; then
    cat > render.yaml << 'EOF'
services:
  - type: worker
    name: iptv-renewal-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m src.email_scheduler
    envVars:
      - key: RAPIDAPI_KEY
        sync: false  # Configure manualmente no dashboard do Render
EOF
    echo "✅ render.yaml criado"
else
    echo "ℹ️  render.yaml já existe"
fi

# Criar .renderignore se não existir
if [ ! -f ".renderignore" ]; then
    cat > .renderignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.pyd
.env
venv/
env/
.git/
screenshot_*.png
*.log
EOF
    echo "✅ .renderignore criado"
else
    echo "ℹ️  .renderignore já existe"
fi

echo ""
echo "=========================================="
echo "✅ ARQUIVOS CRIADOS!"
echo "=========================================="
echo ""
echo "📋 Próximos passos:"
echo "1. Acesse https://render.com"
echo "2. Crie uma nova conta"
echo "3. Crie um novo 'Background Worker'"
echo "4. Conecte seu repositório GitHub"
echo "5. Configure a variável de ambiente RAPIDAPI_KEY"
echo "6. Deploy!"
echo ""
echo "💡 Dica: Configure também o email antes:"
echo "   python scripts/setup_email.py"
echo ""

