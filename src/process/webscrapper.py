import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import docx
import os
import subprocess
import re
from database import post, getAllPub, delete
import tkinter as tk
from tkinter import simpledialog
from enum import Enum
import datetime

logger = logging.getLogger(__name__)

# (connect, read) em segundos — evita thread travada se wol.jw.org não responder
_TIMEOUT = (8, 20)
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def _build_session():
    """Sessão HTTP com retry/backoff em erros de rede e 5xx."""
    s = requests.Session()
    retry = Retry(
        total=2,
        backoff_factor=0.5,  # espera 0s, 0.5s entre tentativas
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.headers.update(_HEADERS)
    return s


_session = _build_session()


def _get(url):
    """GET robusto (timeout + retry). Retorna Response ou None (com log)."""
    try:
        resp = _session.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp
    except requests.exceptions.Timeout:
        logger.warning("Timeout ao acessar %s", url)
    except requests.exceptions.RequestException as e:
        logger.warning("Falha de rede em %s: %s", url, e)
    return None


class webscrapper:
    def executar(url):
        print("Iniciando o webscrapper: " + url)
        response = _get(url)
        if response is None:
            return None
        # Analisando o HTML com BeautifulSoup
        return BeautifulSoup(response.text, "html.parser")

    def executarBuscaURL(url):
        response = _get(url)
        if response is None:
            return None

        # Analisando o HTML com BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        link = soup.find('a', class_='cardLine1Prominent')

        if link and 'href' in link.attrs:
            return link['href']
        else:
            return None

    def extrair_titulos_sentinela_meetings(url, qtd_semanas=5):
        """
        Extrai os títulos do estudo da Sentinela da página de meetings.
        Cada URL (ano/mês) retorna uma semana. Itera 5 vezes incrementando o mês:
        ex: 2026/6 -> 2026/7 -> 2026/8 -> 2026/9 -> 2026/10
        
        Args:
            url: URL da página de meetings (ex: https://wol.jw.org/pt/wol/meetings/r5/lp-t/2026/6)
            qtd_semanas: Quantidade de semanas a extrair (padrão 5)
            
        Returns:
            Lista de dicts com 'semana', 'titulo_estudo', 'tema_discurso', 'orador', 'leitor_sentinela'
        """
        resultados = []
        partes = url.rstrip('/').split('/')
        if len(partes) < 2:
            return resultados
        
        try:
            ano = int(partes[-2])
            num_inicial = int(partes[-1])
        except (ValueError, IndexError):
            return resultados
        
        base_url = '/'.join(partes[:-2])
        paginas_ok = 0  # páginas que carregaram e tinham a estrutura esperada

        for i in range(qtd_semanas):
            num_semana = num_inicial + i
            url_semana = f"{base_url}/{ano}/{num_semana}"
            soup = webscrapper.executar(url_semana)
            if not soup:
                continue

            cards = soup.find_all('a', class_='cardLine1Prominent')
            if cards:
                paginas_ok += 1
            titulo = ""
            
            for card in cards:
                card_line2 = card.find('div', class_='cardLine2')
                if not card_line2 or 'Sentinela (Estudo)' not in card_line2.get_text():
                    continue
                card_line1 = card.find('div', class_='cardLine1')
                texto_line1 = card_line1.get_text() if card_line1 else ""
                texto_line1 = " ".join(texto_line1.split()).strip()
                titulo = texto_line1
                periodo_semana = texto_line1
                break
            
            if titulo:
                resultados.append({
                    'semana': periodo_semana,
                    'titulo_estudo': titulo,
                    'tema_discurso': '',
                    'orador': '',
                    'leitor_sentinela': ''
                })

        # Distingue "sem dados" de "estrutura de wol.jw.org mudou": se nenhuma
        # página trouxe os cards esperados, o layout do site provavelmente mudou.
        if paginas_ok == 0:
            logger.warning(
                "Nenhum card 'cardLine1Prominent' encontrado em %d página(s) a "
                "partir de %s — estrutura de wol.jw.org pode ter mudado.",
                qtd_semanas, url,
            )

        return resultados