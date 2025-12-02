# Script PowerShell para configurar Windows Task Scheduler automaticamente
# Execute como Administrador

Write-Host "`n=== CONFIGURAÇÃO DO AGENDADOR DE TAREFAS WINDOWS ===" -ForegroundColor Yellow
Write-Host "`nEste script criará uma tarefa agendada para renovar IPTV a cada 48 horas`n" -ForegroundColor Cyan

# Verificar se está rodando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "   Clique com botão direito e selecione 'Executar como administrador'" -ForegroundColor Yellow
    pause
    exit 1
}

# Obter caminhos
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source

if (-not $pythonExe) {
    Write-Host "❌ Python não encontrado no PATH!" -ForegroundColor Red
    Write-Host "   Certifique-se de que o Python está instalado e no PATH" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "📁 Caminho do projeto: $projectPath" -ForegroundColor Green
Write-Host "🐍 Python: $pythonExe" -ForegroundColor Green

# Nome da tarefa
$taskName = "IPTV_Auto_Renewal"

# Verificar se a tarefa já existe
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "`n⚠️  Tarefa '$taskName' já existe!" -ForegroundColor Yellow
    $response = Read-Host "Deseja substituir? (S/N)"
    if ($response -ne "S" -and $response -ne "s") {
        Write-Host "Operação cancelada." -ForegroundColor Yellow
        exit 0
    }
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "✅ Tarefa antiga removida" -ForegroundColor Green
}

# Criar ação
$action = New-ScheduledTaskAction -Execute $pythonExe `
    -Argument "-m src.send_m3u_email" `
    -WorkingDirectory $projectPath

# Criar gatilho (a cada 2 dias, começando agora)
$trigger = New-ScheduledTaskTrigger -Daily -DaysInterval 2 -At (Get-Date).AddMinutes(5)

# Criar configurações
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 60)

# Criar principal (executar mesmo quando usuário não estiver logado)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest

# Registrar tarefa
try {
    Register-ScheduledTask -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Renova credenciais IPTV automaticamente a cada 48 horas" | Out-Null
    
    Write-Host "`n✅ TAREFA CRIADA COM SUCESSO!" -ForegroundColor Green
    Write-Host "`n📋 Detalhes:" -ForegroundColor Cyan
    Write-Host "   Nome: $taskName" -ForegroundColor White
    Write-Host "   Frequência: A cada 2 dias (48 horas)" -ForegroundColor White
    Write-Host "   Próxima execução: Verifique no Agendador de Tarefas" -ForegroundColor White
    
    Write-Host "`n💡 Para verificar ou editar:" -ForegroundColor Yellow
    Write-Host "   Abra o Agendador de Tarefas (taskschd.msc)" -ForegroundColor White
    Write-Host "   Procure por: $taskName" -ForegroundColor White
    
    Write-Host "`n🧪 Para testar manualmente:" -ForegroundColor Yellow
    Write-Host "   python -m src.send_m3u_email" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Erro ao criar tarefa: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n" -NoNewline
pause

