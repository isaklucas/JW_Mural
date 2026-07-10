# SDD 03 — Quebrar o God Object `layout.py`

**Status:** ✅ Decomposição estrutural concluída (2026-07-09). `layout.py` foi de **3914 → 324 linhas**; todas as 9 telas movidas para mixins em `src/views/`. **Desvio de design:** usei mixins (mantêm `self` idêntico, move verbatim, risco baixo) em vez de classes-view + injeção de serviço. A camada `services/` (R3/R4 — UI não chamar DB direto) fica como follow-up. Ver "Pendências" no fim.
**Prioridade:** P3 (grande, incremental — semanas em passos pequenos)
**Módulo alvo:** `src/layout.py` (3981 linhas, 1 classe `ModernApp`, ~90 funções aninhadas)
**Depende de:** SDD 02 (testes como rede de segurança)
**Bloqueia:** manutenção futura em geral

---

## 1. Problema

`layout.py` = 3981 linhas, classe única `ModernApp`, ~90 funções aninhadas.
Mistura tudo numa camada: construção de UI, regras de negócio, threading,
acesso a DB, geração de docx.

Sintomas concretos:

- Cada tela é um método gigante com closures aninhadas mutando estado por
  captura de escopo (`salvar_reuniao`, `adicionar_publicador`,
  `salvar_alteracoes`, `confirmar_gerar`...). Impossível testar isolado.
- `ModernApp` chama `database` direto — sem camada de serviço.
- Métodos por tela: `publicadores` (270), `historico` (1240),
  `criar_quadro_de_anuncio` (1989), `criar_reuniao_final_semana` (2254),
  `historico_final_semana` (2363), `historico_publicadores` (2541),
  `designacoes_salao` (2803), `dashboards` (3498), `abrir_configuracoes` (3768).
  Cada um = candidato natural a módulo próprio.

## 2. Objetivo

Decompor `ModernApp` em módulos por tela + camada de serviço, **incrementalmente**,
uma tela por vez, sem regressão de comportamento. Meta: nenhum arquivo > ~600 linhas.

**Não-objetivo:** reescrever UI, trocar ttkbootstrap, mudar o visual.

## 3. Requisitos

| # | Requisito |
|---|-----------|
| R1 | Comportamento visível ao usuário idêntico a cada passo. |
| R2 | Cada tela vira módulo próprio em `src/views/`. |
| R3 | Regras de negócio saem da UI para `src/services/`. |
| R4 | UI nunca chama `database` direto — sempre via serviço. |
| R5 | Refatoração incremental: cada PR migra 1 tela, app funcional entre PRs. |
| R6 | Testes do SDD 02 passam após cada passo. |

## 4. Design

### 4.1 Arquitetura alvo

```
src/
  app.py                    # bootstrap: cria root, monta shell, delega às views
  shell.py                  # navegação/cards do menu principal (era create_card)
  views/
    publicadores_view.py
    historico_view.py
    quadro_anuncio_view.py
    final_semana_view.py
    designacoes_view.py
    dashboards_view.py
    config_view.py
  services/
    publicador_service.py   # CRUD + regras de publicador
    reuniao_service.py      # midweek: orquestra s140 + persistência
    final_semana_service.py
    designacao_service.py   # regras de designação (compartilha com s140)
    scraper_service.py      # fachada sobre webscrapper
  process/                  # (mantém s140, final_semana, webscrapper)
  database/                 # (inalterado)
  util/                     # (inalterado)
```

### 4.2 Padrão de uma View

Cada view: classe recebe `parent` (frame) + serviço injetado. Sem lógica de
negócio, sem acesso a DB. Closures aninhadas viram métodos.

```python
# views/publicadores_view.py
class PublicadoresView:
    def __init__(self, parent, service):
        self.parent = parent
        self.service = service          # publicador_service
        self._build()

    def _build(self): ...
    def _on_adicionar(self): ...        # era abrir_modal_adicionar (nested)
    def _on_editar(self): ...
    def _on_excluir(self): ...
    def _atualizar_lista(self):
        dados = self.service.listar()   # nunca database.getAllPub direto
        ...
```

### 4.3 Camada de Serviço

Move as regras hoje embutidas na UI. Testável sem tkinter.

```python
# services/publicador_service.py
class PublicadorService:
    def listar(self): return getAllPub()
    def adicionar(self, dados): ...      # validação aqui, não na UI
    def excluir(self, id): ...
    def resetar_historico(self, id): ...
```

### 4.4 Estratégia incremental (ordem de ataque)

Migrar da tela mais isolada para a mais acoplada. Sugestão:

1. **`config_view`** (3768) — menor, poucas deps. Prova do padrão.
2. **`dashboards_view`** (3498) — read-only, baixo risco.
3. **`historico_publicadores_view`** (2541).
4. **`designacoes_view`** (2803).
5. **`historico_view`** + **`final_semana`** (as maiores/mais acopladas por último).
6. Extrair `shell.py` (navegação/cards) e reduzir `ModernApp` a bootstrap fino.

Cada passo:
> extrai tela → cria serviço → liga fios → roda app + `pytest` → commit.

### 4.5 Estado compartilhado

Closures que hoje capturam variáveis do método pai viram atributos da view
(`self.tree`, `self.entry_nome`, ...). Estado entre telas (ex.: DB config) vive
num objeto de contexto injetado, não em globais.

## 5. Tarefas

- [~] T1 — `src/views/` criado (`__init__.py` + `components.py`). `src/services/` ainda não.
- [x] **T1.5 (piloto de extração)** — `views/components.py::criar_card` extraído de `ModernApp.create_card` (que virou wrapper fino que delega). Prova o padrão "tirar construção de widget do god object". Verificado por smoke headless: 8 cards renderizam. Spec PyInstaller atualizado (`src/views` em datas + `views.components` em hiddenimports).
- [x] **Bônus — botões ACESSAR** — descoberto que sob tema ttkbootstrap o `tk.Button` antigo era re-tematizado para `primary`, então as cores por-estilo (info/success/warning/danger) NUNCA apareciam (todos azuis). Trocado por `ttk.Button(bootstyle=style)`: cores por-card corretas de fato, hover nativo, seta "➜", padding maior (mais alto). Smoke confirma 6 estilos distintos.
- [x] T2 — Todas as telas movidas para `src/views/` como mixins (ver Resultado). `config_view` incluída.
- [x] T3 — `dashboards` → `views/dashboards_view.py::DashboardsMixin`.
- [x] T4 — `historico_publicadores` → `views/publicadores_view.py`.
- [x] T5 — `designacoes_salao` → `views/designacoes_view.py`.
- [x] T6 — `historico` + `historico_final_semana` → `views/historico_view.py`; `criar_reuniao_final_semana` → `views/reunioes_view.py`.
- [x] T7 — `ModernApp` reduzido a menu + bootstrap (`__init__` + `create_card`), 324 linhas. `shell.py` dedicado não foi necessário — o menu cabe no `__init__` enxuto.
- [x] T8 — `CLAUDE.md` atualizado; `JW_Mural.spec` com `src/views` + hiddenimports dos 8 módulos. `build.bat`/entry point inalterados (`layout.py` continua o entry).

## Resultado (2026-07-09)

| Módulo | Mixin | Telas | Linhas |
|---|---|---|---|
| `views/publicadores_view.py` | `PublicadoresMixin` | publicadores, historico_publicadores | 1232 |
| `views/historico_view.py` | `HistoricoMixin` | historico, historico_final_semana | 927 |
| `views/reunioes_view.py` | `ReunioesMixin` | criar_quadro_de_anuncio, criar_reuniao_final_semana | 374 |
| `views/designacoes_view.py` | `DesignacoesMixin` | designacoes_salao | 695 |
| `views/dashboards_view.py` | `DashboardsMixin` | dashboards | 270 |
| `views/config_view.py` | `ConfigMixin` | abrir_configuracoes | 93 |

`class ModernApp(PublicadoresMixin, HistoricoMixin, ReunioesMixin, DesignacoesMixin, DashboardsMixin, ConfigMixin)`.

Método de extração: script mecânico movendo os blocos verbatim (fidelidade byte-a-byte), não reescrita manual — evita bugs de transcrição em 3600 linhas.

### Verificação

1. Syntax OK em todos os módulos.
2. AST undefined-name check: 0 nomes não resolvidos em qualquer mixin.
3. Smoke headless: `ModernApp` instancia, 9 métodos herdados via MRO, 8 cards.
4. **Cada uma das 9 telas abre sem erro** (driver headless com DB falso + Messagebox no-op).
5. `pytest` verde (13).

## 6. Critérios de Aceite

1. ✅ App instancia e as 9 telas abrem (verificado headless, antes e depois da camada de serviço). Bodies movidos verbatim ⇒ comportamento idêntico. *Falta QA visual interativo com Mongo real.*
2. 🟡 `historico_view` (927) e `publicadores_view` (1232) ainda passam de ~600 linhas — cada arquivo agrupa 2 telas grandes. Dividir 1-tela-por-arquivo é refino futuro.
3. ✅ **Atingido** — `grep "db_ops\|from database\|DatabaseOperations" src/views/*.py` = ZERO. As views falam só com `src/services/`.
4. ✅ `pytest` verde após a refatoração.
5. ✅ `python src/layout.py` continua sendo o entry funcional.

## Camada de serviço (R3/R4) — ✅ concluída (2026-07-09)

`src/services/` criado; único código de UI que importa `database`:

| Serviço | Métodos | Usado por |
|---|---|---|
| `publicador_service` | listar, adicionar, excluir, atualizar, buscar_historico, resetar_todo_historico, restaurar_historico | publicadores_view |
| `reuniao_service` | listar, buscar, salvar, salvar/listar/buscar/excluir_final_semana | historico_view |
| `designacao_service` | listar_candidatos, salvar, listar, buscar, excluir | designacoes_view |
| `dashboard_service` | contar_participacoes_por_parte, contar_participacoes_unicas_por_reuniao, contar_designacoes_por_publicador | dashboards_view |

Delegam ao singleton `db_ops` (não instanciam `DatabaseOperations()` a cada chamada — evita recriar índices). Acesso raw à collection (restaurar histórico no rename) foi encapsulado em `publicador_service.restaurar_historico`.

Verificação: AST undefined-name = 0 nas views; 9 telas abrem com a camada; `pytest` verde (13); spec atualizado (`src/services` + hiddenimports).

### Refino futuro (opcional)

- [ ] Dividir `publicadores_view` e `historico_view` em 1 arquivo por tela (< 600 linhas).
- [ ] Converter mixins em classes-view (`__init__(parent, service)`) se o desacoplamento justificar.
- [ ] Rotear também backup/restore (`config_view` → `util.backup`) por um serviço, se quiser purismo total.

## Builder de executável (auditoria)

- `JW_Mural.spec` — adicionados `('src/views','views')` e `('src/services','services')` em `datas`, e os módulos em `hiddenimports`. Mesmo padrão já usado por `database`/`process`/`util` (comprovado).
- `JW_Mural.iss` — **sem mudança**: `[Files]` usa `Source: "dist\JW_Mural\*"; recursesubdirs` → instala tudo que o PyInstaller gerar.
- `build.bat` — **sem mudança**: só invoca a spec + Inno.
- Entry point `src/layout.py` inalterado.

## 7. Riscos

- `build.bat` / PyInstaller referencia entry point e imports — atualizar spec ao
  mudar `layout.py`. Manter `layout.py` como shim temporário reduz risco.
- Estado compartilhado por closure é sutil; migração tela-a-tela + teste manual
  a cada passo contém o risco.
- Sem os testes do SDD 02, esta refatoração é arriscada — respeitar a dependência.
