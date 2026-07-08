# Módulos

Descrição das pastas e arquivos principais do projeto.

## layout.py

Interface gráfica principal e ponto de entrada. Contém a classe `ModernApp`, que monta a janela com cards: Criar Reunião Meio de Semana, Criar Reunião Final de Semana, Publicadores, Histórico de Publicadores, Histórico Meio/Final de Semana, Dashboards. Cada card abre a janela ou fluxo correspondente e chama `process.s140`, `process.final_semana` e `database.db_ops`. A execução de `layout.py` cria a janela ttkbootstrap, instancia `ModernApp` e roda as verificações de startup (`util.startup_manager`).

## database/

**db_connection.py** — Conexão com MongoDB ou DynamoDB conforme `.env`; garante existência das collections `reunioes` e `reunioes_final_semana` no MongoDB. Expõe `get_connection()` (collection ou tabela de publicadores).

**db_operations.py** — CRUD de publicadores, salvamento/busca de reuniões (meio e final de semana), atualização de histórico, listagens, contagens e métodos para seleção automática (por permissão, anciãos/servos, “quem fez menos”). Cria índices em `reunioes` e `reunioes_final_semana`.

**__init__.py** — Exporta `db_ops` e funções (post, getAllPub, delete, salvar_reuniao, listar_reunioes, salvar_reuniao_final_semana, etc.).

**init_db.py** — Inicialização do banco; índices principais estão em `DatabaseOperations.__init__` em db_operations.

## process/

**s140.py** — Reunião de meio de semana: webscrapper para obter HTML, extração de partes, preenchimento manual ou automático de publicadores, geração do Word (Template_PT.docx), salvamento em documentosCriados/ e atualização de reunião e histórico via db_ops.

**final_semana.py** — Reunião final de semana: extração de títulos da Sentinela (webscrapper), seleção automática de presidente (anciãos/servos) e leitor (leitura_sentinela), modais para dirigente e dados (tema, orador, presidente, leitor) com autocomplete de temas a partir de assets/temas_discursos.json, geração de dois Word (Sentinela e Oradores) a partir dos templates em Templates/, salvamento em documentosCriados/ e em reunioes_final_semana.

**webscrapper.py** — Requisições ao wol.jw.org e parsing (BeautifulSoup); extração de títulos do estudo da Sentinela na página de meetings. Usado por s140 e final_semana.

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
