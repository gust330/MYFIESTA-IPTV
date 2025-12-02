# 📧 MYFIESTA IPTV - Sistema Automático de Renovação

Sistema automatizado que busca credenciais IPTV a cada 48 horas e envia o link M3U por email, pronto para usar no VLC Player.

## 🎯 Funcionalidades

- ✅ **Busca Automática de Credenciais** - Obtém novas credenciais IPTV automaticamente via Playwright
- ✅ **Geração de Link M3U** - Cria link M3U compatível com VLC Player
- ✅ **Envio Automático por Email** - Envia email a cada 48 horas com o novo link
- ✅ **Scheduler Automático** - Executa automaticamente sem intervenção manual
- ✅ **Deployment na Nuvem** - Suporta Railway, Render e outros serviços

## 📋 Pré-requisitos

1. **Python 3.8+**
2. **Conta de email** (Gmail, Outlook, etc.) para envio
3. **Chave RapidAPI** para geração de emails temporários
4. **Dependências**: `pip install -r requirements.txt`

## 🚀 Instalação Rápida

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd MYFIESTA-IPTV-main
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure a chave RapidAPI

Edite `src/playwright_script.py` e adicione sua chave:

```python
RAPIDAPI_KEY = "sua-chave-aqui"
```

Obtenha uma chave gratuita em: https://rapidapi.com/johndevz/api/gmailnator

### 4. Configure o email

Execute o script de configuração:

```bash
python scripts/setup_email.py
```

**Para Gmail:**
- Use uma **Senha de App** (não a senha normal)
- Obtenha em: https://myaccount.google.com/apppasswords
- Servidor: `smtp.gmail.com`
- Porta: `587` (TLS)

**Para Outlook:**
- Pode usar senha normal ou senha de app
- Servidor: `smtp-mail.outlook.com`
- Porta: `587` (TLS)

## 🎮 Uso

### Teste Manual

Execute uma vez para testar:

```bash
python -m src.send_m3u_email
```

Este comando vai:
1. Buscar novas credenciais automaticamente
2. Gerar o link M3U
3. Enviar email com o link

### Execução Automática (48 em 48 horas)

#### Opção 1: Scheduler Python (Local)

```bash
python -m src.email_scheduler
```

O scheduler vai:
- Executar imediatamente na primeira vez
- Executar novamente a cada 48 horas
- Manter-se rodando em background

**⚠️ Mantenha o terminal aberto!**

#### Opção 2: Deployment na Nuvem (Recomendado)

Para manter o sistema rodando 24/7 mesmo com o computador desligado, consulte o **[Guia de Deployment](DEPLOYMENT_GUIDE.md)**.

**Opções recomendadas:**
- 🆓 **Railway.app** - Gratuito, fácil de configurar
- 🆓 **Render.com** - Gratuito, similar ao Railway
- 💻 **Windows Task Scheduler** - Se mantiver PC ligado

## 📧 Como Usar o Link M3U no VLC

1. Abra o **VLC Media Player**
2. Vá em: **Mídia > Abrir Localização de Rede** (ou `Ctrl+N`)
3. Cole o link M3U do email
4. Clique em **Reproduzir**

**Dica:** Salve o link como favorito no VLC para acesso rápido!

## 📁 Estrutura do Projeto

```
MYFIESTA-IPTV-main/
├── src/
│   ├── playwright_script.py    # Busca credenciais via Playwright
│   ├── send_m3u_email.py       # Script principal (busca + gera + envia)
│   ├── email_sender.py         # Envio de emails via SMTP
│   ├── m3u_generator.py        # Geração de URL M3U
│   └── email_scheduler.py       # Scheduler automático
├── scripts/
│   ├── setup_email.py          # Configuração interativa de email
│   ├── setup_railway.py        # Setup para Railway.app
│   ├── setup_render.sh         # Setup para Render.com
│   └── setup_windows_task.ps1  # Setup Windows Task Scheduler
├── data/                       # Dados (auto-criado)
│   ├── config.json             # Configuração de email
│   └── credentials.json        # Credenciais IPTV
├── requirements.txt            # Dependências Python
├── DEPLOYMENT_GUIDE.md         # Guia completo de deployment
└── README.md                   # Este arquivo
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Para deployment na nuvem, configure:

- `RAPIDAPI_KEY` - Sua chave da RapidAPI

### Arquivo de Configuração

O arquivo `data/config.json` é criado automaticamente ao executar `setup_email.py`:

```json
{
  "email_config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "seu-email@gmail.com",
    "sender_password": "sua-senha-de-app",
    "receiver_email": "destinatario@gmail.com"
  }
}
```

## 🛠️ Solução de Problemas

### Erro de Autenticação de Email

**Gmail:**
- Use **Senha de App** em vez da senha normal
- Ative verificação em 2 etapas primeiro
- Obter senha de app: https://myaccount.google.com/apppasswords

**Outlook:**
- Verifique se a senha está correta
- Pode precisar ativar "Aplicativos menos seguros"

### Email não chega

- Verifique a pasta de **Spam**
- Confirme que o email destinatário está correto
- Teste enviando manualmente primeiro: `python -m src.send_m3u_email`

### Credenciais não são obtidas

- Verifique se a chave da RapidAPI está válida
- Confirme que o email gerado é @gmail.com (o sistema garante isso automaticamente)
- Verifique os logs para erros específicos

### Scheduler não funciona

- Verifique se o Python está no PATH
- Use caminho absoluto no agendador do Windows
- Mantenha o terminal aberto se usar scheduler Python
- Para 24/7, use deployment na nuvem (Railway/Render)

## 📝 Notas Importantes

- O sistema busca **novas credenciais** automaticamente a cada execução
- O link M3U é gerado dinamicamente a partir das credenciais atuais
- As credenciais são válidas por ~48 horas (trial)
- O email é enviado **antes** das credenciais expirarem
- O sistema garante que emails gerados sejam sempre @gmail.com

## 🚀 Deployment na Nuvem

Para manter o sistema rodando 24/7 sem precisar manter o computador ligado, consulte o **[Guia de Deployment](DEPLOYMENT_GUIDE.md)**.

### Quick Start - Railway.app

1. Execute: `python scripts/setup_railway.py`
2. Acesse [railway.app](https://railway.app)
3. Conecte seu repositório GitHub
4. Configure a variável `RAPIDAPI_KEY`
5. Deploy!

## 📄 Licença

Este projeto é fornecido "como está" para fins educacionais.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs do sistema
2. Consulte o [Guia de Deployment](DEPLOYMENT_GUIDE.md)
3. Teste localmente primeiro
4. Verifique todas as configurações

---

**Desenvolvido para automatizar a renovação de credenciais IPTV e facilitar o acesso via VLC Player.**
