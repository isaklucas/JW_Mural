"""Testes do parser do scraper — offline, via fixtures HTML e monkeypatch."""
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from process.webscrapper import webscrapper

FIXTURES = Path(__file__).parent / "fixtures"
URL = "https://wol.jw.org/pt/wol/meetings/r5/lp-t/2026/6"


def _soup(nome):
    html = (FIXTURES / nome).read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")


def test_extrai_titulo_sentinela(monkeypatch):
    soup = _soup("sentinela_meetings.html")
    monkeypatch.setattr(webscrapper, "executar", lambda url: soup)

    res = webscrapper.extrair_titulos_sentinela_meetings(URL, qtd_semanas=1)

    assert len(res) == 1
    assert res[0]["titulo_estudo"] == "A alegria de Jeová é a nossa fortaleza"
    assert res[0]["semana"] == res[0]["titulo_estudo"]
    # campos que o parser deixa vazios para preenchimento posterior
    assert res[0]["tema_discurso"] == ""
    assert res[0]["orador"] == ""
    assert res[0]["leitor_sentinela"] == ""


def test_ignora_card_que_nao_e_sentinela(monkeypatch):
    # página com cards, mas nenhum "Sentinela (Estudo)" -> sem dados, sem aviso
    soup = _soup("sentinela_vazio.html")
    monkeypatch.setattr(webscrapper, "executar", lambda url: soup)

    res = webscrapper.extrair_titulos_sentinela_meetings(URL, qtd_semanas=1)

    assert res == []


def test_pagina_sem_estrutura_loga_aviso(monkeypatch, caplog):
    # nenhum cardLine1Prominent -> retorna [] E avisa que estrutura pode ter mudado
    soup = _soup("sem_estrutura.html")
    monkeypatch.setattr(webscrapper, "executar", lambda url: soup)

    with caplog.at_level(logging.WARNING, logger="process.webscrapper"):
        res = webscrapper.extrair_titulos_sentinela_meetings(URL, qtd_semanas=1)

    assert res == []
    assert any("estrutura de wol.jw.org" in r.message for r in caplog.records)


def test_multiplas_semanas_iteram_urls(monkeypatch):
    # cada semana devolve o mesmo título; confirma que qtd_semanas controla o total
    soup = _soup("sentinela_meetings.html")
    urls_chamadas = []

    def fake_executar(url):
        urls_chamadas.append(url)
        return soup

    monkeypatch.setattr(webscrapper, "executar", fake_executar)

    res = webscrapper.extrair_titulos_sentinela_meetings(URL, qtd_semanas=3)

    assert len(res) == 3
    # incrementa o mês na URL: 2026/6 -> 2026/7 -> 2026/8
    assert urls_chamadas[0].endswith("/2026/6")
    assert urls_chamadas[1].endswith("/2026/7")
    assert urls_chamadas[2].endswith("/2026/8")


def test_url_invalida_retorna_vazio():
    # URL sem ano/mês numéricos -> retorno controlado, sem exceção
    assert webscrapper.extrair_titulos_sentinela_meetings("http://x", qtd_semanas=1) == []


def test_get_falha_de_rede_retorna_none(monkeypatch):
    # _get devolvendo None (rede caiu) -> executar retorna None, sem estourar
    import process.webscrapper as ws

    monkeypatch.setattr(ws, "_get", lambda url: None)
    assert ws.webscrapper.executar("http://qualquer") is None
