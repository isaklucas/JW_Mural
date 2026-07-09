; JW_Mural.iss — Inno Setup 6
; Compile com: ISCC.exe JW_Mural.iss

#define AppName "JW Mural"
; Versao lida de VERSION.txt (fonte unica de verdade, compartilhada com o app)
#define FH FileOpen("VERSION.txt")
#define AppVersion Trim(FileRead(FH))
#expr FileClose(FH)
#define AppPublisher "Congregacao JW"
#define AppExeName "JW_Mural.exe"
#define SourceDir "dist\JW_Mural"
#define OutputDir "installer_output"

[Setup]
AppId={{F3A2D1B4-7C8E-4F90-A1B2-C3D4E5F67890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir={#OutputDir}
OutputBaseFilename=Setup_JW_Mural
SetupIconFile=assets\jw_mural_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
MinVersion=10.0.17763
; Permite atualizar por cima da versao em execucao: o Inno usa o Restart Manager
; para fechar qualquer instancia que ainda esteja segurando arquivos em {app}.
; NAO usar AppMutex: ele exibe a mensagem "app em execucao / clique OK", que entra
; em loop infinito quando o proprio app dispara o instalador (ver src/util/updater.py).
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Atalhos adicionais:"; Flags: unchecked

[Dirs]
Name: "{app}\documentosCriados"
Name: "{app}\Templates"
Name: "{app}\assets"

[Files]
; App completo gerado pelo PyInstaller
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Templates obrigatorios (garantia explicita)
Source: "Templates\*"; DestDir: "{app}\Templates"; Flags: ignoreversion
; Assets obrigatorios
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs
; .env do projeto
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion
; Script OPCIONAL para instalar o MongoDB manualmente (dependencia externa)
Source: "install_mongo.ps1"; DestDir: "{app}"; Flags: ignoreversion
; Versao ao lado do exe (o app le para checar atualizacoes)
Source: "VERSION.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; MongoDB NAO e instalado pelo setup — e dependencia manual (ver README).
; O app cria as colecoes no primeiro acesso; install_mongo.ps1 fica em {app}
; para instalacao manual opcional do MongoDB.

; Abre o app ao final (opcional)
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName} agora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\documentosCriados"
Type: filesandordirs; Name: "{app}\__pycache__"
