# Arquitetura

Visão geral da organização do JW Mural.

## Entrada

A aplicação inicia em **layout.py**: cria a janela principal (ttkbootstrap, tema litera), configura fonte dos botões, instancia **ModernApp** e inicia o loop. Após a janela estar visível, executa verificações de startup via **util.startup_manager** (diretórios, arquivos, banco).

## Camadas

**UI** — Toda a interface em **layout.py** (ModernApp, cards, janelas, formulários, modais). Chama diretamente process e db_ops.

**Process** — **process/** contém regras e geração: **s140** (meio de semana), **final_semana** (final de semana), **webscrapper** (wol.jw.org). Usam **database.db_ops** para ler/gravar dados.

**Database** — **database/db_connection.py** (conexão) e **db_operations.py** (CRUD, reuniões, histórico). O projeto usa a instância **db_ops** para todos os acessos.

**Util** — **util/**: system_checks, startup_manager, janelas, db_utils, comandosUteis. Usados por layout e process quando necessário.

## Fluxo de dados

Usuário age em layout -> layout chama process (s140 ou final_semana) -> process usa webscrapper e db_ops -> documentos gerados em process a partir de Templates/, gravados em documentosCriados/. Reuniões e histórico persistidos via db_ops.

## Diagrama

- layout.py -> process.s140 / process.final_semana
- process -> webscrapper + database.db_ops
- final_semana usa assets/temas_discursos.json
- layout e process usam util (checks, janelas, etc.)

Conexão ao banco em database/db_connection.py; operações em database/db_operations.py.
