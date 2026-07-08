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

### 1. Criar Reunião de Meio de Semana
- Extração automática de dados do wol.jw.org via web scraping
- Geração de documentos Word formatados (S140)
- Suporte para múltiplas semanas
- **Dois modos de atribuição de publicadores:**
  - **Seleção manual:** Diálogo para cada parte, com busca e suporte a múltiplos (formato "Nome1 / Nome2")
  - **Seleção automática:** Critérios por parte (Ancião, Servo Ministerial, permissões, sexo), prioriza quem está há mais tempo sem participar; modal de revisão permite editar antes de gerar
- Integração com base de dados de publicadores

### 1.1 Criar Reunião Final de Semana
- Extração dos títulos do estudo da Sentinela na página de meetings (wol.jw.org)
- Geração de **dois** documentos Word: Sentinela (dirigente, títulos e leitores) e Oradores (presidente, orador e tema por semana)
- **Seleção automática opcional:** Presidente = anciãos e servos ministeriais (quem fez menos "Presidente Final Semana"); Leitor da Sentinela = publicadores com permissão leitura_sentinela (quem fez menos "Leitura Sentinela"); distribuição um por semana com ciclo
- Tema de discurso com **autocomplete** a partir de `assets/temas_discursos.json`
- Templates em `Templates/` (template_final_semana_sentinela.docx e template_final_semana_oradores.docx) são apenas lidos; saída em `documentosCriados/`

### 2. Gerenciar Publicadores
- CRUD completo de publicadores
- Status de batismo, sexo, Ancião, Servo Ministerial
- Permissões: parte da escola, oração, leitura na reunião, leitura_sentinela, presidente_final_semana
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

### Instalação via Setup_JW_Mural.exe (recomendado)

1. Execute `installer_output\Setup_JW_Mural.exe` como **Administrador**
2. O instalador irá:
   - Instalar o JW Mural em `C:\Program Files\JW Mural\`
   - Instalar/iniciar MongoDB via winget (se não estiver presente)
   - Inicializar as collections do banco
   - Abrir o aplicativo ao final
3. Inicie o app pelo atalho criado ou executando `JW_Mural.exe` na pasta de instalação

### Instalação manual (desenvolvimento)

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

Copie o modelo `.env.example` para `.env` e ajuste os valores:

**Windows:**
```bash
copy .env.example .env
```

**Linux/macOS:**
```bash
cp .env.example .env
```

> ⚠️ O arquivo `.env` **não** é versionado (está no `.gitignore`) porque a
> `MONGODB_URI` pode conter usuário/senha em produção (ex.: MongoDB Atlas).
> Nunca comite o `.env` nem chaves AWS.

Conteúdo padrão (`.env.example`):
```env
DB_TYPE=mongodb
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=jw_mural
MONGODB_COLLECTION=publicadores
# DynamoDB (opcional):
# AWS_REGION=us-east-1
# DYNAMODB_TABLE=publicadores
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

Se não existirem, crie manualmente:

```bash
mkdir assets documentosCriados Templates
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

O ícone deve estar localizado em `assets/icon.ico` (Windows) ou `assets/icon.png` (Linux/macOS). O build usa `assets/icon.ico`; se não existir, a aplicação inicia sem ícone. O arquivo `jw_mural_icon_40x40.png` pode ser convertido para `.ico` se necessário.

## 💻 Uso

### Iniciar a Aplicação

**Windows:**
```bash
python src/layout.py
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
   - **Utilizar base de publicadores**: Marque para atribuir publicadores às partes
   - **Gerar com Publicadores (Seleção Automática)**: Marque para seleção automática; o sistema escolherá publicadores com base em critérios (Ancião, SM, permissões) e tempo sem participar. Um modal de revisão permitirá editar antes de gerar o documento
3. Clique em **"Gerar Reunião"**
4. Se marcou "Utilizar base de publicadores":
   - **Com seleção automática:** O sistema preenche as partes e exibe um modal para revisar e editar. Clique em "Salvar e Continuar" para gerar o documento
   - **Sem seleção automática:** Será solicitado o nome do publicador para cada parte em diálogos individuais
5. O documento será gerado em `documentosCriados/` e aberto automaticamente

### Criar uma Reunião Final de Semana

1. Clique em **"Criar Reunião Final de Semana"** no menu principal
2. Preencha a **URL** da página de meetings (ex.: `https://wol.jw.org/pt/wol/meetings/...`) e o **Nome do Arquivo**
3. Opcional: marque **Seleção automática do Presidente** e/ou **Seleção automática do Leitor da Sentinela**
4. Clique em **"Gerar Reunião"**
5. Escolha o **Dirigente de Sentinela** no modal (entre anciãos)
6. No próximo modal, preencha por semana: **Tema Discurso** (autocomplete), **Orador**, **Presidente** e **Leitor Sentinela** (autocomplete); confirme
7. Dois documentos (Sentinela e Oradores) serão gerados em `documentosCriados/` e abertos

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
├── build.bat                 # Pipeline de build: PyInstaller + Inno Setup
├── install_mongo.ps1         # Script de instalação MongoDB (bundlado no installer)
├── JW_Mural.iss              # Configuração Inno Setup (gera Setup_JW_Mural.exe)
├── JW_Mural.spec             # Configuração PyInstaller
├── VERSION.txt               # Versão do app (fonte única; lida pelo app e pelo .iss)
├── .env.example              # Modelo de variáveis de ambiente (copie para .env)
├── .gitignore
├── requirements.txt          # Dependências Python
├── README.md
├── assets/                   # Recursos visuais
│   ├── jw_mural_icon.ico     # Ícone da aplicação
│   └── temas_discursos.json  # Lista de temas para autocomplete
├── Templates/                # Templates Word (lidos, não alterados)
│   ├── Template_PT.docx
│   ├── template_final_semana_sentinela.docx
│   └── template_final_semana_oradores.docx
├── Docs/                     # Documentação técnica (01..06)
├── documentosCriados/        # Documentos gerados (não versionados)
└── src/                      # Código-fonte
    ├── layout.py             # Interface gráfica principal (entrypoint)
    ├── version.py            # __version__ (lê VERSION.txt)
    ├── database/             # Acesso a dados
    │   ├── __init__.py
    │   ├── db_operations.py  # Operações CRUD
    │   └── init_db.py        # Inicialização do banco
    ├── process/              # Processamento de dados
    │   ├── s140.py           # Gerador S140 (meio de semana)
    │   ├── final_semana.py   # Gerador final de semana
    │   └── webscrapper.py    # Web scraping wol.jw.org
    └── util/                 # Utilitários
        ├── db_utils.py
        ├── janelas.py
        ├── startup_manager.py
        ├── system_checks.py
        └── updater.py        # Auto-atualização via GitHub Releases
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

### Script Opcional: transcribe.py

Script separado para transcrição de áudio usando [Whisper](https://github.com/openai/whisper). Não faz parte do fluxo principal do JW Mural. Requer instalação do Whisper (`pip install openai-whisper`) e configuração do caminho do áudio no próprio arquivo.

### Documentação para Desenvolvedores

- **[Docs/](Docs/README.md)**: Documentação detalhada (arquitetura, banco de dados, módulos e fluxos)
- **[Docs/06-Build-e-Instalador.md](Docs/06-Build-e-Instalador.md)**: Como gerar e distribuir o instalador

## 🔨 Build e Deploy

Ver documentação completa: **[Docs/06-Build-e-Instalador.md](Docs/06-Build-e-Instalador.md)**

### Resumo rápido

```bat
build.bat
```

Gera `installer_output\Setup_JW_Mural.exe`. Requer PyInstaller e Inno Setup instalados.

### Atualizações automáticas

O app instalado verifica atualizações ao abrir, consultando os **GitHub
Releases** do repositório. Havendo versão mais nova, avisa o usuário, baixa o
novo `Setup_JW_Mural.exe` e o executa — atualizando por cima da instalação.

Para publicar uma nova versão:

1. Editar `VERSION.txt` (ex.: `1.1`) — fonte única de versão (usada pelo app e pelo instalador).
2. Rodar `build.bat`.
3. Publicar o release anexando o instalador (o asset **precisa** se chamar `Setup_JW_Mural.exe`):
   ```bash
   gh release create v1.1 installer_output/Setup_JW_Mural.exe -t "v1.1" -n "Notas da versão"
   ```

> O repositório (ou ao menos os releases) precisa ser **público** para a
> verificação funcionar sem token. Detalhes: **[Docs/06-Build-e-Instalador.md](Docs/06-Build-e-Instalador.md)**.

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
Crie os diretórios manualmente: `mkdir assets documentosCriados Templates`

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

**Versão:** ver `VERSION.txt`  
**Última atualização:** 2026
