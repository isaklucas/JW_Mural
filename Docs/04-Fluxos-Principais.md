# Fluxos Principais

Descrição dos fluxos de uso mais importantes e onde eles estão implementados no código.

> **Nota de arquitetura (atual):** onde os passos abaixo dizem "layout chama
> `db_ops.X()`", hoje a lógica vive na **tela em `views/`** (mixin de `ModernApp`)
> e o acesso ao banco passa pela **camada de serviço** (`services/`): p.ex.
> `db_ops.getAllPub()` → `publicador_service.listar()`,
> `db_ops.salvar_reuniao()` → `reuniao_service.salvar()`,
> `db_ops.contar_participacoes_por_parte()` → `dashboard_service.contar_participacoes_por_parte()`.
> As telas não importam `database`/`db_ops` diretamente. Os nomes `db_ops.*`
> abaixo indicam a operação de banco final (dentro do serviço).

---

## 0. Arranque e encerramento (backup)

- **Arranque:** `layout.py` cria a janela e chama `initialize_application` → `startup_manager.run_checks()`, que verifica sistema/conexão e chama `backup_database()` — exporta as collections para `backups/<AAAA-MM-DD>/` e **pula se a pasta do dia já existe** (snapshot de antes das edições do dia).
- **Encerramento:** fechar no X dispara `_encerrar_app` (registrado em `root.protocol("WM_DELETE_WINDOW", ...)`), que mostra "Salvando backup..." e chama `backup_database(sufixo="-saida", forcar=True)` → `backups/<AAAA-MM-DD>-saida/`, sobrescrito a cada fechamento do dia. Falha de backup não impede o app de fechar. O mesmo backup roda antes de `updater.lancar_instalador_e_sair` (atualização também encerra o app).
- **Retenção:** todo backup bem-sucedido chama `limpar_backups_antigos(90)` — apaga pastas de backup com mais de 90 dias (nome fora do padrão `AAAA-MM-DD*` é ignorado).
- **Restaurar:** Configurações → Restaurar Banco lista todas as subpastas de `backups/` (inclusive as `-saida`) e usa `backup.restore_database`.

---

## 1. Criar Reunião de Meio de Semana

1. O usuário clica no card **Criar Reunião de Meio de Semana** em **layout.py** e preenche a janela: URL do wol.jw.org, quantidade de semanas, nome do arquivo, idioma, e opções “Utilizar base de publicadores” e “Gerar com Publicadores (Seleção Automática)”.
2. Ao confirmar, **layout** chama **process.s140.gerar_s140** com os parâmetros informados.
3. **s140** usa **webscrapper** para obter o HTML de cada semana (lista de soups) e **s140.extrair_partes** para montar a estrutura de partes por semana (presidente, oração, tesouro, joias, leitura, escola, nossa vida cristã, estudo, oração final).
4. Se “Utilizar base de publicadores” estiver marcado:
   - **Com seleção automática:** **s140.selecionar_publicadores_automaticamente** preenche as partes com critérios (Ancião, Servo Ministerial, permissões, sexo, tempo sem participar); em seguida **s140.mostrar_resumo_e_editar_publicadores** exibe um modal para revisar e editar; só então segue a geração.
   - **Sem seleção automática:** **s140.solicitarNomePublicadorPartes** abre diálogos (util.janelas) para cada parte; depois a geração.
5. **s140.criarDocumentoApartirDoObjeto** gera o documento Word a partir do template (Template_PT.docx) e salva em **documentosCriados/**.
6. Se houve preenchimento com publicadores e foi seleção manual, **s140.atualizarHistoricoPublicadores** é chamado; em seguida **layout** (ou s140) chama **db_ops.salvar_reuniao** para persistir a reunião e atualizar o histórico dos publicadores na collection **reunioes**.

Referência principal: **layout.py** (janela do quadro de anúncio / criar reunião) e **process/s140.py**.

---

## 2. Criar Reunião Final de Semana

O card abre `escolher_modo_final_semana`: **Criar reunião** (Minutas, padrão), **Modelo do documento** ou **modo antigo** (fluxo 2.L abaixo).

### 2.M Modo Minutas (bimestre)

1. **Passo 1 — Período** (`views/minutas_view.py`): mês inicial + ano (sempre 2 meses), dirigente de A Sentinela, nome do arquivo, seleção automática de presidente/leitor.
2. Em thread: `minuta_service.buscar_programacao` monta os sábados (`process/minutas/periodo.py`) e, para cada um, busca o título do estudo em `https://wol.jw.org/pt/wol/meetings/r5/lp-t/<ano ISO>/<semana ISO>`; aplica a seleção automática (mesmas funções do legado).
3. **Passo 2 — Oradores vindo:** por mês, congregação de onde vêm; por sábado, título do estudo (editável), tema, orador, presidente, leitor.
4. **Passo 3 — Oradores indo:** por mês, congregação de destino; por sábado, orador e tema (em branco = não houve).
5. **Gerar:** `minuta_service.gerar_final_semana` renderiza cada minuta (`fds_oradores`, `fds_sentinela`) sobre o arquivo modelo, remove a reunião anterior do mesmo período (se houver — evita histórico duplicado), salva em `reunioes_final_semana` (`modo: "minuta"`, `meses`, `semanas` planas com `data`/`data_historico`), grava os .docx em `documentos_gerados` e em `documentosCriados/` e os abre.

Durante os passos, a coluna da direita mostra a **pré-visualização ao vivo** (re-renderiza ~0,5 s depois de cada tecla; escolhe Oradores ou Sentinela; "Abrir no Word").
6. **Histórico:** detalhes de reunião `modo: "minuta"` têm **Abrir documentos** (exporta do banco) e **Editar** reabre o assistente no passo 2.

**Modelo do documento** (`editor_minutas`): a aparência vem do Word oficial importado ("Importar arquivo oficial…"); a tela só define os títulos do topo, qual tabela do modelo serve de exemplo para cada parte, o título de cada mês (variáveis `{mes}`, `{congregacao_recebendo}`…) e o que vai em cada coluna — com pré-visualização ao vivo. Cada salvamento incrementa `versao` e guarda a anterior em `minutas_versoes`.

### 2.L Modo legado (templates .docx)

1. O usuário clica no card **Criar Reunião Final de Semana** em **layout.py** e preenche URL, nome do arquivo e opções de seleção automática de Presidente e de Leitor da Sentinela.
2. Ao confirmar, **layout** inicia o fluxo em uma thread de background: chama **final_semana.FinalSemana.buscar_titulos_meetings** (que usa **webscrapper.extrair_titulos_sentinela_meetings**) para obter as 9 semanas com títulos do estudo da Sentinela.
3. Na mesma thread: se marcado, **FinalSemana.selecionar_presidente_automaticamente(semanas)** preenche presidente por semana usando **db_ops.listar_presidentes_final_semana_ordenados_por_menos_partecipacoes()** (anciãos e servos, ordenados por quem fez menos “Presidente Final Semana”). Se marcado, **FinalSemana.selecionar_leitor_automaticamente(semanas)** preenche leitor_sentinela com **db_ops.listar_ordenados_por_menos_partecipacoes("leitura_sentinela", "Leitura Sentinela")**.
4. **layout** agenda na thread principal: modal **solicitar_dirigente_sentinela** (escolher dirigente entre anciãos), depois **solicitar_dados_usuario(semanas)** — modal com tema de discurso (autocomplete de **assets/temas_discursos.json**), orador, presidente e leitor por semana (autocomplete com anciãos/servos e com leitura_sentinela).
5. Após o usuário confirmar, **FinalSemana.criar_documento_sentinela** e **criar_documento_oradores** geram os dois Word a partir dos templates em **Templates/** e salvam em **documentosCriados/**.
6. **FinalSemana.salvar_historico_final_semana** chama **db_ops.salvar_reuniao_final_semana** para gravar em **reunioes_final_semana** e atualizar o histórico dos publicadores (partes “Presidente Final Semana” e “Leitura Sentinela”).

Referência principal: **layout.py** (janela “Criar Reunião Final de Semana” e callback na main thread) e **process/final_semana.py**.

---

## 3. Publicadores (CRUD, permissões, histórico)

1. O usuário abre **Publicadores** a partir do card no **layout.py**; a janela lista publicadores carregados com **db_ops.getAllPub()** e oferece busca, adicionar, editar e excluir.
2. Ao adicionar ou editar, o formulário coleta nome, batismo, sexo, Ancião, Servo Ministerial e permissões (parte_escola, oracao, leitura_livro, leitura_sentinela, presidente_final_semana). **layout** chama **db_ops.post()** ou **db_ops.update_publicador()** conforme o caso.
3. Ao excluir, **layout** chama **db_ops.delete(nome)** após confirmação.
4. O histórico de cada publicador é armazenado no documento do publicador (campo **historico**); não há tela dedicada de “edição de histórico”, mas as reuniões salvas atualizam esse campo via **db_operations._atualizar_historico_individual**.

Referência principal: **layout.py** (janela de publicadores, formulário de adicionar/editar) e **database/db_operations.py**.

---

## 4. Histórico e Dashboards

- **Histórico de Reuniões (meio de semana):** **layout** abre uma janela que usa **db_ops.listar_reunioes(ano, mes)** (ou filtros equivalentes) e exibe a lista; ao selecionar uma reunião, **db_ops.buscar_reuniao(ano, semana)** carrega os detalhes para exibição.
- **Histórico de Reuniões (final de semana):** **layout** usa **db_ops.listar_reunioes_final_semana** e **buscar_reuniao_final_semana** para listar e mostrar detalhes.
- **Histórico de Publicadores:** **layout** lista publicadores e, ao escolher um, chama **db_ops.buscar_historico_publicador(nome)** para exibir as participações (parte e data).
- **Dashboards:** **layout** usa **db_ops.contar_participacoes_por_parte** (e métodos relacionados) para obter dados e monta gráficos (matplotlib) na própria janela — participações por publicador e participações por reunião.

Referência principal: **layout.py** (janelas de histórico e de dashboards) e **database/db_operations.py** (listar_reunioes, buscar_reuniao, listar_reunioes_final_semana, buscar_reuniao_final_semana, buscar_historico_publicador, contar_participacoes_por_parte, etc.).
