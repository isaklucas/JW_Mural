# JW Mural

Aplicação desktop (Windows) para gerar e gerenciar a programação das reuniões de congregações de Testemunhas de Jeová.

## O que faz

- **Extrai** a programação das reuniões do site oficial (wol.jw.org).
- **Gera documentos Word** prontos:
  - Reunião de meio de semana (S140).
  - Reunião de fim de semana (Sentinela + Oradores).
- **Atribui publicadores** às partes — manualmente ou por seleção automática (considera cargo, permissões e quem está há mais tempo sem participar).
- **Gerencia publicadores** (cadastro, permissões, histórico de participações).
- **Dashboards** com estatísticas de participação.

Os documentos são salvos em `documentosCriados/`.

## Requisitos

- Windows 10 ou superior
- Python 3.11+ (só para rodar em modo desenvolvimento)
- MongoDB rodando localmente (o instalador cuida disso automaticamente)

## Como rodar

### Opção A — Usuário final (instalador)

1. Execute `Setup_JW_Mural.exe` como **Administrador**.
2. O instalador instala o app, configura o MongoDB e inicializa o banco.
3. Abra pelo atalho criado na Área de Trabalho / Menu Iniciar.

O app instalado se **atualiza sozinho**: ao abrir, verifica se há versão nova e oferece baixar e instalar.

### Opção B — Desenvolvimento (a partir do código)

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/isaklucas/JW_Mural.git
cd JW_Mural

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
copy .env.example .env      # ajuste a MONGODB_URI se necessário

# 5. Rodar
python src/layout.py
```

> Precisa de um MongoDB acessível na `MONGODB_URI` do `.env` (padrão: `mongodb://localhost:27017/`).

## Configuração (`.env`)

Copie `.env.example` para `.env`. O `.env` **não** é versionado (pode conter usuário/senha do banco).

```env
DB_TYPE=mongodb
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=jw_mural
MONGODB_COLLECTION=publicadores
```

Suporta MongoDB (padrão) ou DynamoDB via `DB_TYPE`.

## Estrutura

```
JW_Mural/
├── src/                  # Código-fonte
│   ├── layout.py         # Interface gráfica (entrypoint)
│   ├── version.py        # Versão do app (lê VERSION.txt)
│   ├── process/          # Web scraping + geração dos documentos Word
│   ├── database/         # Acesso a dados (MongoDB / DynamoDB)
│   └── util/             # Diálogos, inicialização, updater
├── Templates/            # Modelos Word (.docx)
├── assets/               # Ícones e dados de autocomplete
├── Docs/                 # Documentação técnica (01..06)
├── VERSION.txt           # Versão do app (fonte única)
├── build.bat             # Gera o instalador
└── requirements.txt
```

## Build e atualizações

Gerar o instalador (requer PyInstaller e Inno Setup):

```bat
build.bat
```

Publicar uma nova versão (o app instalado detecta automaticamente):

1. Editar `VERSION.txt` (ex.: `1.1`).
2. Rodar `build.bat`.
3. `gh release create v1.1 installer_output/Setup_JW_Mural.exe -t "v1.1" -n "Notas"`.

Detalhes completos: **[Docs/06-Build-e-Instalador.md](Docs/06-Build-e-Instalador.md)**.

## Documentação

Documentação técnica em **[Docs/](Docs/README.md)**: arquitetura, banco de dados, módulos, fluxos, telas e build.

---

Uso interno para congregações de Testemunhas de Jeová.
