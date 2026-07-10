# SDD 01 — Robustez do Webscrapper

**Status:** ✅ Implementado (2026-07-09)
**Prioridade:** P1 (crítico, ~30 min)
**Módulo alvo:** `src/process/webscrapper.py`
**Depende de:** nada
**Bloqueia:** SDD 02 (fixtures de teste do parser)

---

## 1. Problema

`webscrapper.py` faz `requests.get(url)` cru em 3 pontos (`executar`,
`executarBuscaURL`, e via `executar` dentro de `extrair_titulos_sentinela_meetings`):

```python
response = requests.get(url)          # linha 18, 28
```

Falhas:

- **Sem `timeout`** → se wol.jw.org lento/caído, a thread de scraping trava
  indefinidamente. UI mostra spinner infinito ("app em execução").
- **Sem `User-Agent`** → servidor pode responder 403/bloquear bot.
- **Sem retry/backoff** → soluço de rede = erro seco, usuário reinicia tudo.
- **Sem tratamento de exceção** (`ConnectionError`, `Timeout`, DNS) → estoura
  stacktrace na thread, sem mensagem clara.
- **Sem validação de estrutura** → se wol.jw.org muda o HTML, `find_all` retorna
  `[]` e a função devolve lista vazia silenciosa. Usuário acha que "não tem
  reunião" quando na verdade o scraper quebrou.

## 2. Objetivo

Toda chamada de rede: com timeout, User-Agent, retry, exceção tratada e sinal
claro de falha propagado à UI. Zero mudança na assinatura pública das funções
(`executar`, `executarBuscaURL`, `extrair_titulos_sentinela_meetings`).

## 3. Requisitos

| # | Requisito |
|---|-----------|
| R1 | Toda requisição HTTP usa `timeout` (conexão + leitura). Default 15s. |
| R2 | Toda requisição envia header `User-Agent` de navegador real. |
| R3 | Retry automático com backoff exponencial em erro de rede / 5xx (3 tentativas). |
| R4 | Exceções de rede capturadas e convertidas em retorno controlado + log. |
| R5 | Quando o HTML não bate com a estrutura esperada, distinguir "sem dados" de "estrutura quebrou" e logar aviso. |
| R6 | Assinaturas públicas inalteradas (chamadores em `s140.py` / `final_semana.py` não mudam). |

## 4. Design

### 4.1 Sessão HTTP centralizada

Criar um único ponto de saída de rede reutilizado por todas as funções:

```python
import logging
import requests
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)

_TIMEOUT = (10, 20)  # (connect, read)
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}

def _build_session():
    s = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1.0,              # 0s, 1s, 2s
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update(_HEADERS)
    return s

_session = _build_session()

def _get(url):
    """Requisição GET robusta. Retorna Response ou None (com log)."""
    try:
        resp = _session.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp
    except requests.exceptions.Timeout:
        logger.warning("Timeout ao acessar %s", url)
    except requests.exceptions.RequestException as e:
        logger.warning("Falha de rede em %s: %s", url, e)
    return None
```

### 4.2 Refatorar funções existentes

- `executar(url)` → usa `_get`; retorna `soup` ou `None`.
- `executarBuscaURL(url)` → usa `_get`; mesma lógica de extração do `href`.
- `extrair_titulos_sentinela_meetings` → já chama `executar`, herda robustez.
  Adicionar contador: se `soup` OK mas `cards == []` em TODAS as semanas,
  logar aviso "estrutura de wol.jw.org pode ter mudado".

### 4.3 Sinal para a UI

`_get` retornando `None` já é o contrato atual (funções devolvem `None`/`[]`).
A camada de UI (`layout.py::processar_geracao`) deve tratar retorno vazio com
mensagem específica: *"Não foi possível acessar wol.jw.org. Verifique a conexão."*
em vez de spinner infinito. (Ajuste pequeno no chamador.)

## 5. Tarefas

- [x] T1 — Adicionar `logging`, `_HEADERS`, `_TIMEOUT`, `_build_session`, `_get` no topo de `webscrapper.py`.
- [x] T2 — Reescrever `executar` e `executarBuscaURL` para usar `_get`.
- [x] T3 — Adicionar detecção de "estrutura quebrada" em `extrair_titulos_sentinela_meetings` (aviso quando 0 cards em todas semanas).
- [x] T4 — Chamador `layout.py::processar_geracao` já tinha try/except + messagebox + esconder_loading; `_get` retorna `None` sem estourar, então falha de rede não trava a UI. Sem mudança necessária. `updater.py` já usava timeout+raise_for_status.
- [x] T5 — Teste funcional: host inalcançável falha limpo (bounded, sem hang infinito), `_get` captura `RequestException` → `None`. Config nova: `total=2` retries, `backoff=0.5`, connect timeout 8s.

## 6. Critérios de Aceite

1. Internet desligada → geração falha com mensagem clara em ≤20s, sem travar UI.
2. wol.jw.org acessível → resultado idêntico ao comportamento atual.
3. Erro 503 transitório → retry automático recupera sem intervenção.
4. Nenhuma mudança nas assinaturas de `s140.py` / `final_semana.py`.

## 7. Riscos

- `requests.Session` global + threads: `Session` é thread-safe para GET simples;
  ok para o uso atual. Se surgir concorrência pesada, criar sessão por thread.
- `Retry` precisa de `urllib3` (já vem com `requests`). Sem dependência nova.
