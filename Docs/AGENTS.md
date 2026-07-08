# JW Mural - Guia para Agentes IA

## Visão Executiva

O **JW Mural** é uma aplicação desktop Python para congregações de Testemunhas de Jeová. O sistema extrai automaticamente dados de reuniões do site wol.jw.org, gera documentos Word (S140) com a programação completa e gerencia uma base de publicadores com histórico de participações. Suporta seleção manual ou automática de publicadores para cada parte da reunião, respeitando critérios (Ancião, Servo Ministerial, permissões, sexo) e priorizando quem está há mais tempo sem participar.

## Ponto de Entrada

- **Arquivo principal:** `layout.py`
- **Execução:** `python layout.py` ou `JW_Mural.exe`
- **Inicialização:** `if __name__ == "__main__"` → cria janela ttkbootstrap → `initialize_application(root)` → `ModernApp(root)`

## Módulos Principais

| Módulo | Responsabilidade |
|--------|-------------------|
| `layout.py` | Interface gráfica (ModernApp), menu principal, janelas de CRUD e dashboards |
| `process/s140.py` | Extração de dados do HTML, geração de documentos Word, seleção de publicadores |
| `process/webscrapper.py` | Requisições HTTP e parsing HTML (BeautifulSoup) do wol.jw.org |
| `database/db_operations.py` | CRUD de publicadores e reuniões, seleção automática por critérios |
| `database/db_connection.py` | Conexão MongoDB ou DynamoDB |
| `util/janelas.py` | Diálogos modais (seleção de publicador, confirmações) |
| `util/startup_manager.py` | Verificações de sistema na inicialização |
| `util/system_checks.py` | Validação de diretórios, arquivos e variáveis de ambiente |

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

1. **Placeholders do template:** p01-p23 (conteúdo), p34-p45 (publicadores). Não alterar numeração sem atualizar `Templates/Template_PT.docx`.
2. **Threading:** Operações longas (web scraping, geração de documento) devem rodar em thread separada para não travar a UI.
3. **Nomes:** Sempre normalizar com `util.ComandosUteis.TitleCase()` antes de salvar.
4. **Banco:** Manter compatibilidade MongoDB e DynamoDB; verificar `db_type` em operações específicas.
5. **Múltiplos publicadores:** Formato "Nome1 / Nome2" para partes com dois participantes.
6. **Validação:** Validar entrada do usuário antes de persistir no banco.
