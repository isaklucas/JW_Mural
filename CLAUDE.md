# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run application
python src/layout.py

# Build executable + installer
build.bat

# Initialize DB schema
python src/database/init_db.py

# System checks
python src/util/system_checks.py

# Run tests (offline — não precisa de MongoDB)
python -m pytest
```

Tests em `tests/` (pytest): parser do scraper + designação automática. Rodam offline via um módulo `database` falso injetado em `sys.modules` (`tests/conftest.py`). Deps de dev: `pip install -r requirements-dev.txt`. No linter configured.

## Architecture

Desktop app (Windows-primary) for managing JW congregation meeting schedules: scrapes wol.jw.org, assigns publishers to meeting parts, generates Word documents.

### Entry Point

`src/layout.py` (~320 lines) — `ModernApp` class: main menu + bootstrap. ttkbootstrap GUI. Long operations (scraping, doc generation) run in background threads to avoid UI freeze.

`ModernApp` inherits its screens from per-screen **mixins** in `src/views/` (SDD 03 decomposition — the class used to be one ~3600-line file):

- `views/components.py` — `criar_card` (card + ACESSAR button builder).
- `views/_shared.py` — shared imports for the mixins (`from views._shared import *`).
- `views/publicadores_view.py` — `PublicadoresMixin` (`publicadores`, `historico_publicadores`).
- `views/historico_view.py` — `HistoricoMixin` (`historico`, `historico_final_semana`).
- `views/reunioes_view.py` — `ReunioesMixin` (`criar_quadro_de_anuncio`, `criar_reuniao_final_semana`).
- `views/designacoes_view.py` — `DesignacoesMixin` (`designacoes_salao`).
- `views/dashboards_view.py` — `DashboardsMixin` (`dashboards`).
- `views/config_view.py` — `ConfigMixin` (`abrir_configuracoes`).

The screen mixins never touch `database`/`db_ops` directly — they go through the **service layer** in `src/services/` (`publicador_service`, `reuniao_service`, `designacao_service`, `dashboard_service`), which is the only UI-side code that imports `database`. Add a new DB operation there, not in a view.

### Modules

**`src/process/s140.py`** — Midweek meeting (S140 form) generator. Fetches meeting program from wol.jw.org via `webscrapper`, fills placeholders in `Templates/Template_PT.docx`, assigns publishers manually (dialog) or automatically (role-based: Elder, Ministerial Servant, etc.), saves to `documentosCriados/`.

**`src/process/final_semana.py`** — Weekend meeting generator. Same placeholder approach with two templates: `template_final_semana_sentinela.docx` (Watchtower study) and `template_final_semana_oradores.docx` (Speakers).

**`src/process/webscrapper.py`** — Scrapes `wol.jw.org`. Key method: `extrair_titulos_sentinela_meetings(url, qtd_semanas=5)`. URL format: `https://wol.jw.org/pt/wol/meetings/r5/lp-t/YYYY/M`.

**`src/database/`** — `db_operations.py` has `DatabaseOperations` class; `__init__.py` exports flat functions. Supports MongoDB (default) or DynamoDB via `DB_TYPE` env var.

**`src/util/`** — `janelas.py` (custom dialogs), `startup_manager.py` (init logic), `system_checks.py` (env validation), `db_utils.py` (helpers).

### Data Collections

- `publicadores` — publisher list with participation history
- `reunioes` — midweek meeting records
- `reunioes_final_semana` — weekend meeting records

### Templates

Word `.docx` files in `Templates/` use placeholder markers (e.g. `{participante}`, `{data}`). Output goes to `documentosCriados/`.

## Configuration

`.env` file required:

```
DB_TYPE=mongodb
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=jw_mural
MONGODB_COLLECTION=publicadores
# DynamoDB alternative:
# DB_TYPE=dynamodb
# AWS_REGION=us-east-1
# DYNAMODB_TABLE=publicadores
```

## Conventions

- Variable/function names in Portuguese
- Classes: PascalCase; methods: camelCase
- `assets/temas_discursos.json` — autocomplete data for discourse themes
