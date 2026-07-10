# JW Mural - Guia para Agentes IA

## Visão Executiva

O **JW Mural** é uma aplicação desktop Python para congregações de Testemunhas de Jeová. O sistema extrai automaticamente dados de reuniões do site wol.jw.org, gera documentos Word (S140) com a programação completa e gerencia uma base de publicadores com histórico de participações. Suporta seleção manual ou automática de publicadores para cada parte da reunião, respeitando critérios (Ancião, Servo Ministerial, permissões, sexo) e priorizando quem está há mais tempo sem participar.

## Ponto de Entrada

- **Arquivo principal:** `src/layout.py` (menu + bootstrap, ~320 linhas)
- **Execução:** `python src/layout.py` ou `JW_Mural.exe`
- **Inicialização:** cria janela ttkbootstrap → `ModernApp(root)` → verificações de startup
- **`ModernApp`** herda as telas de mixins em `views/`:
  `class ModernApp(PublicadoresMixin, HistoricoMixin, ReunioesMixin, DesignacoesMixin, DashboardsMixin, ConfigMixin)`

## Módulos Principais

| Módulo | Responsabilidade |
|--------|-------------------|
| `layout.py` | Menu principal (cards clicáveis) + bootstrap; herda as telas dos mixins |
| `views/*_view.py` | Telas (uma por mixin): publicadores, histórico, reuniões, designações, dashboards, config |
| `views/components.py` | Construtor de card (card inteiro clicável, sem botão "ACESSAR") |
| `views/_shared.py` | Imports compartilhados pelas telas (incl. os serviços) |
| `services/*_service.py` | **Camada de dados da UI** — única parte da UI que fala com `database`/`db_ops` |
| `process/s140.py` | Extração do HTML, geração de documentos Word, seleção de publicadores |
| `process/webscrapper.py` | HTTP + parsing (BeautifulSoup) do wol.jw.org, com timeout/retry |
| `database/db_operations.py` | CRUD de publicadores e reuniões, seleção automática por critérios |
| `database/db_connection.py` | Conexão MongoDB ou DynamoDB |
| `util/janelas.py` | Diálogos modais (seleção de publicador, confirmações) |
| `util/startup_manager.py` | Verificações de sistema na inicialização |
| `util/updater.py` | Auto-update via GitHub Releases (só no app `frozen`) |
| `tests/` | pytest offline (scraper + designação); `database` falso em `sys.modules` |

## Fluxo Principal: Criação de Reunião

1. Usuário preenche URL, quantidade de semanas, nome do arquivo e opções (utilizar base, seleção automática)
2. `s140.gerar_s140()` → `buscarSoupDasSemnas()` → `extrair_partes()`
3. Se `preencherPubs` e `gerarComPublicadores`: `selecionar_publicadores_automaticamente()` → `mostrar_resumo_e_editar_publicadores()`
4. Se `preencherPubs` e não automático: `solicitarNomePublicadorPartes()` (diálogos manuais)
5. `criarDocumentoApartirDoObjeto()` → substitui placeholders p01-p45 no template → salva em `documentosCriados/`
6. Se preenchido: `atualizarHistoricoPublicadores()` → `salvar_reuniao()` no banco

## Documentação Detalhada

- **Para humanos:** [README.md](README.md) — instalação, uso, troubleshooting
- **Para IA/desenvolvedores:** [README_IA.md](README_IA.md) — arquitetura, fluxos, modelos de dados, APIs

## Regras de Ouro para Modificações

1. **Nova tela / mexer em tela existente:** editar o mixin em `views/` correspondente (uma tela por módulo). Não voltar a inchar `layout.py` — ele é só menu + bootstrap. Widgets reutilizáveis vão em `views/components.py`.
2. **Acesso a banco na UI:** as telas **não** importam `database`/`db_ops`. Nova operação de banco vai num `services/*_service.py`; a tela chama o serviço. Manter `grep "db_ops\|from database" src/views/*.py` = vazio.
3. **Handlers que fecham janela:** nunca passar uma janela possivelmente destruída como `parent=` de `Messagebox` (quebra o dialog e deixa *grab* pendente, travando cliques em modais). Guardar com `winfo_exists()`. Ver `historico_view.salvar_reuniao`.
4. **Testes:** rodar `python -m pytest` (offline). Lógica pura nova (parser, designação) ganha teste. Os testes usam um `database` falso em `sys.modules` (`tests/conftest.py`).
5. **Placeholders do template:** p01-p23 (conteúdo), p34-p45 (publicadores). Não alterar numeração sem atualizar `Templates/Template_PT.docx`.
6. **Threading:** operações longas (scraping, geração de documento) em thread separada para não travar a UI.
7. **Nomes:** normalizar com `util.ComandosUteis.TitleCase()` antes de salvar.
8. **Banco:** manter compatibilidade MongoDB e DynamoDB; verificar `db_type` em operações específicas.
9. **Múltiplos publicadores:** formato "Nome1 / Nome2" para partes com dois participantes.
10. **Build:** ao adicionar um pacote novo em `src/`, incluí-lo no `JW_Mural.spec` (`datas` + `hiddenimports`) — como `views`/`services`. `build.bat` e `JW_Mural.iss` não precisam mudar.

## Gotchas conhecidos

- **ttkbootstrap re-tematiza `tk.Button`:** sob um tema, o `bg` passado no construtor vira `primary`. Para colorir um `tk.Button`, use `.configure(bg=...)` **após** criar. (Botões `ttk.Button` às vezes não mostram texto no Windows — daí o uso de `tk.Button`.)
- **Importar `database` conecta no Mongo** (no import de `db_ops`). Por isso testes/headless injetam um `database` falso em `sys.modules` antes de importar módulos de produção.
