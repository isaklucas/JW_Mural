# Banco de Dados

O JW Mural suporta dois backends: **MongoDB** (recomendado) e **AWS DynamoDB**. A conexão e o tipo de banco são definidos em `.env` e usados em `database/db_connection.py` e `database/db_operations.py`.

## MongoDB

Um único banco (nome configurável por `MONGODB_DB_NAME`, padrão `jw_mural`) contém três collections.

### Collection: `publicadores`

Armazena os publicadores da congregação.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `nome` | string | Nome do publicador (chave única; usado em buscas e título). |
| `batizado` | boolean | Se é batizado. |
| `Anciao` | boolean | Se é ancião. |
| `Servo_Ministerial` | boolean | Se é servo ministerial. |
| `sexo` | string | Ex.: `"Masculino"`, `"Feminino"`. |
| `permissoes` | objeto | `parte_escola`, `oracao`, `leitura_livro`, `leitura_sentinela`, `presidente_final_semana` (boolean cada). |
| `data_inclusao` | string | Data de inclusão (ISO). |
| `ultima_parte` | string | Texto da última parte realizada (legado/informativo). |
| `historico` | array | Lista de `{ "parte": string, "data": string }` (ex.: `"Presidente"`, `"Semana 1 de Janeiro de 2026"`). |

- **Índices:** não há índice único explícito em `publicadores`; o nome é usado como identificador.
- A collection é a mesma usada por `db_connection.get_connection()` em modo MongoDB.

### Collection: `reunioes`

Reuniões de **meio de semana**. Chave lógica: `ano` + `semana`.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ano` | number | Ano da reunião. |
| `semana` | string | Ex.: `"SEMANA 1"`, `"SEMANA 2"`. |
| `data_reuniao` | string | Data da reunião. |
| `presidente` | string | Nome do presidente. |
| `oracao_inicial` | string | Nome do designado. |
| `tesouro` | string | Idem. |
| `joias_espirituais` | string | Idem. |
| `leitura_biblia` | string | Idem. |
| `escola` | objeto | `primeira_parte`, `segunda_parte`, `terceira_parte`, `quarta_parte` (nomes). |
| `nossa_vida_crista` | objeto | `primeira_parte`, `segunda_parte` (nomes). |
| `estudo_congregacao` | string | Nome do condutor. |
| `oracao_final` | string | Nome do designado. |
| `ultima_atualizacao` | string | ISO. |

- **Índice:** `(ano, semana)` único (criado em `db_operations.__init__`).

### Collection: `reunioes_final_semana`

Reuniões de **final de semana**. Uma entrada por ano/mês; chave lógica: `ano` + `mes`.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ano` | number | Ano. |
| `mes` | number | Mês (1–12). |
| `semanas` | array | Lista de objetos por semana: `titulo_estudo`, `tema_discurso`, `orador`, `presidente`, `leitor_sentinela`, etc. |
| `ultima_atualizacao` | string | ISO. |

- **Índice:** `(ano, mes)` único.
- Ao salvar, o sistema atualiza o histórico dos publicadores (presidente e leitor da Sentinela) com partes `"Presidente Final Semana"` e `"Leitura Sentinela"`.

---

## DynamoDB

- **Tabela:** uma única tabela (nome em `DYNAMODB_TABLE`, normalmente `publicadores`) armazena os **publicadores** com a mesma estrutura lógica (nome, batizado, Anciao, Servo_Ministerial, sexo, permissoes, data_inclusao, ultima_parte, historico).
- **Chave primária:** `nome` (string).
- **Reuniões:** o código de reunião de meio de semana e de final de semana que usa `self.db['reunioes']` e `self.db['reunioes_final_semana']` está preparado para MongoDB. Em modo DynamoDB, `get_connection()` retorna a tabela de publicadores; as operações que usam `reunioes` ou `reunioes_final_semana` não estão implementadas para DynamoDB (ex.: `salvar_reuniao_final_semana` retorna erro indicando suporte apenas MongoDB). Ou seja: **reunioes e reunioes_final_semana existem apenas no MongoDB**.

---

## Referências no código

- Conexão e escolha MongoDB/DynamoDB: `database/db_connection.py`.
- CRUD, reuniões, histórico, listagens e seleção automática: `database/db_operations.py`.
- Criação de collections e índices (MongoDB): `DatabaseOperations.__init__` em `db_operations.py`.
