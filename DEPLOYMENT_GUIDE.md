# 🚀 Guia de Deployment - Manter o Sistema Rodando 24/7

Este guia explica como manter o sistema de renovação automática de IPTV funcionando mesmo com o computador desligado.

## 🎯 Opção Recomendada: GitHub Actions (100% Gratuito)

**GitHub Actions** é a melhor opção gratuita - totalmente gratuito, sem limites para repositórios públicos, e fácil de configurar.

### Configuração GitHub Actions

**Passos:**

1. **Configure os Secrets no GitHub:**
   - Vá em: Settings → Secrets and variables → Actions → New repository secret
   - Adicione os seguintes secrets:
     - `RAPIDAPI_KEY` - Sua chave da RapidAPI
     - `SMTP_SERVER` - Servidor SMTP (ex: smtp.gmail.com)
     - `SMTP_PORT` - Porta SMTP (ex: 587)
     - `SENDER_EMAIL` - Seu email remetente
     - `SENDER_PASSWORD` - Senha de app do email
     - `RECEIVER_EMAIL` - Email destinatário

2. **O workflow já está configurado!**
   - O arquivo `.github/workflows/iptv-renewal.yml` já está criado
   - Executa automaticamente a cada 48 horas
   - Você também pode executar manualmente: Actions → IPTV Auto Renewal → Run workflow

3. **Pronto!** O sistema executará automaticamente a cada 48 horas.

**Vantagens:**
- ✅ **100% Gratuito** - Sem limites para repositórios públicos
- ✅ **Automático** - Executa a cada 48 horas via cron
- ✅ **Sem manutenção** - Não precisa manter nada rodando
- ✅ **Logs completos** - Veja todas as execuções no GitHub
- ✅ **Execução manual** - Pode executar quando quiser

---

## 📋 Outras Opções Gratuitas

### Opção 2: PythonAnywhere (Tarefas Agendadas)

PythonAnywhere oferece plano gratuito com tarefas agendadas.

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

**Limitações:**
- ⚠️ Tarefas agendadas têm limites no plano gratuito
- ⚠️ Precisa fazer upload manual dos arquivos

---

### Opção 3: Windows Task Scheduler (PC Precisa Estar Ligado)

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
Execute como Administrador:
```powershell
.\scripts\setup_windows_task.ps1
```

---

## 🔧 Configuração Necessária

### Para GitHub Actions

Configure os secrets no GitHub:
1. Vá em: **Settings → Secrets and variables → Actions**
2. Adicione os secrets necessários (veja lista acima)

### Para Outras Opções

Execute localmente para configurar o email:
```bash
python scripts/setup_email.py
```

Isso criará o arquivo `data/config.json` com suas configurações SMTP.

---

## 📊 Comparação das Opções

| Opção | Custo | Complexidade | Requer PC Ligado | Recomendado Para |
|-------|-------|--------------|------------------|------------------|
| **GitHub Actions** | **100% Gratuito** | ⭐ Fácil | ❌ Não | **Todos (Recomendado)** |
| PythonAnywhere | Gratuito | ⭐⭐ Médio | ❌ Não | Quem prefere interface web |
| Windows Task Scheduler | Gratuito | ⭐⭐ Médio | ✅ Sim | Quem mantém PC ligado |

---

## 🎯 Recomendação Final

**Para todos os usuários**: Use **GitHub Actions**
- ✅ 100% gratuito
- ✅ Fácil de configurar (apenas adicionar secrets)
- ✅ Funciona 24/7 sem precisar manter PC ligado
- ✅ Logs completos e execução manual disponível
- ✅ Não requer conhecimento técnico avançado

---

## 🐛 Troubleshooting

### GitHub Actions não executa

- Verifique se os secrets estão configurados corretamente
- Verifique os logs da execução em Actions → IPTV Auto Renewal
- Confirme que o workflow está habilitado (Actions → Workflows)

### Email não está sendo enviado

- Verifique se todos os secrets de email estão configurados
- Teste localmente primeiro: `python -m src.send_m3u_email`
- Verifique os logs do GitHub Actions

### Credenciais não estão sendo obtidas

- Verifique se `RAPIDAPI_KEY` está configurado corretamente
- Confirme que o email gerado é @gmail.com (o sistema garante isso)
- Verifique os logs do GitHub Actions para erros específicos

---

## 📝 Notas Importantes

1. **GitHub Actions**: Para repositórios públicos, é totalmente gratuito. Para privados, há limites generosos no plano gratuito.

2. **Segurança**: Nunca commite arquivos com credenciais no Git. Use sempre secrets/variáveis de ambiente.

3. **Backup**: Mantenha backup das configurações de email em local seguro.

4. **Monitoramento**: Configure notificações do GitHub para saber quando o workflow executa.

---

## 🆘 Suporte

Se tiver problemas:
1. Verifique os logs do GitHub Actions
2. Teste localmente primeiro: `python -m src.send_m3u_email`
3. Confirme todas as configurações
4. Verifique a documentação do GitHub Actions
