# install_mongo.ps1 — instalado em {app} pelo Inno Setup
# Instala TUDO que o MongoDB precisa, de forma autonoma:
#   1. Visual C++ Redistributable (x64) — mongod 8.x nao roda sem a versao mais nova
#      (crash 0xC0000139 STATUS_ENTRYPOINT_NOT_FOUND antes de gerar qualquer log).
#   2. MongoDB Server — tenta winget; se falhar, baixa o MSI oficial e roda msiexec.
#   3. Cria/inicia o servico e valida a porta 27017 de fato.
# Roda em contexto ELEVADO (admin) durante a instalacao.

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Versao do MongoDB (fixada). O 8.x falha em algumas maquinas Windows com
# "entry point GetProcessWorkingSetSize not found" (0xC0000139) no load do mongod.
# 7.0 e LTS e roda de forma ampla no Win10/11 — usada no winget E no MSI direto.
$MongoVersion = "7.0.28"
$MongoMsiUrl  = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-$MongoVersion-signed.msi"
$VcRedistUrl  = "https://aka.ms/vs/17/release/vc_redist.x64.exe"

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

# Testa se a porta 27017 aceita conexao (servico realmente no ar).
function Test-MongoPort {
    try {
        $c = New-Object Net.Sockets.TcpClient
        $c.Connect("127.0.0.1", 27017)
        $ok = $c.Connected
        $c.Close()
        return $ok
    } catch { return $false }
}

# Resolve o winget mesmo quando nao esta no PATH (contexto elevado/nao-interativo).
function Resolve-Winget {
    $cmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $userAlias = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\winget.exe"
    if (Test-Path $userAlias) { return $userAlias }
    $pkg = Get-ChildItem "$env:ProgramFiles\WindowsApps" -Filter "winget.exe" -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -like "*Microsoft.DesktopAppInstaller_*" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if ($pkg) { return $pkg.FullName }
    return $null
}

# Baixa um arquivo com log de progresso simples.
function Download-File($url, $dest) {
    Log "Baixando $url"
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
    Log "Salvo em $dest ($([math]::Round((Get-Item $dest).Length/1MB,1)) MB)"
}

# --- 1. Visual C++ Redistributable (x64) ---------------------------------
# Instala sempre (idempotente): o mongod 8.x exige a versao mais recente e o
# instalador ignora se ja estiver atualizado (codigo 1638).
function Ensure-VCRedist {
    Log "Garantindo Visual C++ Redistributable (x64)..."
    $vc = Join-Path $env:TEMP "vc_redist.x64.exe"
    try {
        Download-File $VcRedistUrl $vc
        $p = Start-Process -FilePath $vc -ArgumentList "/install","/quiet","/norestart" -Wait -PassThru
        $code = $p.ExitCode
        # 0 = ok, 3010 = ok (precisa reboot), 1638 = versao mais nova ja instalada
        if ($code -in 0,3010,1638) {
            Log "VC++ Redistributable OK (codigo $code)."
        } else {
            Log "VC++ Redistributable retornou codigo $code (seguindo mesmo assim)."
        }
    } catch {
        Log "AVISO: falha ao instalar VC++ Redistributable: $($_.Exception.Message)"
    } finally {
        Remove-Item $vc -ErrorAction SilentlyContinue
    }
}

# --- 2. Instala o MongoDB Server -----------------------------------------
function Install-MongoWinget {
    $winget = Resolve-Winget
    if (-not $winget) { Log "winget nao encontrado."; return $false }
    Log "Instalando MongoDB $MongoVersion via winget: $winget"
    # --version fixa o 7.0 (evita o 8.x que quebra no load em algumas maquinas).
    # --force evita cair no fluxo de 'update' quando ha registro orfao (0x8A15002B).
    & $winget install -e --id MongoDB.Server --version $MongoVersion --scope machine -h --force `
        --accept-package-agreements --accept-source-agreements
    Log "winget install retornou codigo $LASTEXITCODE"
    return ($LASTEXITCODE -eq 0)
}

function Install-MongoMsi {
    Log "Instalando MongoDB via MSI direto (fallback sem winget)..."
    $msi = Join-Path $env:TEMP "mongodb-$MongoVersion.msi"
    Download-File $MongoMsiUrl $msi
    # ADDLOCAL=ServerService instala o mongod E cria o servico do Windows.
    # SHOULD_INSTALL_COMPASS=0 evita baixar o Compass (grande e desnecessario).
    $args = "/i `"$msi`" /qn /norestart ADDLOCAL=`"ServerService,Client`" SHOULD_INSTALL_COMPASS=`"0`""
    $p = Start-Process -FilePath "msiexec.exe" -ArgumentList $args -Wait -PassThru
    Log "msiexec retornou codigo $($p.ExitCode)"
    Remove-Item $msi -ErrorAction SilentlyContinue
    return ($p.ExitCode -in 0,3010)
}

# --- 3. Inicia o servico e valida ----------------------------------------
function Start-MongoAndVerify {
    $mongo = Get-MongoService
    if (-not $mongo) { Log "Servico MongoDB nao encontrado."; return $false }
    if ($mongo.Status -ne "Running") {
        try {
            Start-Service $mongo.Name -ErrorAction Stop
            Log "Servico $($mongo.Name) iniciado."
        } catch {
            Log "Falha ao iniciar servico: $($_.Exception.Message)"
        }
    }
    # Espera a porta responder (mongod leva alguns segundos pra subir).
    for ($i = 0; $i -lt 15; $i++) {
        if (Test-MongoPort) { Log "MongoDB respondendo na porta 27017."; return $true }
        Start-Sleep -Seconds 2
    }
    Log "MongoDB nao respondeu na porta 27017 apos aguardar."
    return $false
}

# =========================================================================
Log "=== Iniciando configuracao do MongoDB ==="

Ensure-VCRedist

# Se ja existe e responde na porta, nada a fazer.
$mongo = Get-MongoService
if ($mongo -and (Start-MongoAndVerify)) {
    Log "OK (ja instalado e rodando)."
    exit 0
}

# Se existe um MongoDB instalado mas que nao sobe (ex.: 8.x com bug de entrypoint),
# desinstala antes para o 7.0 entrar limpo.
if ($mongo) {
    Log "MongoDB existente nao subiu. Desinstalando antes de reinstalar o $MongoVersion..."
    $winget = Resolve-Winget
    if ($winget) { & $winget uninstall --id MongoDB.Server -e --silent 2>&1 | Out-Null }
}

# Nao existe (ou existe quebrado): instala. winget primeiro, MSI como fallback.
$installed = Install-MongoWinget
if (-not $installed) {
    Log "winget falhou/indisponivel. Tentando MSI direto..."
    try {
        $installed = Install-MongoMsi
    } catch {
        Log "Falha no MSI direto: $($_.Exception.Message)"
        $installed = $false
    }
}

if (-not $installed) {
    Log "ERRO: nao foi possivel instalar o MongoDB automaticamente."
    Start-Process "https://www.mongodb.com/try/download/community"
    exit 1
}

# Da um tempo pro servico ser registrado apos a instalacao.
for ($i = 0; $i -lt 12 -and -not (Get-MongoService); $i++) { Start-Sleep -Seconds 3 }

if (Start-MongoAndVerify) {
    Log "MongoDB instalado e rodando."
    exit 0
} else {
    Log "MongoDB instalado, mas o servico nao subiu. Verifique o log do mongod."
    exit 1
}
