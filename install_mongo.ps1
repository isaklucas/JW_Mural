# install_mongo.ps1 — instalado em {app} pelo Inno Setup
# Verifica/instala MongoDB e garante que o servico esta rodando.
# Roda em contexto ELEVADO (admin) durante a instalacao — winget pode nao estar
# no PATH nesse contexto, por isso resolvemos o caminho explicitamente.

$ErrorActionPreference = "Stop"

# --- Log em arquivo (ao lado do script) para diagnostico ---
$LogFile = Join-Path $PSScriptRoot "install_mongo.log"
function Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg"
    Write-Host $line
    try { Add-Content -Path $LogFile -Value $line -Encoding utf8 } catch {}
}

function Get-MongoService {
    return Get-Service -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -like "*Mongo*" } |
        Select-Object -First 1
}

# Resolve o winget mesmo quando nao esta no PATH (contexto elevado/nao-interativo).
function Resolve-Winget {
    $cmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    # Alias de execucao por-usuario (mesma conta apos elevacao UAC).
    $userAlias = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\winget.exe"
    if (Test-Path $userAlias) { return $userAlias }

    # Local real do pacote (disponivel para o contexto elevado com leitura em Program Files).
    $pkg = Get-ChildItem "$env:ProgramFiles\WindowsApps" -Filter "winget.exe" -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -like "*Microsoft.DesktopAppInstaller_*" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if ($pkg) { return $pkg.FullName }

    return $null
}

Log "=== Iniciando configuracao do MongoDB ==="

$mongo = Get-MongoService
if ($mongo) {
    Log "MongoDB encontrado: $($mongo.Name) [$($mongo.Status)]"
    if ($mongo.Status -ne "Running") {
        Start-Service $mongo.Name
        Log "Servico iniciado."
    }
    Log "OK (ja instalado)."
    exit 0
}

Log "MongoDB nao encontrado. Tentando instalar via winget..."

$winget = Resolve-Winget
if (-not $winget) {
    Log "winget NAO encontrado (PATH, LOCALAPPDATA e WindowsApps). Abrindo pagina de download."
    Start-Process "https://www.mongodb.com/try/download/community"
    Log "Instale o MongoDB manualmente e rode o instalador novamente."
    exit 1
}
Log "winget: $winget"

& $winget install -e --id MongoDB.Server --scope machine -h `
    --accept-package-agreements --accept-source-agreements
$code = $LASTEXITCODE
Log "winget install retornou codigo $code"
if ($code -ne 0) {
    Log "Falha ao instalar MongoDB via winget."
    exit 1
}

Log "Aguardando registro do servico MongoDB..."
$mongo = $null
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Seconds 3
    $mongo = Get-MongoService
    if ($mongo) { break }
}

if ($mongo) {
    if ($mongo.Status -ne "Running") {
        Start-Service $mongo.Name -ErrorAction SilentlyContinue
    }
    Log "MongoDB instalado e rodando ($($mongo.Name))."
    exit 0
} else {
    Log "Servico MongoDB nao encontrado apos instalacao. Verifique manualmente."
    exit 1
}
