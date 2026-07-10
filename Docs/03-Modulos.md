# Módulos

Descrição das pastas e arquivos principais do projeto.

## layout.py

Ponto de entrada e **menu principal** (~320 linhas). Contém a classe `ModernApp`, que monta a janela com cards (Criar Reunião Meio/Final de Semana, Publicadores, Histórico de Publicadores, Histórico Meio/Final de Semana, Designações Salão, Dashboards) e faz o bootstrap. As telas em si **não** ficam aqui: `ModernApp` as herda de mixins em `views/`. A execução de `layout.py` cria a janela ttkbootstrap, instancia `ModernApp` e roda as verificações de startup (`util.startup_manager`); no app compilado dispara a checagem de atualização.

## views/

Interface — uma tela por módulo, cada uma um *mixin* de `ModernApp`.

- **components.py** — `criar_card`: constrói cada card do menu. O card **inteiro é clicável** (não há botão "ACESSAR"); faixa de cor no topo identifica a categoria; cursor de mão e hover dão o affordance.
- **_shared.py** — imports compartilhados pelas telas (`from views._shared import *`): ttk/tk, constantes, `Messagebox`, `s140`, `final_semana` e os *serviços*. As telas obtêm o acesso a dados por aqui, não por `database`.
- **publicadores_view.py** — `PublicadoresMixin`: telas `publicadores` e `historico_publicadores`.
- **historico_view.py** — `HistoricoMixin`: `historico` e `historico_final_semana`.
- **reunioes_view.py** — `ReunioesMixin`: `criar_quadro_de_anuncio` (meio de semana) e `criar_reuniao_final_semana`.
- **designacoes_view.py** — `DesignacoesMixin`: `designacoes_salao` (áudio, vídeo, microfone, indicadores).
- **dashboards_view.py** — `DashboardsMixin`: `dashboards`.
- **config_view.py** — `ConfigMixin`: `abrir_configuracoes`.

## services/

Camada de serviço — **única parte da UI que importa `database`/`db_ops`**. As telas chamam estes serviços (singletons) em vez de acessar o banco direto.

- **publicador_service.py** — `publicador_service`: listar, adicionar, excluir, atualizar, buscar_historico, resetar_todo_historico, restaurar_historico.
- **reuniao_service.py** — `reuniao_service`: listar/buscar/salvar reuniões + variantes `_final_semana`.
- **designacao_service.py** — `designacao_service`: listar_candidatos, salvar, listar, buscar, excluir.
- **dashboard_service.py** — `dashboard_service`: contagens para os gráficos.

## tests/

Suíte pytest offline (não precisa de MongoDB). `conftest.py` injeta um módulo `database` falso em `sys.modules` antes dos imports. `test_webscrapper.py` (parser via fixtures HTML) e `test_designacao.py` (designação automática). Rodar: `python -m pytest`. Deps de dev em `requirements-dev.txt`.

## database/

**db_connection.py** — Conexão com MongoDB ou DynamoDB conforme `.env`; garante existência das collections `reunioes` e `reunioes_final_semana` no MongoDB. Expõe `get_connection()` (collection ou tabela de publicadores).

**db_operations.py** — CRUD de publicadores, salvamento/busca de reuniões (meio e final de semana), atualização de histórico, listagens, contagens e métodos para seleção automática (por permissão, anciãos/servos, “quem fez menos”). Cria índices em `reunioes` e `reunioes_final_semana`.

**__init__.py** — Exporta `db_ops` e funções (post, getAllPub, delete, salvar_reuniao, listar_reunioes, salvar_reuniao_final_semana, etc.).

**init_db.py** — Inicialização do banco; índices principais estão em `DatabaseOperations.__init__` em db_operations.

## process/

**s140.py** — Reunião de meio de semana: webscrapper para obter HTML, extração de partes, preenchimento manual ou automático de publicadores, geração do Word (Template_PT.docx), salvamento em documentosCriados/ e atualização de reunião e histórico via db_ops.

**final_semana.py** — Reunião final de semana: extração de títulos da Sentinela (webscrapper), seleção automática de presidente (anciãos/servos) e leitor (leitura_sentinela), modais para dirigente e dados (tema, orador, presidente, leitor) com autocomplete de temas a partir de assets/temas_discursos.json, geração de dois Word (Sentinela e Oradores) a partir dos templates em Templates/, salvamento em documentosCriados/ e em reunioes_final_semana.

**webscrapper.py** — Requisições ao wol.jw.org e parsing (BeautifulSoup); extração de títulos do estudo da Sentinela na página de meetings. Usado por s140 e final_semana. Rede robusta: sessão HTTP com `timeout`, `User-Agent` e retry/backoff; falha de rede vira retorno `None` (sem travar a UI) e há aviso em log quando a estrutura do site muda (0 cards).

## util/

**system_checks.py** — Verificação de diretórios e arquivos obrigatórios (assets, Templates, .env, templates Word).

**startup_manager.py** — Janela de loading e execução das verificações no arranque; criação de diretórios se necessário.

**janelas.py** — Diálogos para solicitar nome de publicador (com lista filtrável) e outros modais reutilizáveis.

**db_utils.py** — Utilitários de banco.

**comandosUteis.py** — Funções como `TitleCase` para formatação de nomes; usadas em db_operations.

## assets/

Ícone da aplicação (icon.ico) e **temas_discursos.json** (array de strings "N. Título do tema") para autocomplete do campo Tema Discurso no modal de final de semana. Carregado por `final_semana._carregar_temas_discursos()`.

## Templates/

**Template_PT.docx** — Reunião meio de semana (placeholders p01, p02, …). **template_final_semana_sentinela.docx** e **template_final_semana_oradores.docx** — Final de semana (w_dirigente, w1..w9). Arquivos só leitura; saída em documentosCriados/.
