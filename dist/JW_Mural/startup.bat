@echo off
echo Iniciando JW Mural...
echo.

:: Verificar se os diretórios necessários existem
if not exist "documentosCriados" mkdir documentosCriados
if not exist "Templates" mkdir Templates
if not exist "util" mkdir util
if not exist "process" mkdir process
if not exist "database" mkdir database
if not exist "assets" mkdir assets

:: Verificar o arquivo .env
if not exist ".env" (
    echo Criando arquivo .env padrão...
    echo # Arquivo de configuração do JW Mural > .env
    echo MONGODB_URI=mongodb://localhost:27017 >> .env
    echo DB_NAME=jw_mural >> .env
    echo COLLECTION_NAME=reunioes >> .env
    echo DB_TYPE=mongodb >> .env
    echo MONGODB_DB_NAME=jw_mural >> .env
    echo MONGODB_COLLECTION=reunioes >> .env
)

:: Iniciar o programa
start JW_Mural.exe

echo Programa iniciado!
pause 