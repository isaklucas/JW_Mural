# Build e Instalador

## Visão Geral

O pipeline de distribuição gera um único arquivo `Setup_JW_Mural.exe` que instala o app completo, configura MongoDB e inicializa o banco.

```
build.bat
  └─ PyInstaller (JW_Mural.spec)  →  dist\JW_Mural\
  └─ Inno Setup  (JW_Mural.iss)   →  installer_output\Setup_JW_Mural.exe
```

## Pré-requisitos para Build

| Ferramenta | Instalação |
|-----------|-----------|
| Python 3.11+ com venv ativo | `winget install Python.Python.3.12` |
| Dependências do projeto | `.venv\Scripts\pip install -r requirements.txt` |
| Inno Setup 6 | `winget install JRSoftware.InnoSetup` |

Verificar que `.venv\` existe e tem `PyInstaller`:
```bat
.venv\Scripts\python.exe -m PyInstaller --version
```

## Gerar o Instalador

Na raiz do projeto, como Administrador:

```bat
build.bat
```

O script executa 3 etapas:

1. **Converte ícone** — `assets\jw_mural_icon_40x40.png` → `assets\jw_mural_icon.ico` (só na primeira vez)
2. **PyInstaller** — empacota `layout.py` e todas as dependências em `dist\JW_Mural\`
3. **Inno Setup** — compila `JW_Mural.iss` e gera `installer_output\Setup_JW_Mural.exe`

Saída final: `installer_output\Setup_JW_Mural.exe` (~53 MB)

## O que o Instalador Faz

Ao executar `Setup_JW_Mural.exe` no PC do usuário:

1. Instala o app em `C:\Program Files\JW Mural\`
2. Copia Templates, assets e `.env`
3. Executa `install_mongo.ps1` — instala/inicia MongoDB via winget se necessário
4. Executa `JW_Mural.exe --init-db` — cria collections e índices no banco
5. Oferece abrir o app ao final

**Requer:** Windows 10 1809+ (build 17763), execução como Administrador.

## Arquivos do Pipeline

| Arquivo | Função |
|---------|--------|
| `build.bat` | Orquestra PyInstaller + Inno Setup |
| `JW_Mural.spec` | Config PyInstaller: entrypoint, dados bundlados, hidden imports |
| `JW_Mural.iss` | Config Inno Setup: instalação, atalhos, pós-instalação |
| `install_mongo.ps1` | Bundlado no installer; instala/inicia MongoDB no destino |

## Modificar Configurações

### Versão do app
Fonte única de verdade: arquivo `VERSION.txt` na raiz. Editar só ele:
```
1.1
```
O `JW_Mural.iss` lê esse arquivo via ISPP (`FileOpen`/`FileRead`) e o app lê o
mesmo `VERSION.txt` (bundlado pelo PyInstaller e copiado ao lado do exe) via
`src/version.py` (`__version__`). Não editar a versão em mais nenhum lugar.

### Adicionar arquivos ao bundle
Editar `JW_Mural.spec`, seção `datas`:
```python
datas=[
    ('assets', 'assets'),
    ('Templates', 'Templates'),
    # adicionar aqui
],
```

### Diretório de instalação padrão
Editar `JW_Mural.iss`:
```ini
DefaultDirName={autopf}\{#AppName}
```

## Atualizações Automáticas (GitHub Releases)

O app instalado verifica atualizações ao abrir. Se houver um release mais novo
no GitHub, avisa o usuário, baixa o novo `Setup_JW_Mural.exe` e o executa — o
Inno Setup fecha a instância aberta (via mutex `JW_Mural_Running`) e atualiza
por cima.

**Componentes:**
| Peça | Papel |
|------|-------|
| `src/version.py` | Expõe `__version__` (lê `VERSION.txt`) |
| `src/util/updater.py` | Consulta a API do GitHub, compara versão, baixa e lança o instalador |
| `layout.py` (`start_checks`) | Dispara o check em background só no app compilado (`frozen`) |
| `JW_Mural.iss` | `CloseApplications` + `AppMutex=JW_Mural_Running` para substituir o app em uso |

**Pré-requisito:** o repositório (ou ao menos os releases) precisa ser
**público** — a API `releases/latest` é consultada sem token (limite 60 req/h
por IP, suficiente). Repo em `github.com/isaklucas/JW_Mural` (ver `GITHUB_REPO`
em `src/util/updater.py`).

### Publicar uma nova versão

1. Editar `VERSION.txt` (ex.: `1.1`) e commitar.
2. Rodar `build.bat` — gera `installer_output\Setup_JW_Mural.exe` já com a nova versão.
3. Criar o release no GitHub anexando o instalador (o asset **precisa** se chamar `Setup_JW_Mural.exe`):
   ```bash
   gh release create v1.1 installer_output/Setup_JW_Mural.exe -t "v1.1" -n "Notas da versão"
   ```
4. Pronto: todos os apps instalados detectam e oferecem a atualização na próxima abertura.

## Troubleshooting

**"Inno Setup não encontrado"**
```bat
winget install JRSoftware.InnoSetup
```
Caminho esperado: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

**"PyInstaller falhou"**
- Verificar que `.venv` está ativo e `requirements.txt` instalado
- Rodar manualmente para ver erro: `.venv\Scripts\python.exe -m PyInstaller JW_Mural.spec`

**"Ícone não encontrado"**
- Verificar que `assets\jw_mural_icon_40x40.png` existe
- Ou colocar `assets\jw_mural_icon.ico` diretamente para pular conversão

**Installer gerado mas MongoDB não instala no destino**
- `install_mongo.ps1` requer winget e conexão com internet no PC destino
- Alternativa: instalar MongoDB manualmente antes de rodar o installer
