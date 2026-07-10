# Interface e Telas

Resumo das telas e ações principais do usuário.

## Tela principal

Menu com cards de acesso às funcionalidades: Criar Reunião de Meio de Semana, Criar Reunião Final de Semana, Publicadores, Histórico de Publicadores, Histórico Reunião Meio de Semana, Histórico Reunião Final de Semana, Designações Salão, Dashboards. **Cada card inteiro é clicável** e abre a janela correspondente (não há botão "ACESSAR"): uma faixa de cor no topo identifica a categoria e o cursor de mão indica o clique. O ícone de engrenagem abre Configurações.

## Criar Reunião de Meio de Semana

Formulário com: URL do wol.jw.org, quantidade de semanas, nome do arquivo, idioma, checkbox "Utilizar base de publicadores" e "Gerar com Publicadores (Seleção Automática)". Botão "Gerar Reunião". Com publicadores: ou diálogos por parte (manual) ou modal de resumo para revisar e editar (automático). Documento gerado em documentosCriados/ e aberto.

## Criar Reunião Final de Semana

Formulário com: URL da página de meetings, nome do arquivo, checkboxes para seleção automática de Presidente e de Leitor da Sentinela. Botão "Gerar Reunião". Em seguida: modal para escolher Dirigente de Sentinela (entre anciãos); modal para preencher, por semana, Tema Discurso (autocomplete com temas do JSON), Orador, Presidente e Leitor Sentinela (autocomplete com anciãos/servos e com permissão leitura_sentinela). Dois documentos gerados (Sentinela e Oradores) em documentosCriados/.

## Publicadores

Lista de publicadores com busca. Botões: Adicionar Publicador, Editar, Excluir. Formulário de adicionar/editar: nome, batizado (toggle), sexo, Ancião, Servo Ministerial, permissões (parte_escola, oração, leitura_livro, leitura_sentinela, presidente_final_semana e as de salão: audio_video, indicador, microfone). Exclusão com confirmação. Operações de banco via `publicador_service`.

## Histórico Reunião Meio de Semana

Filtros por ano e mês. Lista de reuniões; ao clicar, exibe detalhes (partes e participantes).

## Histórico Reunião Final de Semana

Filtros por ano e mês. Lista de reuniões de final de semana; ao clicar, exibe detalhes das semanas (tema, orador, presidente, leitor).

## Histórico de Publicadores

Busca por nome. Lista de publicadores; ao selecionar um, exibe o histórico de participações (parte e data).

## Designações Salão

Gerencia designações de áudio, vídeo, microfone e indicadores por mês. Geração automática (respeitando impedimentos e balanceando por quem fez menos), edição manual na tabela, salvar/excluir por mês e exportar `.docx`. Dados via `designacao_service`.

## Dashboards

Três modos: Participações por Publicador (barras), Participações por Reunião (agrupado por mês) e Designações de Salão (tabela). Filtro opcional por parte. Gráficos com matplotlib na própria janela; contagens via `dashboard_service`.
