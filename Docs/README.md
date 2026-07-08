# Documentação do JW Mural

Documentação técnica e funcional do projeto JW Mural — sistema de gerenciamento de reuniões de meio e final de semana para congregações.

## Índice

| Documento | Conteúdo |
|------------|----------|
| [01-Arquitetura.md](01-Arquitetura.md) | Visão geral da arquitetura: entrada, camadas (UI, process, database, util) e fluxo de dados entre módulos. |
| [02-Banco-de-Dados.md](02-Banco-de-Dados.md) | Estrutura do banco de dados: MongoDB e DynamoDB, collections/tabelas, esquema dos documentos e índices. |
| [03-Modulos.md](03-Modulos.md) | Descrição de cada módulo e arquivo: função e responsabilidades (layout, database, process, util, assets, Templates). |
| [04-Fluxos-Principais.md](04-Fluxos-Principais.md) | Fluxos de uso: criar reunião meio de semana, criar reunião final de semana, publicadores, histórico e dashboards. |
| [05-Interface-e-Telas.md](05-Interface-e-Telas.md) | Resumo das telas da aplicação e ações principais do usuário. |
| [06-Build-e-Instalador.md](06-Build-e-Instalador.md) | Como gerar o instalador, versionamento e atualizações automáticas via GitHub Releases. |

## Onde encontrar o quê

- **Como o sistema está organizado** → 01-Arquitetura.md  
- **Estrutura de dados e persistência** → 02-Banco-de-Dados.md  
- **O que cada pasta/arquivo faz** → 03-Modulos.md  
- **Passo a passo dos fluxos principais** → 04-Fluxos-Principais.md  
- **Telas e uso da interface** → 05-Interface-e-Telas.md  
- **Build, versionamento e atualizações** → 06-Build-e-Instalador.md  
