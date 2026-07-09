<#
  release.ps1 — Pipeline completa de release do JW Mural.

  Uso:
    powershell -ExecutionPolicy Bypass -File release.ps1 -Version 1.2 -Notes "texto das notas"

  Passos:
    1. Preflight: gh instalado + autenticado, ISCC presente, .venv presente, arvore de trabalho limpa.
    2. Bump VERSION.txt = -Version (fonte unica lida pelo app e pelo Inno Setup).
    3. Commit "chore: release vX.Y".
    4. build.bat  -> dist\JW_Mural\ + installer_output\Setup_JW_Mural.exe
    5. git tag vX.Y ; push do commit ; push da tag.
    6. gh release create vX.Y com Setup_JW_Mural.exe anexado (nome exigido pelo updater).

  Qualquer falha aborta antes de publicar. Idempotencia: aborta se a tag ja existir.
#>
param(
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$Notes = ""
)

$ErrorActionPreference = "Stop"

function Fail($msg) { Write-Host "ERRO: $msg" -ForegroundColor Red; exit 1 }
function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

# Normaliza versao (sem 'v' no VERSION.txt; tag com 'v')
$Version = $Version.TrimStart('v', 'V').Trim()
if ($Version -notmatch '^\d+(\.\d+){1,3}$') { Fail "Versao invalida: '$Version'. Use algo como 1.2 ou 1.2.3." }
$Tag = "v$Version"

# Raiz do repo
$RepoRoot = (git rev-parse --show-toplevel 2>$null)
if (-not $RepoRoot) { Fail "Nao esta dentro de um repositorio git." }
Set-Location $RepoRoot

# ── Preflight ─────────────────────────────────────────────────────────────
Step "Preflight"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Fail "GitHub CLI (gh) nao encontrado. Instale com:  winget install GitHub.cli  e depois:  gh auth login"
}
gh auth status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "gh nao autenticado. Rode:  gh auth login" }

$ISCC = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $ISCC)) { Fail "Inno Setup 6 nao encontrado. Instale com: winget install JRSoftware.InnoSetup" }
if (-not (Test-Path ".venv\Scripts\python.exe")) { Fail ".venv nao encontrada (necessaria para PyInstaller)." }

# Tag ja existe?
$existing = (git tag --list $Tag)
if ($existing) { Fail "Tag $Tag ja existe. Escolha outra versao ou remova a tag." }

# Versao nova deve ser maior que a ULTIMA RELEASE publicada (baseline do updater).
# Compara com a maior tag existente; se nao houver nenhuma, qualquer versao serve.
function VerTuple($s) { ($s.TrimStart('v', 'V') -split '\.') | ForEach-Object { [int]$_ } }
$ultimaTag = (git tag --list "v*" | Sort-Object { $v = VerTuple $_; $v[0] * 1000000 + ($v[1]) * 1000 + ($(if ($v.Count -gt 2) { $v[2] } else { 0 })) } | Select-Object -Last 1)
if ($ultimaTag) {
    $na = VerTuple $Version; $nb = VerTuple $ultimaTag
    $len = [Math]::Max($na.Count, $nb.Count)
    while ($na.Count -lt $len) { $na += 0 }; while ($nb.Count -lt $len) { $nb += 0 }
    $maior = $false
    for ($i = 0; $i -lt $len; $i++) {
        if ($na[$i] -gt $nb[$i]) { $maior = $true; break }
        if ($na[$i] -lt $nb[$i]) { break }
    }
    if (-not $maior) { Fail "Versao $Version nao e maior que a ultima release ($ultimaTag). O updater so oferece versoes maiores." }
    Write-Host "   Ultima release: $ultimaTag  ->  nova: $Version"
} else {
    Write-Host "   Nenhuma release anterior; publicando $Version como primeira."
}

# Arvore de trabalho limpa (exceto VERSION.txt que vamos alterar)
$dirty = (git status --porcelain --untracked-files=no | Where-Object { $_ -notmatch 'VERSION\.txt$' })
if ($dirty) {
    Write-Host $dirty
    Fail "Ha alteracoes nao commitadas. Commite o codigo antes de gerar a release."
}

# ── Bump VERSION.txt ─────────────────────────────────────────────────────
Step "Bump VERSION.txt -> $Version"
# UTF-8 SEM BOM: version.py faz read().strip() (nao remove BOM) e o Inno le com FileRead.
[System.IO.File]::WriteAllText((Join-Path $RepoRoot "VERSION.txt"), "$Version`n", (New-Object System.Text.UTF8Encoding($false)))
git add -- VERSION.txt
# So commita se houve mudanca (a versao pode ja estar em VERSION.txt).
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "chore: release $Tag" | Out-Null
} else {
    Write-Host "   VERSION.txt ja em $Version; sem commit de versao."
}

# ── Build ────────────────────────────────────────────────────────────────
Step "Build (PyInstaller + Inno Setup)"
$bat = Join-Path $RepoRoot "build.bat"
cmd /c "`"$bat`""
if ($LASTEXITCODE -ne 0) { Fail "build.bat falhou (exit $LASTEXITCODE)." }

$Setup = "installer_output\Setup_JW_Mural.exe"
if (-not (Test-Path $Setup)) { Fail "Instalador nao gerado em $Setup." }
Write-Host "   Instalador: $Setup ($([math]::Round((Get-Item $Setup).Length/1MB,1)) MB)"

# ── Tag + push ───────────────────────────────────────────────────────────
Step "Tag + push"
git tag -a $Tag -m $Tag
git push origin HEAD
git push origin $Tag

# ── GitHub Release ───────────────────────────────────────────────────────
Step "Criando GitHub Release $Tag"
if (-not $Notes) { $Notes = "Release $Tag" }
gh release create $Tag $Setup --title $Tag --notes $Notes
if ($LASTEXITCODE -ne 0) { Fail "gh release create falhou." }

Write-Host ""
Write-Host "OK: release $Tag publicada. Os apps instalados vao oferecer a atualizacao no proximo boot." -ForegroundColor Green
