# Interface e Telas

Resumo das telas e ações principais do usuário.

## Tela principal

Menu com cards de acesso às funcionalidades: Criar Reunião de Meio de Semana, Criar Reunião Final de Semana, Publicadores, Histórico de Publicadores, Histórico Reunião Meio de Semana, Histórico Reunião Final de Semana, Dashboards. Cada card tem botão "ACESSAR" que abre a janela correspondente.

## Criar Reunião de Meio de Semana

Formulário com: URL do wol.jw.org, quantidade de semanas, nome do arquivo, idioma, checkbox "Utilizar base de publicadores" e "Gerar com Publicadores (Seleção Automática)". Botão "Gerar Reunião". Com publicadores: ou diálogos por parte (manual) ou modal de resumo para revisar e editar (automático). Documento gerado em documentosCriados/ e aberto.

## Criar Reunião Final de Semana

Formulário com: URL da página de meetings, nome do arquivo, checkboxes para seleção automática de Presidente e de Leitor da Sentinela. Botão "Gerar Reunião". Em seguida: modal para escolher Dirigente de Sentinela (entre anciãos); modal para preencher, por semana, Tema Discurso (autocomplete com temas do JSON), Orador, Presidente e Leitor Sentinela (autocomplete com anciãos/servos e com permissão leitura_sentinela). Dois documentos gerados (Sentinela e Oradores) em documentosCriados/.

## Publicadores

Lista de publicadores com busca. Botões: Adicionar Publicador, Editar, Excluir. Formulário de adicionar/editar: nome, batizado, sexo, Ancião, Servo Ministerial, permissões (parte_escola, oração, leitura_livro, leitura_sentinela, presidente_final_semana). Exclusão com confirmação.

## Histórico Reunião Meio de Semana

Filtros por ano e mês. Lista de reuniões; ao clicar, exibe detalhes (partes e participantes).

## Histórico Reunião Final de Semana

Filtros por ano e mês. Lista de reuniões de final de semana; ao clicar, exibe detalhes das semanas (tema, orador, presidente, leitor).

## Histórico de Publicadores

Busca por nome. Lista de publicadores; ao selecionar um, exibe o histórico de participações (parte e data).

## Dashboards

Dois modos: Participações por Publicador (gráfico de barras) e Participações por Reunião (agrupado por mês). Filtro opcional por parte no dashboard de participações. Gráficos gerados com matplotlib na própria janela.
