@echo off
setlocal EnableDelayedExpansion

echo ================================================
echo  JW Mural - Build Pipeline
echo ================================================

:: --- Converte icone PNG -> ICO (necessario uma vez) ---
if not exist "assets\jw_mural_icon.ico" (
    echo [0/3] Convertendo icone PNG para ICO...
    .venv\Scripts\python.exe -c "from PIL import Image; img=Image.open('assets/jw_mural_icon_40x40.png').convert('RGBA'); img.save('assets/jw_mural_icon.ico', format='ICO', sizes=[(16,16),(32,32),(48,48),(256,256)])"
    if errorlevel 1 (
        echo ERRO: Falha ao converter icone. Verifique se Pillow esta instalado.
        exit /b 1
    )
    echo Icone convertido: assets\jw_mural_icon.ico
)

:: --- Limpa builds anteriores ---
echo [1/3] Limpando dist\ e build\...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: --- PyInstaller ---
echo [2/3] Executando PyInstaller...
.venv\Scripts\python.exe -m PyInstaller JW_Mural.spec
if errorlevel 1 (
    echo ERRO: PyInstaller falhou.
    exit /b 1
)
echo PyInstaller OK - dist\JW_Mural\ pronto.

:: --- Inno Setup ---
echo [3/3] Compilando instalador com Inno Setup...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo ERRO: Inno Setup 6 nao encontrado em %ISCC%
    echo Instale com: winget install JRSoftware.InnoSetup
    exit /b 1
)

if not exist installer_output mkdir installer_output
%ISCC% JW_Mural.iss
if errorlevel 1 (
    echo ERRO: Inno Setup falhou.
    exit /b 1
)

echo.
echo ================================================
echo  BUILD COMPLETO
echo  Saida: installer_output\Setup_JW_Mural.exe
echo ================================================
