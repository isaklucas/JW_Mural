# install_mongo.ps1 — instalado em {app} pelo Inno Setup
# Verifica/instala MongoDB e garante que o servico esta rodando

$ErrorActionPreference = "Stop"

function Get-MongoService {
    return Get-Service | Where-Object { $_.DisplayName -like "*Mongo*" } | Select-Object -First 1
}

$mongo = Get-MongoService

if ($mongo) {
    Write-Host "MongoDB encontrado: $($mongo.Name) [$($mongo.Status)]"
    if ($mongo.Status -ne "Running") {
        Start-Service $mongo.Name
        Write-Host "Servico iniciado."
    }
    exit 0
}

Write-Host "MongoDB nao encontrado. Instalando via winget..."

$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    Write-Host "winget nao disponivel. Abrindo pagina de download..."
    Start-Process "https://www.mongodb.com/try/download/community"
    Write-Host "Instale o MongoDB manualmente e execute o instalador novamente."
    exit 1
}

winget install -e --id MongoDB.Server -h --accept-package-agreements --accept-source-agreements
if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha ao instalar MongoDB via winget (codigo $LASTEXITCODE)."
    exit 1
}

Write-Host "Aguardando servico MongoDB..."
Start-Sleep -Seconds 8

$mongo = Get-MongoService
if ($mongo) {
    if ($mongo.Status -ne "Running") {
        Start-Service $mongo.Name -ErrorAction SilentlyContinue
    }
    Write-Host "MongoDB instalado e rodando."
    exit 0
} else {
    Write-Host "Servico MongoDB nao encontrado apos instalacao. Verifique manualmente."
    exit 1
}
