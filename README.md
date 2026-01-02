# JW Mural

Sistema de Gerenciamento de Reuniões de Meio de Semana para Congregações de Testemunhas de Jeová.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Build e Deploy](#build-e-deploy)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)

## 🎯 Sobre o Projeto

O **JW Mural** é uma aplicação desktop desenvolvida em Python que automatiza a criação e gerenciamento de documentos de programação para reuniões de meio de semana. O sistema:

- Extrai automaticamente informações das reuniões do site oficial (wol.jw.org)
- Gera documentos Word formatados com a programação completa
- Gerencia uma base de dados de publicadores
- Mantém histórico de participações nas reuniões
- Fornece dashboards com estatísticas e visualizações

### Público-Alvo

- Secretários de congregação
- Coordenadores de reuniões
- Superintendentes de serviço de campo

## ✨ Funcionalidades

### 1. Criar Reunião
- Extração automática de dados do wol.jw.org via web scraping
- Geração de documentos Word formatados (S140)
- Suporte para múltiplas semanas
- Atribuição automática de publicadores às partes
- Integração com base de dados de publicadores

### 2. Gerenciar Publicadores
- CRUD completo de publicadores
- Status de batismo
- Busca e filtros
- Histórico de última parte realizada
- Validação de nomes duplicados

### 3. Histórico de Reuniões
- Visualização de todas as reuniões criadas
- Filtros por mês e ano
- Detalhes completos de cada reunião
- Lista de participantes por parte

### 4. Histórico de Publicadores
- Histórico individual de cada publicador
- Lista de todas as partes realizadas
- Datas de participação
- Busca por nome

### 5. Dashboards
- Gráficos de participações por publicador
- Estatísticas de participações por mês
- Visualizações com matplotlib
- Top 10 publicadores mais ativos

## 📦 Requisitos

### Sistema Operacional
- Windows 10 ou superior
- Linux (com suporte a Tkinter)
- macOS (com suporte a Tkinter)

### Software
- Python 3.11 ou superior
- MongoDB 4.4+ ou AWS DynamoDB
- Microsoft Word (para visualizar documentos gerados)

### Dependências Python
Todas as dependências estão listadas em `requirements.txt`:

```
ttkbootstrap
pymongo
python-docx
Pillow
requests
beautifulsoup4
pyinstaller
matplotlib
boto3
python-dotenv
```

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd JW_Mural
```

### 2. Criar Ambiente Virtual

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
# Tipo de banco de dados (mongodb ou dynamodb)
DB_TYPE=mongodb

# Configurações MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=jw_mural
MONGODB_COLLECTION=publicadores

# Configurações DynamoDB (se usar)
AWS_REGION=us-east-1
DYNAMODB_TABLE=publicadores
```

### 5. Configurar Banco de Dados

#### MongoDB (Recomendado)

1. Instale o MongoDB: https://www.mongodb.com/try/download/community
2. Inicie o serviço MongoDB
3. O sistema criará automaticamente as collections necessárias na primeira execução

#### DynamoDB (Alternativa)

1. Configure as credenciais AWS
2. Crie uma tabela no DynamoDB com a chave primária `nome` (String)
3. Configure as variáveis de ambiente apropriadas

### 6. Verificar Estrutura de Diretórios

Certifique-se de que os seguintes diretórios existem:

```
JW_Mural/
├── assets/              # Ícones e recursos visuais
├── database/            # Módulos de banco de dados
├── documentosCriados/   # Documentos gerados
├── process/             # Processamento de dados
├── Templates/           # Templates Word
└── util/               # Utilitários
```

Se não existirem, execute:

**Windows:**
```bash
setup\startup.bat
```

**Linux/macOS:**
```bash
mkdir -p assets documentosCriados Templates process database util
```

## ⚙️ Configuração

### Arquivo .env

O arquivo `.env` contém todas as configurações do sistema. Exemplo completo:

```env
# Tipo de banco de dados
DB_TYPE=mongodb

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=jw_mural
MONGODB_COLLECTION=publicadores

# DynamoDB (opcional)
AWS_REGION=us-east-1
DYNAMODB_TABLE=publicadores
```

### Templates Word

O sistema utiliza templates Word localizados em `Templates/`. O template padrão é `Template_PT.docx`.

**Importante:** O template deve conter placeholders no formato `p01`, `p02`, etc., que serão substituídos pelos dados da reunião.

### Ícone da Aplicação

O ícone deve estar localizado em `assets/icon.ico` (Windows) ou `assets/icon.png` (Linux/macOS).

## 💻 Uso

### Iniciar a Aplicação

**Windows:**
```bash
python layout.py
```

Ou execute o executável compilado:
```bash
JW_Mural.exe
```

**Linux/macOS:**
```bash
python3 layout.py
```

### Criar uma Reunião

1. Clique em **"Criar Reunião"** no menu principal
2. Preencha os campos:
   - **URL**: URL da semana inicial do wol.jw.org (ex: `https://wol.jw.org/pt/wol/d/r4/lp-t/...`)
   - **Quantidade de Semanas**: Número de semanas a processar
   - **Nome do Arquivo**: Nome para o documento gerado
   - **Idioma**: Idioma do template (atualmente apenas PT)
   - **Utilizar base de publicadores**: Marque para atribuir publicadores automaticamente
3. Clique em **"Gerar Reunião"**
4. Se marcou "Utilizar base de publicadores", será solicitado o nome do publicador para cada parte
5. O documento será gerado em `documentosCriados/` e aberto automaticamente

### Gerenciar Publicadores

1. Clique em **"Publicadores"** no menu principal
2. Use a busca para encontrar publicadores
3. Clique em **"Adicionar Publicador"** para adicionar novos
4. Selecione um publicador e clique em **"Editar"** para modificar
5. Clique em **"Excluir"** para remover (com confirmação)

### Visualizar Histórico

#### Histórico de Reuniões
1. Clique em **"Histórico"** no menu principal
2. Use os filtros de mês e ano para buscar
3. Clique em uma reunião para ver detalhes completos

#### Histórico de Publicadores
1. Clique em **"Histórico de Publicadores"** no menu principal
2. Use a busca para encontrar um publicador
3. Clique em um publicador para ver seu histórico completo

### Dashboards

1. Clique em **"Dashboards"** no menu principal
2. Selecione entre:
   - **Participações por Publicador**: Gráfico de barras com número de participações
   - **Participações por Reunião**: Gráfico agrupado por mês dos top 10 publicadores

## 📁 Estrutura do Projeto

```
JW_Mural/
├── assets/                    # Recursos visuais
│   └── icon.ico              # Ícone da aplicação
├── database/                 # Módulos de banco de dados
│   ├── __init__.py           # Exportações do módulo
│   ├── db_connection.py     # Conexão com banco
│   ├── db_operations.py     # Operações CRUD
│   └── init_db.py           # Inicialização do banco
├── documentosCriados/        # Documentos gerados
├── logs/                     # Logs do sistema
├── process/                  # Processamento de dados
│   ├── s140.py              # Geração de documentos S140
│   └── webscrapper.py       # Web scraping
├── setup/                    # Scripts de setup
│   ├── startup.bat          # Script de inicialização Windows
│   └── setup_env.py         # Configuração de ambiente
├── Templates/                # Templates Word
│   └── Template_PT.docx     # Template padrão
├── util/                     # Utilitários
│   ├── comandosUteis.py     # Funções auxiliares
│   ├── db_utils.py          # Utilitários de banco
│   ├── janelas.py           # Diálogos e modais
│   ├── startup_manager.py   # Gerenciador de inicialização
│   └── system_checks.py     # Verificações de sistema
├── .env                      # Variáveis de ambiente (criar)
├── build.py                  # Script de build
├── JW_Mural.spec            # Configuração PyInstaller
├── layout.py                # Interface gráfica principal
├── requirements.txt         # Dependências Python
└── README.md                # Este arquivo
```

### Descrição dos Módulos Principais

#### `layout.py`
Interface gráfica principal usando ttkbootstrap. Contém:
- Menu principal com cards de navegação
- Janelas de gerenciamento de publicadores
- Janelas de histórico
- Dashboards com gráficos

#### `database/`
Módulo de acesso a dados:
- **db_connection.py**: Gerencia conexões MongoDB/DynamoDB
- **db_operations.py**: Operações CRUD e queries complexas
- **init_db.py**: Inicialização e criação de índices

#### `process/`
Processamento de dados:
- **s140.py**: Extração de dados e geração de documentos Word
- **webscrapper.py**: Web scraping do wol.jw.org

#### `util/`
Utilitários e helpers:
- **janelas.py**: Diálogos modais para entrada de dados
- **startup_manager.py**: Verificações e inicialização do sistema
- **system_checks.py**: Validação de requisitos do sistema
- **db_utils.py**: Utilitários de banco de dados

## 🔨 Build e Deploy

### Compilar Executável

O projeto utiliza PyInstaller para criar executáveis standalone.

#### Usando build.py

```bash
python build.py
```

O executável será gerado em `dist/JW_Mural/`.

#### Configuração Manual

Edite `JW_Mural.spec` conforme necessário e execute:

```bash
pyinstaller JW_Mural.spec
```

### Arquivos Incluídos no Build

- `assets/`: Recursos visuais
- `database/`: Módulos de banco
- `process/`: Processamento
- `util/`: Utilitários
- `Templates/`: Templates Word
- `documentosCriados/`: Diretório de saída

### Distribuição

1. Compile o executável
2. Distribua a pasta `dist/JW_Mural/` completa
3. Certifique-se de que o MongoDB está instalado no sistema destino
4. Configure o arquivo `.env` no sistema destino

## 🗺️ Roadmap

### Versão 1.0 (Atual)
- ✅ Geração de documentos S140
- ✅ Gerenciamento de publicadores
- ✅ Histórico de reuniões
- ✅ Dashboards básicos

### Próximas Versões

#### V1.1
- [ ] Layout melhorado
- [ ] Adicionar label de congregação
- [ ] Refatoração de código e comentários

#### V2.0
- [ ] Formatação 100% do documento Word
- [ ] Campo de designados do mês para gerar documento pronto
- [ ] Sistema de login
- [ ] Histórico de quem fez as partes
- [ ] Exportação para PDF
- [ ] Suporte a múltiplos idiomas
- [ ] Sincronização em nuvem

## 🔧 Troubleshooting

### Erro: "Não foi possível conectar ao banco de dados"

**Causa:** MongoDB não está rodando ou URI incorreta.

**Solução:**
1. Verifique se o MongoDB está instalado e rodando
2. Confirme a URI no arquivo `.env`
3. Teste a conexão: `mongosh "mongodb://localhost:27017/"`

### Erro: "Diretórios faltando"

**Causa:** Estrutura de diretórios não foi criada.

**Solução:**
Execute `setup\startup.bat` (Windows) ou crie os diretórios manualmente.

### Erro: "Template não encontrado"

**Causa:** Template Word não está no diretório correto.

**Solução:**
1. Verifique se `Templates/Template_PT.docx` existe
2. Certifique-se de que o template contém os placeholders corretos (p01, p02, etc.)

### Erro ao gerar documento

**Causa:** URL inválida ou estrutura HTML do site mudou.

**Solução:**
1. Verifique se a URL está correta e acessível
2. Teste a URL no navegador
3. Verifique os logs em `logs/` para mais detalhes

### Publicador não aparece na lista

**Causa:** Nome não está formatado corretamente ou não foi salvo.

**Solução:**
1. Verifique se o nome foi salvo corretamente
2. Use a busca para encontrar o publicador
3. Verifique o banco de dados diretamente

### Documento gerado está vazio ou incorreto

**Causa:** Template não contém os placeholders corretos.

**Solução:**
1. Verifique o template em `Templates/Template_PT.docx`
2. Certifique-se de que todos os placeholders (p01-p45) estão presentes
3. Verifique a formatação do template

## 📝 Licença

Este projeto é de uso interno para congregações de Testemunhas de Jeová.

## 🤝 Contribuindo

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📧 Suporte

Para suporte, abra uma issue no repositório ou entre em contato com os mantenedores do projeto.

---

**Versão:** 1.0  
**Última atualização:** 2024
