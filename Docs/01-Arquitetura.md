# Arquitetura

Visão geral da organização do JW Mural.

## Entrada

A aplicação inicia em **src/layout.py**: cria a janela principal (ttkbootstrap, tema litera), instancia **ModernApp** e inicia o loop. Após a janela estar visível, executa verificações de startup via **util.startup_manager** (diretórios, arquivos, banco). No app compilado (`frozen`), também dispara em background a checagem de atualização (**util.updater**).

`layout.py` é enxuto (~320 linhas): contém só o **menu principal** (cards) e o bootstrap. As telas em si foram extraídas para mixins em **src/views/** (ver Camadas).

## Camadas

**UI** — **src/views/**. Cada tela é um *mixin* de `ModernApp` (um módulo por tela); `layout.py` monta o menu e herda as telas. **views/components.py** tem o construtor de card. **views/_shared.py** centraliza os imports das telas. A UI **não** acessa o banco direto — fala com a camada de serviço.

**Services** — **src/services/**. Única parte da UI que importa `database`/`db_ops`. `publicador_service`, `reuniao_service`, `designacao_service`, `dashboard_service` encapsulam as operações de banco usadas pelas telas.

**Process** — **src/process/**: **s140** (meio de semana), **final_semana** (final de semana), **webscrapper** (wol.jw.org, com timeout/retry). Usam **database.db_ops** para ler/gravar dados. (Process ainda usa `db_ops` direto; a camada de serviço cobre as telas.)

**Database** — **src/database/db_connection.py** (conexão) e **db_operations.py** (CRUD, reuniões, histórico). Instância única **db_ops** para todos os acessos.

**Util** — **src/util/**: system_checks, startup_manager, janelas, db_utils, comandosUteis, updater, backup.

**Testes** — **tests/**: pytest offline (parser do scraper + designação automática). Injeta um `database` falso em `sys.modules` para rodar sem MongoDB. Ver `pytest.ini`, `tests/conftest.py`.

## Fluxo de dados

Usuário age numa tela (views) → tela chama `process` (s140/final_semana) e/ou os `services` → process usa webscrapper + db_ops → documentos gerados a partir de `Templates/`, gravados em `documentosCriados/`. Reuniões e histórico persistidos via services/db_ops.

## Diagrama

- `layout.py` (menu) → herda telas de `views/*_view.py` (mixins)
- `views/*` → `services/*` → `database.db_ops`
- `views/reunioes_view` → `process.s140` / `process.final_semana`
- `process` → `webscrapper` + `database.db_ops`
- `final_semana` usa `assets/temas_discursos.json`
- todos usam `util` (checks, janelas, etc.)

Conexão ao banco em `database/db_connection.py`; operações em `database/db_operations.py`.
