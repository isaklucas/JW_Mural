# SDD 02 — Testes do Miolo (parser + designação)

**Status:** ✅ Implementado (2026-07-09) — 13 testes, verde offline
**Prioridade:** P2 (~1 dia)
**Módulos alvo:** `src/process/webscrapper.py`, `src/process/s140.py`
**Depende de:** SDD 01 (scraper estável antes de fixar comportamento)
**Bloqueia:** SDD 03 (rede de segurança antes de refatorar `layout.py`)

---

## 1. Problema

Zero testes no projeto. Toda validação é manual, rodando a GUI. Duas áreas de
lógica pura e crítica quebram silenciosamente:

- **Parser do scraper** (`extrair_titulos_sentinela_meetings`): depende do HTML
  de wol.jw.org. Quando o site muda, ninguém percebe até gerar documento errado.
- **Designação automática** (`s140.selecionar_publicadores_automaticamente`,
  `s140.py:376`): distribui publicadores por papel (Ancião, Servo Min., etc.)
  com regras `pick_one_ciclo`, `pick_two_escola`, `pick_estudo`,
  `adicionar_a_assigned`. Bug aqui = designação injusta/inválida silenciosa.

Refatorar `layout.py` (SDD 03) sem testes = regressão garantida.

## 2. Objetivo

Suíte `pytest` cobrindo **lógica pura** (sem GUI, sem rede, sem DB real).
~20 testes no miolo que quebra. Rodável offline em segundos.

**Fora de escopo:** testar a GUI ttkbootstrap, testar rede real, cobertura 100%.

## 3. Requisitos

| # | Requisito |
|---|-----------|
| R1 | `pytest` roda sem internet e sem MongoDB. |
| R2 | Parser testado com fixture HTML salvo (snapshot real de wol.jw.org). |
| R3 | Designação automática testada com publicadores fake em memória. |
| R4 | DB abstraído/mockado — testes não tocam Mongo. |
| R5 | Um comando único roda tudo: `pytest`. |
| R6 | CI opcional: workflow GitHub Actions rodando `pytest` no push. |

## 4. Design

### 4.1 Estrutura

```
tests/
  __init__.py
  conftest.py                 # fixtures compartilhadas, mock de DB
  fixtures/
    sentinela_meetings.html   # snapshot real de wol.jw.org (1 semana)
    sentinela_vazio.html      # página sem card de Sentinela
  test_webscrapper.py
  test_designacao.py
pytest.ini                    # config (testpaths, etc.)
```

### 4.2 Testar o parser sem rede

Problema: `extrair_titulos_sentinela_meetings` chama `webscrapper.executar(url)`
que faz rede. Solução: refatorar mínimo para injetar o `soup`, OU monkeypatchar
`executar`.

```python
# test_webscrapper.py
from bs4 import BeautifulSoup
from process.webscrapper import webscrapper

def test_extrai_titulo_sentinela(monkeypatch):
    html = open("tests/fixtures/sentinela_meetings.html", encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    monkeypatch.setattr(webscrapper, "executar", lambda url: soup)

    res = webscrapper.extrair_titulos_sentinela_meetings(
        "https://wol.jw.org/pt/wol/meetings/r5/lp-t/2026/6", qtd_semanas=1)

    assert len(res) == 1
    assert res[0]["titulo_estudo"]          # não vazio
    assert "semana" in res[0]

def test_pagina_sem_sentinela_retorna_vazio(monkeypatch):
    html = open("tests/fixtures/sentinela_vazio.html", encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    monkeypatch.setattr(webscrapper, "executar", lambda url: soup)
    res = webscrapper.extrair_titulos_sentinela_meetings("...", qtd_semanas=1)
    assert res == []
```

### 4.3 Testar designação automática

`selecionar_publicadores_automaticamente(partesPorSemana, salvar_imediatamente=False)`
já tem flag para NÃO tocar o DB. Montar `partesPorSemana` fake + lista de
publicadores fake e verificar invariantes:

```python
# test_designacao.py
def test_nao_repete_publicador_na_mesma_semana(publicadores_fake, partes_fake):
    s140.selecionar_publicadores_automaticamente(
        partes_fake, salvar_imediatamente=False)
    for semana in partes_fake:
        nomes = [p["publicador"] for p in semana["partes"] if p["publicador"]]
        assert len(nomes) == len(set(nomes))   # sem duplicata na semana

def test_respeita_papel(publicadores_fake, partes_fake):
    # parte que exige Ancião não recebe publicador comum
    ...

def test_distribui_carga(publicadores_fake, partes_fake):
    # ninguém recebe 2x enquanto outro do mesmo papel tem 0
    ...
```

`getAllPub` / `post` mockados via `conftest.py` (monkeypatch em
`process.s140` ou injeção). Confirmar a fonte real dos nomes ao implementar.

### 4.4 Mock de DB

```python
# conftest.py
import pytest

@pytest.fixture
def publicadores_fake():
    return [
        {"nome": "Irmão A", "papel": "Anciao", "participacoes": 0},
        {"nome": "Irmão B", "papel": "Servo",  "participacoes": 3},
        # ...
    ]

@pytest.fixture(autouse=True)
def sem_db(monkeypatch):
    # bloqueia qualquer chamada real ao Mongo durante os testes
    ...
```

## 5. Tarefas

- [x] T1 — `requirements-dev.txt` (pytest) + `pytest.ini` (`testpaths=tests`, `pythonpath=src`).
- [x] T2 — Fixtures HTML em `tests/fixtures/` (`sentinela_meetings`, `sentinela_vazio`, `sem_estrutura`). **Desvio:** sintéticas (casam com os seletores do parser), não snapshot real — rede indisponível na hora. Trocar por snapshot real de wol.jw.org quando possível (comentado nos arquivos).
- [x] T3 — `test_webscrapper.py`: 6 testes (extrai título, ignora não-Sentinela, avisa estrutura quebrada, itera URLs por mês, URL inválida, falha de rede→None).
- [x] T4 — Estrutura mapeada. `partesPorSemana[i]` usa chaves `semana`, `estudoDiscurso`, `escola4`, `nvcP2`; algoritmo escreve `Participantes` (dict com Presidente, OracaoInicial, ...). `db_ops` é a dependência (listas ordenadas + `obter_sexo_publicador` + `salvar_reuniao`).
- [x] T5 — `conftest.py`: injeta módulo `database` FALSO em `sys.modules` antes do import (contorna conexão Mongo no import), `FakeDbOps` configurável, `__getattr__` no-op para símbolos extras.
- [x] T6 — `test_designacao.py`: 7 testes (sem repetição na semana, oração final=presidente, rotação de presidente, pool vazio→"não possui", partes ausentes, `salvar_imediatamente` False/True). **Desvio:** "respeita papel" NÃO é unit — a regra de papel/permissão vive na query do `db_ops` real → cobrir em teste de integração, não aqui.
- [x] T7 — `.github/workflows/test.yml` roda `pytest` no push/PR (windows-latest, py3.13).

## 6. Critérios de Aceite

1. `pytest` verde offline, sem Mongo, em <5s.
2. Alterar o HTML da fixture (simular mudança do site) → teste do parser falha.
3. Quebrar regra de designação → teste correspondente falha.
4. Nenhum teste escreve no banco real.

## 7. Riscos

- Estrutura interna de `partesPorSemana` pode ser mais complexa que o esperado;
  T4 (mapeamento) precede a escrita dos testes de designação.
- Imports do `s140.py` puxam `tkinter`/`docx` no topo — pode exigir isolar a
  lógica pura ou tolerar o import em ambiente headless.
