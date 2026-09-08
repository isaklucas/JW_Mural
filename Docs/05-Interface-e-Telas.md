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

Botão **Alterar / Remover** na janela de detalhes: corrige UMA participação selecionada — passa a parte para outro publicador ("Substituir") ou apaga a participação ("Remover"). Vale para partes com dois participantes ("Nome1 / Nome2"): o modal pede qual dos dois. A alteração vai ao mesmo tempo para o histórico dos publicadores e para o documento da reunião — via `remover_participacao` / `reatribuir_participacao` (mesmo modal em `views/components.py`). É o Transferir Histórico reduzido a uma entrada só.

## Histórico Reunião Final de Semana

Filtros por ano e mês. Lista de reuniões de final de semana; ao clicar, exibe detalhes das semanas (tema, orador, presidente, leitor).

## Histórico de Publicadores

Busca por nome. Lista de publicadores; ao selecionar um, exibe o histórico de participações (parte e data).

Botão **Alterar / Remover** na janela de detalhes: corrige UMA participação selecionada — passa a parte para outro publicador ("Substituir") ou apaga a participação ("Remover"). Vale para partes com dois participantes ("Nome1 / Nome2"): o modal pede qual dos dois. A alteração vai ao mesmo tempo para o histórico dos publicadores e para o documento da reunião — via `remover_participacao` / `reatribuir_participacao` (mesmo modal em `views/components.py`). É o Transferir Histórico reduzido a uma entrada só.

Botão **Transferir Histórico**: move todas as participações de um publicador para outro (usado quando a participação foi gravada no irmão errado). Escolhe origem e destino, mescla no destino sem duplicar `parte+data`, zera a origem e — com o toggle "Atualizar também as reuniões já salvas" marcado (padrão) — troca o nome em `reunioes`, `reunioes_final_semana` e `designacoes_salao`. Sem essa troca, resalvar a semana reconstrói o histórico a partir da reunião e desfaz a transferência. Via `publicador_service.transferir_historico`.

## Designações Salão

Gerencia designações de áudio, vídeo, microfone e indicadores por mês. Geração automática (respeitando impedimentos e balanceando por quem fez menos), edição manual na tabela, salvar/excluir por mês e exportar `.docx`. Dados via `designacao_service`.

## Dashboards

Quatro modos, um por categoria de parte — as contagens são disjuntas e nunca se somam (ver `src/database/partes.py`):

- **Meio de Semana - Publicador** (barras) — partes do programa do S140, com filtro opcional por parte.
- **Meio de Semana - Reunião** (barras) — quantas reuniões de meio de semana cada publicador participou (1x por reunião).
- **Final de Semana** (tabela) — Leitura Sentinela e Presidente Final Semana.
- **Designações Salão** (tabela) — trabalho na reunião: áudio, vídeo, microfone, indicador.

Uma legenda fixa no topo da janela lembra a separação. Gráficos com matplotlib na própria janela; contagens via `dashboard_service`.
