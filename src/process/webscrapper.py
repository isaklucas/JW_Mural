import requests
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



class webscrapper:
    def executar(url):
        print("Iniciando o webscrapper: " + url )
        response = requests.get(url)
        if response.status_code == 200:
        
                # Analisando o HTML com BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                return soup
        else:
            return None
    
    def executarBuscaURL(url):
        response = requests.get(url)
        if response.status_code == 200:
        
            # Analisando o HTML com BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            link = soup.find('a', class_='cardLine1Prominent')
            
            if link and 'href' in link.attrs:
                return link['href']
            else:
                return None
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
        
        for i in range(qtd_semanas):
            num_semana = num_inicial + i
            url_semana = f"{base_url}/{ano}/{num_semana}"
            soup = webscrapper.executar(url_semana)
            if not soup:
                continue
            
            cards = soup.find_all('a', class_='cardLine1Prominent')
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
        
        return resultados