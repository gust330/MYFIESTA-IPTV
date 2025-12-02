# 🚀 Guia de Deployment - Manter o Sistema Rodando 24/7

Este guia explica como manter o sistema de renovação automática de IPTV funcionando mesmo com o computador desligado.

## 📋 Opções Disponíveis

### 1. 🆓 Serviços na Nuvem Gratuitos (Recomendado)

#### Opção A: Render.com (Recomendado)
Render oferece plano gratuito que permite executar aplicações Python continuamente.

**Passos:**
1. Acesse [render.com](https://render.com) e crie uma conta (pode usar GitHub)
2. Crie um novo "Background Worker"
3. Conecte seu repositório GitHub
4. Configure:
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `python -m src.email_scheduler`
5. Adicione variáveis de ambiente:
   - `RAPIDAPI_KEY` - Sua chave da RapidAPI (configure manualmente no dashboard)
6. Deploy!

**Vantagens:**
- ✅ Gratuito (com limites)
- ✅ Fácil de configurar
- ✅ Roda 24/7 automaticamente
- ✅ Não precisa manter PC ligado
- ✅ Suporta Playwright out-of-the-box

**Arquivo de configuração:**
O projeto já inclui `render.yaml` com as configurações necessárias. Render detectará automaticamente este arquivo.

---

#### Opção B: PythonAnywhere
Similar ao Railway, também oferece plano gratuito.

**Passos:**
1. Acesse [render.com](https://render.com) e crie uma conta
2. Crie um novo "Background Worker"
3. Conecte seu repositório
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m src.email_scheduler`
5. Adicione variáveis de ambiente (RAPIDAPI_KEY)
6. Deploy!

**Vantagens:**
- ✅ Gratuito
- ✅ Roda 24/7
- ✅ Interface simples

---

#### Opção C: PythonAnywhere
Especializado em Python, oferece plano gratuito.

**Passos:**
1. Acesse [pythonanywhere.com](https://www.pythonanywhere.com)
2. Crie uma conta gratuita
3. Faça upload dos arquivos via interface web
4. Configure uma tarefa agendada (Scheduled Tasks):
   - **Command**: `cd /home/seuusuario/MYFIESTA-IPTV-main && python -m src.send_m3u_email`
   - **Schedule**: A cada 48 horas
5. Configure também o email (SMTP) nas configurações

**Vantagens:**
- ✅ Gratuito
- ✅ Especializado em Python
- ✅ Interface web completa

---

### 2. 💻 Windows Task Scheduler (PC Precisa Estar Ligado)

Se você mantém o PC ligado 24/7, pode usar o Agendador de Tarefas do Windows.

**Passos:**

1. Abra o **Agendador de Tarefas** (Task Scheduler)
   - Pressione `Win + R`, digite `taskschd.msc` e Enter

2. Clique em **Criar Tarefa Básica** (Create Basic Task)

3. Configure:
   - **Nome**: `IPTV Auto Renewal`
   - **Descrição**: `Renova credenciais IPTV a cada 48 horas`

4. **Gatilho (Trigger)**:
   - Selecione **Recorrente**
   - Configure para repetir a cada **2 dias** (48 horas)
   - Hora inicial: escolha uma hora conveniente

5. **Ação (Action)**:
   - Selecione **Iniciar um programa**
   - **Programa/script**: `python`
   - **Adicionar argumentos**: `-m src.send_m3u_email`
   - **Iniciar em**: `C:\Users\gustv\Documents\MYFIESTA-IPTV-main`

6. **Condições**:
   - ✅ Marque "Iniciar a tarefa mesmo se o computador estiver em modo de espera"
   - ✅ Marque "Acordar o computador para executar esta tarefa"

7. **Configurações**:
   - ✅ Marque "Executar tarefa o mais rápido possível após uma inicialização atrasada"
   - ✅ Marque "Se a tarefa falhar, reiniciar a cada: 1 hora"

**Script Auxiliar (opcional):**
Crie um arquivo `run_scheduler.bat`:
```batch
@echo off
cd /d "C:\Users\gustv\Documents\MYFIESTA-IPTV-main"
python -m src.send_m3u_email
```

---

### 3. 🖥️ Servidor Dedicado / VPS

Se você tem acesso a um servidor (VPS, Raspberry Pi, etc.), pode executar como serviço.

#### Linux (systemd)

Crie um arquivo `/etc/systemd/system/iptv-renewal.service`:

```ini
[Unit]
Description=IPTV Auto Renewal Service
After=network.target

[Service]
Type=simple
User=seuusuario
WorkingDirectory=/caminho/para/MYFIESTA-IPTV-main
ExecStart=/usr/bin/python3 -m src.email_scheduler
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Ative o serviço:
```bash
sudo systemctl enable iptv-renewal.service
sudo systemctl start iptv-renewal.service
```

#### Windows (NSSM - Non-Sucking Service Manager)

1. Baixe [NSSM](https://nssm.cc/download)
2. Instale como serviço:
```cmd
nssm install IPTVRenewal "C:\Python\python.exe" "-m src.email_scheduler"
nssm set IPTVRenewal AppDirectory "C:\Users\gustv\Documents\MYFIESTA-IPTV-main"
nssm start IPTVRenewal
```

---

## 🔧 Configuração Necessária

Independente da opção escolhida, você precisa:

### 1. Variáveis de Ambiente

Configure a chave da RapidAPI:
- **Windows**: Variáveis de Ambiente do Sistema
- **Linux/Cloud**: Arquivo `.env` ou configuração do serviço

### 2. Configuração de Email

Execute uma vez:
```bash
python scripts/setup_email.py
```

Isso criará o arquivo `data/config.json` com suas configurações SMTP.

### 3. Teste Antes de Deployar

Teste localmente primeiro:
```bash
python -m src.send_m3u_email
```

---

## 📊 Comparação das Opções

| Opção | Custo | Complexidade | Requer PC Ligado | Recomendado Para |
|-------|-------|--------------|------------------|------------------|
| Render.com | Gratuito | ⭐ Fácil | ❌ Não | Todos |
| PythonAnywhere | Gratuito | ⭐⭐ Médio | ❌ Não | Todos |
| Windows Task Scheduler | Gratuito | ⭐⭐ Médio | ✅ Sim | Quem mantém PC ligado |
| VPS/Servidor | Pago | ⭐⭐⭐ Difícil | ❌ Não | Usuários avançados |

---

## 🎯 Recomendação

**Para a maioria dos usuários**: Use **Render.com**
- É gratuito
- Fácil de configurar
- Funciona 24/7 sem precisar manter PC ligado
- Não requer conhecimento técnico avançado
- Suporta Playwright nativamente

---

## 🐛 Troubleshooting

### O processo não está rodando
- Verifique os logs do serviço
- Confirme que as variáveis de ambiente estão configuradas
- Teste localmente primeiro

### Email não está sendo enviado
- Verifique `data/config.json`
- Teste a configuração SMTP
- Confirme que a senha de app (Gmail) está correta

### Credenciais não estão sendo obtidas
- Verifique se a chave da RapidAPI está válida
- Confirme que o email gerado é @gmail.com
- Verifique os logs para erros específicos

---

## 📝 Notas Importantes

1. **Serviços Gratuitos**: Têm limites de uso. Se exceder, pode precisar fazer upgrade.

2. **Segurança**: Nunca commite arquivos com credenciais no Git. Use variáveis de ambiente.

3. **Backup**: Mantenha backup do arquivo `data/config.json` em local seguro.

4. **Monitoramento**: Configure notificações (se disponível) para saber quando o processo executa.

---

## 🆘 Suporte

Se tiver problemas:
1. Verifique os logs do serviço
2. Teste localmente primeiro
3. Confirme todas as configurações
4. Verifique a documentação do serviço escolhido

