import requests
from bs4 import BeautifulSoup
import docx
import os
import subprocess
import re
from database import db_ops
import tkinter as tk
from tkinter import simpledialog
from enum import Enum
import datetime
import process.webscrapper as webscrapper
import util.janelas as janela
from docx import Document
from docx.shared import Pt
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from docx.enum.text import WD_ALIGN_PARAGRAPH
import logging

logger = logging.getLogger(__name__)

class s140:
    def gerar_s140(urlEv, nomeEv, idiomaEv , preencherPubs, gerarComPublicadores, qntdSemanas, progress_cb=None):
        ## Busca Soup das Semanas

        listaSoupSemanas = s140.buscarSoupDasSemnas(urlEv, qntdSemanas, progress_cb)

        partesPorSemana = s140.extrair_partes(listaSoupSemanas, progress_cb)

        if preencherPubs:
            if gerarComPublicadores:
                # Usar seleção automática (sem salvar ainda)
                s140.selecionar_publicadores_automaticamente(partesPorSemana, salvar_imediatamente=False, progress_cb=progress_cb)
                
                # Mostrar resumo e permitir edição antes de gerar documento
                if not s140.mostrar_resumo_e_editar_publicadores(partesPorSemana):
                    # Usuário cancelou, não continuar
                    return
            else:
                # Inicializar Participantes vazios e abrir modal único (mesmo do automático)
                for semana in partesPorSemana:
                    semana['Participantes'] = {
                        'Presidente': '',
                        'OracaoInicial': '',
                        'Tesouro': '',
                        'Joias': '',
                        'Leitura': '',
                        'IniciandoConversa': '',
                        'CultivandoInteresse': '',
                        'EstudoDiscurso': 'não possui' if semana.get('estudoDiscurso') == 'não possui' else '',
                        'Escola4': 'não possui' if semana.get('escola4') == 'não possui' else '',
                        'Nvc1': '',
                        'Nvc2': 'não possui' if semana.get('nvcP2') == 'não possue esta Parte' else '',
                        'Estudo': '',
                        'OracaoFinal': '',
                    }
                if not s140.mostrar_resumo_e_editar_publicadores(partesPorSemana):
                    return  # Usuário cancelou

        if progress_cb:
            progress_cb("Gerando documento...", 90)
        s140.criarDocumentoApartirDoObjeto(partesPorSemana , preencherPubs , nomeEv , idiomaEv)

        if preencherPubs and not gerarComPublicadores:
            if progress_cb:
                progress_cb("Salvando histórico...", 95)
            s140.atualizarHistoricoPublicadores(partesPorSemana)

        if progress_cb:
            progress_cb("Concluído!", 100)
           
               
       
            
        
        
    def extrair_partes(listaSoupSemanas, progress_cb=None):
        listaPartesPorSemana = []
        total = len(listaSoupSemanas)
        for idx, soup in enumerate(listaSoupSemanas):
            if progress_cb:
                pct = 40 + int((idx + 1) / total * 20)
                progress_cb(f"Mapeando partes semana {idx + 1}...", pct)
            verificaSemana = soup.find(id="p1")               
            if verificaSemana != None:
                    ## Pega Semana
                    semana = soup.find(id="p1").get_text() 
                    
                    
                    ## Pega Capitulos
                    capituloVersiculo = soup.find(id="p2").get_text()
                    
                    
                    ## Pega cantico Inicial
                    canticoInicialTemp = soup.find(id="p3").get_text().split('|')
                    canticoInicial = canticoInicialTemp[0]
                    
                    
                    ## Pega Tesouro
                    tesouroTemp = soup.find(id="p5").get_text()
                    tesouro = tesouroTemp.split('1.')[1]
                    
                    
                    ## Pergunta das Joias
                    ## Topico a ser buscado
                    topico1 = "2. Joias espirituais"
                    # Encontre todas as tags h3 na página.
                    tags_h3 = soup.find_all("h3")
                    # Inicialize proxima_div com None antes do loop.
                    proxima_div = None
                    # Itere sobre as tags h3 e encontre aquela que contém o texto do tópico desejado.
                    for tag_h3 in tags_h3:
                        if tag_h3.get_text().startswith(topico1):
                            # Use find_next para encontrar a próxima div.
                            proxima_div = tag_h3.find_next("div")
                            # Saia do loop assim que a tag h3 desejada for encontrada.
                            break

                    # Verifique se a próxima div foi encontrada antes de tentar extrair o texto.
                    if proxima_div:
                            perguntaJoiastemp = proxima_div.get_text().split('\n')
                            perguntaJoias = perguntaJoiastemp[4]
                            
                    else:
                            print(f"Div após {topico1} não encontrada na página.")

                    ## Leitura da Semana
                    leituraSemana = None  
                    topico2 = "3. Leitura da Bíblia"      
                    # Inicialize proxima_div com None antes do loop.
                    proxima_div = None
                    # Itere sobre as tags h3 e encontre aquela que contém o texto do tópico desejado.
                    for tag_h3 in tags_h3:
                        if tag_h3.get_text().startswith(topico2):
                            # Use find_next para encontrar a próxima div.
                            proxima_div = tag_h3.find_next("div")
                            # Saia do loop assim que a tag h3 desejada for encontrada.
                            break

                    # Verifique se a próxima div foi encontrada antes de tentar extrair o texto.
                    if proxima_div:
                            leituraSemanatemp = proxima_div.get_text()
                            leituraSemanatemp2 = leituraSemanatemp.replace('\n', '').split(')')
                            leituraSemana = leituraSemanatemp2[1]
                            
                            
                    else:
                            print(f"Div após {topico2} não encontrada na página.")
                    
                    
                    ## Cantico do Meio
                    Canticos = soup.find_all("h3", class_="dc-icon--music")
                    canticoMeio = Canticos[1].get_text()
                    
                    
                    
                    ## Nossa vida Crista Partes
                    # Inicialize uma variável para contar o número de tags dc-icon--music encontradas.
                    contador_dc_icon_music = 0
                    # Itera sobre as tags h3 com seus índices.
                    for index, tag_h3 in enumerate(tags_h3):
                            if "dc-icon--music" in tag_h3.get("class", []):
                                    contador_dc_icon_music += 1

                                    if contador_dc_icon_music == 2:
                                    # Grava o conteúdo das 4 tags anteriores.
                                            anterior_tags = tags_h3[max(0, index - 4):index]

                                            # Grava o conteúdo das três tags seguintes.
                                            proximas_tags = tags_h3[index + 1:index + 4]

                                            # Inicializa variáveis com valores padrão
                                            iniciandoConversa = "não possui"
                                            cultivandoInteresse = "não possui"
                                            estudoDiscurso = "não possui"
                                            escola4 = "não possui"

                                            # Itera sobre as tags anteriores e atribui conforme o início do texto
                                            for i, anterior_tag in enumerate(anterior_tags):
                                                    texto_anterior = anterior_tag.get_text().strip()

                                                    if texto_anterior.startswith("4."):
                                                            iniciandoConversa = texto_anterior
                                                    elif texto_anterior.startswith("5."):
                                                            cultivandoInteresse = texto_anterior
                                                    elif texto_anterior.startswith("6."):
                                                            estudoDiscurso = texto_anterior
                                                    elif texto_anterior.startswith("7."):
                                                            escola4 = texto_anterior

                                            # Grava o conteúdo das três tags seguintes.
                                            nvcP1 = proximas_tags[0].get_text() if proximas_tags else "não possui"
                                            nvcP2 = proximas_tags[1].get_text() if len(proximas_tags) > 1 else "não possui"
                                            estudo = proximas_tags[2].get_text() if len(proximas_tags) > 2 else "não possui"

                                            break
                                                            
                    
                    ## Ajuste caso nao aja parte 2
                    if 'Estudo bíblico' in nvcP2:
                            estudo = nvcP2 
                            nvcP2 = "não possue esta Parte"
                            
                    
                    ## Estudo Biblico
                    topico1 = estudo
                    # Encontre todas as tags h3 na página.
                    tags_h3 = soup.find_all("h3")
                    # Inicialize proxima_div com None antes do loop.
                    proxima_div = None
                    # Itere sobre as tags h3 e encontre aquela que contém o texto do tópico desejado.
                    for tag_h3 in tags_h3:
                        if tag_h3.get_text().startswith(topico1):
                            # Use find_next para encontrar a próxima div.
                            proxima_div = tag_h3.find_next("div")
                            # Saia do loop assim que a tag h3 desejada for encontrada.
                            break

                    # Verifique se a próxima div foi encontrada antes de tentar extrair o texto.
                    if proxima_div:
                            estudoTemp = proxima_div.get_text().split(')')
                            estudo = estudo +  estudoTemp[1].replace('\n', '')                                               
                            
                    else:
                            print(f"Div após {topico1} não encontrada na página.")
                            
                            
                    # Variável para armazenar o texto dentro da tag "Comentários finais"
                    texto_comentarios_finais = None

                    # Procurar pela tag que contém o texto "Comentários finais"
                    for tag in tags_h3:
                            if "Comentários finais" in tag.get_text():
                                    # Se encontrarmos a tag, podemos imprimir ou fazer o que for necessário com ela
                                    #print("Tag com 'Comentários finais':", tag)
                                    # Extrair o texto da tag, se necessário
                                    texto_comentarios_finais = tag.get_text()
                                    #print("Texto dentro da tag:", texto_comentarios_finais)
                                    break  # Interromper o loop, já que encontramos o que queríamos
                            

                    # Se encontramos o texto dentro da tag "Comentários finais", procedemos com a extração da segunda parte
                    if texto_comentarios_finais:
                            # Dividir o texto pelo caractere "|"
                            partes = texto_comentarios_finais.split("|")
                            if len(partes) >= 2:
                                    # Atribuir a segunda parte à variável 'canticoFinal'
                                    canticoFinal = partes[1].strip()  # removendo espaços em branco em excesso
                                    #print('Cantico Final:', canticoFinal)
                            else:
                                    print("Não foi possível extrair a segunda parte do texto")
                    
                    parteSemana = {
                        'semana': semana,
                        'capituloVersiculo': capituloVersiculo,
                        'canticoInicial': canticoInicial,
                        'tesouro': tesouro,
                        'perguntaJoias': perguntaJoias,
                        'leituraSemana': leituraSemana,
                        'iniciandoConversa': iniciandoConversa,
                        'cultivandoInteresse': cultivandoInteresse,
                        'estudoDiscurso': estudoDiscurso,
                        'escola4': escola4,
                        'canticoMeio': canticoMeio,
                        'nvcP1': nvcP1,
                        'nvcP2': nvcP2,
                        'estudo': estudo,
                        'canticoFinal': canticoFinal
                    }
                    print(parteSemana)
                    listaPartesPorSemana.append(parteSemana)
        
        return listaPartesPorSemana           
                    
   
    def buscarSoupDasSemnas(urlEv, qntdSemanas, progress_cb=None):
        urlEnviada = urlEv
        baseJWURL = "https://wol.jw.org"

        # Pega a Semana que está na URL
        urlSplit = urlEnviada.split("/")
        semanas = urlSplit[len(urlSplit) - 1]

        # Variaveis utilizadas para os For e montar a Url novamente
        tamanhoURL = len(urlSplit)
        x = int(semanas)
        y = x+qntdSemanas
        base_url = ''

        for v in range(0, tamanhoURL-1) :
                if v == 0 :
                        base_url = base_url  + urlSplit[v]
                else : base_url = base_url + "/" + urlSplit[v]

        linkSemanas = []
        listaSoupSemanas = []

        print("Iniciando Busca de URL Semanas ")
        for i in range(x, y):
            sem_num = i - x + 1
            if progress_cb:
                pct = int(sem_num / qntdSemanas * 30)
                progress_cb(f"Buscando reunião semana {sem_num}...", pct)
            url = base_url + "/" + str(i)
            link = webscrapper.webscrapper.executarBuscaURL(url)
            linkSemanas.append(link)

        print("Links das Semanas Encontradas: ", linkSemanas)
        for idx, link in enumerate(linkSemanas):
            if progress_cb:
                pct = 30 + int((idx + 1) / len(linkSemanas) * 10)
                progress_cb(f"Carregando conteúdo semana {idx + 1}...", pct)
            urlCompleta = baseJWURL + link
            print("Iniciando Busca de Soup Semana : " + urlCompleta )
            soupSemana = webscrapper.webscrapper.executar(urlCompleta)
            listaSoupSemanas.append(soupSemana)

        return listaSoupSemanas
    
        
    def solicitarNomePublicadorPartes(partesPorSemana):
        ## para cada semana
        publicadores = db_ops.getAllPub()
        nomes_publicadores = [pub['nome'] for pub in publicadores]
        print(nomes_publicadores)
        for semana in partesPorSemana:
            nomePresidente = janela.janelas.solicitar_nome_publicador("Presidente", nomes_publicadores, semana['semana'])
            nome_oracaoInicial = janela.janelas.solicitar_nome_publicador("Oraçao Inicial", nomes_publicadores, semana['semana'])
            nome_tesouro = janela.janelas.solicitar_nome_publicador("Tesouro", nomes_publicadores, semana['semana'])
            nome_joias = janela.janelas.solicitar_nome_publicador("Joias", nomes_publicadores, semana['semana'])
            nome_leitura = janela.janelas.solicitar_nome_publicador("Leitura", nomes_publicadores, semana['semana'])
            nome_iniciandoConversa = janela.janelas.solicitar_nome_publicador("Iniciando Conversa", nomes_publicadores, semana['semana'])
            nome_cultivandoInteresse = janela.janelas.solicitar_nome_publicador("Cultivando Interesse", nomes_publicadores, semana['semana'])
            
            if semana['estudoDiscurso'] != "não possui":
                nome_estudoDiscurso = janela.janelas.solicitar_nome_publicador("Estudo ou Discurso", nomes_publicadores, semana['semana'])
            else: 
                nome_estudoDiscurso = "não possui"
            
            if semana['escola4'] != "não possui":
                nome_escola4 = janela.janelas.solicitar_nome_publicador("Escola Parte 4", nomes_publicadores, semana['semana'])
            else:
                nome_escola4 = "não possui"
            
            nome_nvc1 = janela.janelas.solicitar_nome_publicador("NVC Parte 1", nomes_publicadores, semana['semana'])
            
            if semana['nvcP2'] != "não possue esta Parte":
                nome_nvc2 = janela.janelas.solicitar_nome_publicador("NVC Parte 2", nomes_publicadores, semana['semana'])
            else:
                nome_nvc2 = "não possui"
            
            nome_estudo = janela.janelas.solicitar_nome_publicador("Estudo e leitor", nomes_publicadores, semana['semana'])
            
            participantes = {
                'Presidente': nomePresidente,
                'OracaoInicial': nome_oracaoInicial,
                'Tesouro': nome_tesouro,
                'Joias': nome_joias,
                'Leitura': nome_leitura,
                'IniciandoConversa': nome_iniciandoConversa,
                'CultivandoInteresse': nome_cultivandoInteresse,
                'EstudoDiscurso': nome_estudoDiscurso,
                'Escola4': nome_escola4,
                'Nvc1': nome_nvc1,
                'Nvc2': nome_nvc2,
                'Estudo': nome_estudo,
                'OracaoFinal': nomePresidente
            }
            
            semana['Participantes'] = participantes
            
        return partesPorSemana
    
    def selecionar_publicadores_automaticamente(partesPorSemana, salvar_imediatamente=True, progress_cb=None):
        """
        Seleciona automaticamente publicadores para todas as partes de todas as semanas:
        ordenar por quem fez MENOS a parte, distribuir em ciclo (semana i → posição i % len)
        e evitar que a mesma pessoa faça duas partes na mesma semana (avançar na lista se choque).
        """
        print("Iniciando seleção automática de publicadores...")

        def pick_one_ciclo(lista, week_index, assigned):
            """Escolhe o primeiro candidato em ciclo (week_index % len) que não esteja em assigned."""
            if not lista:
                return "não possui"
            for j in range(len(lista)):
                k = (week_index + j) % len(lista)
                if lista[k] not in assigned:
                    return lista[k]
            return "não possui"

        def pick_two_escola(lista, week_index, assigned):
            """Escolhe dois da lista em ciclo, mesmo sexo, não em assigned. Retorna 'Nome1 / Nome2' ou um nome ou 'não possui'."""
            if not lista:
                return "não possui"
            base = (2 * week_index) % len(lista)
            for j in range(len(lista)):
                k1 = (base + j) % len(lista)
                p1 = lista[k1]
                if p1 in assigned:
                    continue
                sexo1 = db_ops.obter_sexo_publicador(p1)
                for j2 in range(1, len(lista)):
                    k2 = (base + j + j2) % len(lista)
                    p2 = lista[k2]
                    if p2 != p1 and p2 not in assigned and db_ops.obter_sexo_publicador(p2) == sexo1:
                        return f"{p1} / {p2}"
                return p1
            return "não possui"

        def pick_estudo(principais, ajudantes, week_index, assigned):
            """Principal em ciclo, depois ajudante em ciclo (evitando principal e assigned). Formato 'Principal / Ajudante'."""
            principal = pick_one_ciclo(principais, week_index, assigned)
            if principal == "não possui":
                return "não possui"
            assigned_com_principal = set(assigned) | {principal}
            ajudante = pick_one_ciclo(ajudantes, week_index, assigned_com_principal)
            if ajudante == "não possui":
                return principal
            return f"{principal} / {ajudante}"

        def adicionar_a_assigned(nome, assigned):
            if nome and nome != "não possui":
                for n in (p.strip() for p in nome.split("/")):
                    if n:
                        assigned.add(n.strip())

        # Listas ordenadas por menos participações (uma vez só)
        listas = {
            "Presidente": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Presidente"),
            "Oração Inicial": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Oração Inicial"),
            "Tesouro": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Tesouro"),
            "Joias Espirituais": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Joias Espirituais"),
            "Leitura da Bíblia": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Leitura da Bíblia"),
            "Escola - Primeira Parte": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Escola - Primeira Parte"),
            "Escola - Segunda Parte": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Escola - Segunda Parte"),
            "Escola - Terceira Parte": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Escola - Terceira Parte"),
            "Escola - Quarta Parte": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Escola - Quarta Parte"),
            "NVC1": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Nossa Vida Cristã - Primeira Parte"),
            "NVC2": db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Nossa Vida Cristã - Segunda Parte"),
        }
        lista_estudo_principais = db_ops.listar_candidatos_ordenados_por_menos_partecipacoes_meio("Estudo de Congregação")
        lista_estudo_ajudantes = db_ops.listar_ajudantes_estudo_ordenados_por_menos_partecipacoes()

        for i, semana in enumerate(partesPorSemana):
            print(f"Processando semana: {semana['semana']}")
            if progress_cb:
                pct = 60 + int((i + 1) / len(partesPorSemana) * 25)
                progress_cb(f"Selecionando publicadores semana {i + 1}...", pct)
            assigned_this_week = set()

            nome_presidente = pick_one_ciclo(listas["Presidente"], i, assigned_this_week)
            adicionar_a_assigned(nome_presidente, assigned_this_week)

            nome_oracao_inicial = pick_one_ciclo(listas["Oração Inicial"], i, assigned_this_week)
            adicionar_a_assigned(nome_oracao_inicial, assigned_this_week)

            nome_tesouro = pick_one_ciclo(listas["Tesouro"], i, assigned_this_week)
            adicionar_a_assigned(nome_tesouro, assigned_this_week)

            nome_joias = pick_one_ciclo(listas["Joias Espirituais"], i, assigned_this_week)
            adicionar_a_assigned(nome_joias, assigned_this_week)

            nome_leitura = pick_one_ciclo(listas["Leitura da Bíblia"], i, assigned_this_week)
            adicionar_a_assigned(nome_leitura, assigned_this_week)

            nome_iniciando_conversa = pick_two_escola(listas["Escola - Primeira Parte"], i, assigned_this_week)
            adicionar_a_assigned(nome_iniciando_conversa, assigned_this_week)

            nome_cultivando_interesse = pick_two_escola(listas["Escola - Segunda Parte"], i, assigned_this_week)
            adicionar_a_assigned(nome_cultivando_interesse, assigned_this_week)

            if semana['estudoDiscurso'] != "não possui" and ("Discurso" in (semana.get('estudoDiscurso') or '') or "discurso" in (semana.get('estudoDiscurso') or '')):
                nome_estudo_discurso = pick_one_ciclo(listas["Escola - Terceira Parte"], i, assigned_this_week)
            else:
                nome_estudo_discurso = pick_two_escola(listas["Escola - Terceira Parte"], i, assigned_this_week) if semana.get('estudoDiscurso') != "não possui" else "não possui"
            adicionar_a_assigned(nome_estudo_discurso, assigned_this_week)

            nome_escola4 = pick_two_escola(listas["Escola - Quarta Parte"], i, assigned_this_week) if semana.get('escola4') != "não possui" else "não possui"
            adicionar_a_assigned(nome_escola4, assigned_this_week)

            nome_nvc1 = pick_one_ciclo(listas["NVC1"], i, assigned_this_week)
            adicionar_a_assigned(nome_nvc1, assigned_this_week)

            nome_nvc2 = pick_one_ciclo(listas["NVC2"], i, assigned_this_week) if semana.get('nvcP2') != "não possue esta Parte" else "não possui"
            adicionar_a_assigned(nome_nvc2, assigned_this_week)

            nome_estudo = pick_estudo(lista_estudo_principais, lista_estudo_ajudantes, i, assigned_this_week)
            adicionar_a_assigned(nome_estudo, assigned_this_week)

            nome_oracao_final = nome_presidente

            participantes = {
                'Presidente': nome_presidente,
                'OracaoInicial': nome_oracao_inicial,
                'Tesouro': nome_tesouro,
                'Joias': nome_joias,
                'Leitura': nome_leitura,
                'IniciandoConversa': nome_iniciando_conversa,
                'CultivandoInteresse': nome_cultivando_interesse,
                'EstudoDiscurso': nome_estudo_discurso,
                'Escola4': nome_escola4,
                'Nvc1': nome_nvc1,
                'Nvc2': nome_nvc2,
                'Estudo': nome_estudo,
                'OracaoFinal': nome_oracao_final
            }
            semana['Participantes'] = participantes

            if salvar_imediatamente:
                ano = datetime.datetime.now().year
                dados_reuniao = {
                    'ano': ano,
                    'semana': semana['semana'],
                    'data_reuniao': datetime.datetime.now().isoformat(),
                    'presidente': participantes['Presidente'],
                    'oracao_inicial': participantes['OracaoInicial'],
                    'tesouro': participantes['Tesouro'],
                    'joias_espirituais': participantes['Joias'],
                    'leitura_biblia': participantes['Leitura'],
                    'escola': {
                        'primeira_parte': participantes['IniciandoConversa'],
                        'segunda_parte': participantes['CultivandoInteresse'],
                        'terceira_parte': participantes['EstudoDiscurso'],
                        'quarta_parte': participantes['Escola4']
                    },
                    'nossa_vida_crista': {
                        'primeira_parte': participantes['Nvc1'],
                        'segunda_parte': participantes['Nvc2']
                    },
                    'estudo_congregacao': participantes['Estudo'],
                    'oracao_final': participantes['OracaoFinal']
                }
                resultado = db_ops.salvar_reuniao(dados_reuniao)
                if resultado['success']:
                    print(f"Reunião da semana {semana['semana']} salva com sucesso")
                else:
                    print(f"Erro ao salvar reunião da semana {semana['semana']}: {resultado['message']}")
            print(f"Seleção automática concluída para semana {semana['semana']}")
        print("Seleção automática de publicadores concluída para todas as semanas!")
    
    def mostrar_resumo_e_editar_publicadores(partesPorSemana):
        """
        Mostra uma janela modal com resumo de todas as semanas e permite editar os publicadores selecionados.
        
        Returns:
            bool: True se o usuário clicou em Salvar, False se cancelou
        """
        # Criar janela modal
        # Usar uma janela temporária como root
        temp_root = tk.Tk()
        temp_root.withdraw()  # Esconder janela temporária
        
        modal = ttk.Toplevel(temp_root)
        modal.title("Revisar e Editar Publicadores Selecionados")
        modal.geometry("900x700")
        modal.transient(temp_root)
        modal.grab_set()
        
        # Variável para controlar se salvou ou cancelou
        resultado_salvar = [False]
        
        # Container principal
        main_container = ttk.Frame(modal, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Título
        title_label = ttk.Label(
            main_container,
            text="Revisar Publicadores Selecionados",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para scroll
        scroll_frame = ttk.Frame(main_container)
        scroll_frame.pack(fill=BOTH, expand=YES)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Dicionário para armazenar os campos de entrada por semana
        campos_por_semana = {}
        
        # Buscar lista de publicadores para autocomplete
        publicadores = db_ops.getAllPub()
        nomes_publicadores = ["não possui"] + [pub['nome'] for pub in publicadores]
        
        # Criar campos para cada semana
        for idx, semana in enumerate(partesPorSemana):
            semana_num = idx + 1
            participantes = semana.get('Participantes', {})
            
            # Frame para cada semana
            semana_frame = ttk.LabelFrame(
                scrollable_frame,
                text=f"Semana {semana_num}: {semana.get('semana', 'N/A')}",
                padding=15
            )
            semana_frame.pack(fill=X, pady=10, padx=10)
            
            # Grid para campos
            semana_frame.grid_columnconfigure(1, weight=1)
            
            campos_semana = {}
            row = 0
            
            # Mapeamento de partes
            partes_mapping = [
                ('Presidente', 'Presidente'),
                ('Oração Inicial', 'OracaoInicial'),
                ('Tesouro', 'Tesouro'),
                ('Joias Espirituais', 'Joias'),
                ('Leitura da Bíblia', 'Leitura'),
                ('Escola - Iniciando Conversa', 'IniciandoConversa'),
                ('Escola - Cultivando Interesse', 'CultivandoInteresse'),
                ('Escola - Estudo/Discurso', 'EstudoDiscurso'),
                ('Escola - Parte 4', 'Escola4'),
                ('NVC - Parte 1', 'Nvc1'),
                ('NVC - Parte 2', 'Nvc2'),
                ('Estudo de Congregação', 'Estudo'),
                ('Oração Final', 'OracaoFinal')
            ]
            
            for parte_nome, parte_key in partes_mapping:
                ttk.Label(
                    semana_frame,
                    text=f"{parte_nome}:",
                    font=("Helvetica", 10),
                    bootstyle="secondary"
                ).grid(row=row, column=0, padx=(0, 10), pady=5, sticky="w")
                
                # Campo de entrada com autocomplete
                entry_var = tk.StringVar(value=participantes.get(parte_key, "não possui"))
                entry = ttk.Entry(
                    semana_frame,
                    textvariable=entry_var,
                    width=40,
                    bootstyle="primary"
                )
                entry.grid(row=row, column=1, sticky="ew", pady=5)
                
                # Popup flutuante para autocomplete
                popup = tk.Toplevel(semana_frame)
                popup.withdraw()
                popup.overrideredirect(True)
                listbox = tk.Listbox(popup, height=5)
                listbox.pack(fill=tk.BOTH, expand=True)

                def criar_update_listbox(entry_widget, listbox_widget, popup_widget, nomes):
                    def update_listbox(event):
                        texto_completo = entry_widget.get()
                        if '/' in texto_completo:
                            texto = texto_completo.split('/')[-1].strip().lower()
                        else:
                            texto = texto_completo.strip().lower()
                        if texto:
                            valores_filtrados = [n for n in nomes if texto in n.lower()]
                            listbox_widget.delete(0, tk.END)
                            for valor in valores_filtrados[:10]:
                                listbox_widget.insert(tk.END, valor)
                            if valores_filtrados:
                                x = entry_widget.winfo_rootx()
                                y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
                                w = entry_widget.winfo_width()
                                h = min(len(valores_filtrados), 5) * 18 + 4
                                popup_widget.geometry(f"{w}x{h}+{x}+{y}")
                                popup_widget.deiconify()
                                popup_widget.lift()
                            else:
                                popup_widget.withdraw()
                        else:
                            popup_widget.withdraw()
                    return update_listbox

                def on_listbox_select(event, entry_widget, listbox_widget, popup_widget):
                    selection = listbox_widget.curselection()
                    if selection:
                        selected_name = listbox_widget.get(selection[0])
                        current_text = entry_widget.get()
                        if '/' in current_text:
                            antes_barra = '/'.join(current_text.split('/')[:-1]).rstrip()
                            entry_widget.delete(0, tk.END)
                            entry_widget.insert(0, antes_barra + ' / ' + selected_name)
                        else:
                            entry_widget.delete(0, tk.END)
                            entry_widget.insert(0, selected_name)
                        popup_widget.withdraw()
                        entry_widget.focus_set()

                entry.bind('<KeyRelease>', criar_update_listbox(entry, listbox, popup, nomes_publicadores))
                entry.bind('<FocusOut>', lambda e, pw=popup: pw.after(150, pw.withdraw))
                listbox.bind('<<ListboxSelect>>', lambda e, ew=entry, lw=listbox, pw=popup: on_listbox_select(e, ew, lw, pw))
                listbox.bind('<Double-Button-1>', lambda e, ew=entry, lw=listbox, pw=popup: on_listbox_select(e, ew, lw, pw))
                
                campos_semana[parte_key] = entry_var
                row += 1
            
            campos_por_semana[idx] = campos_semana
        
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Frame para botões
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=X, pady=(20, 0))
        
        def salvar_alteracoes():
            # Atualizar participantes com os valores dos campos
            for idx, semana in enumerate(partesPorSemana):
                campos_semana = campos_por_semana[idx]
                participantes = {}
                
                for parte_key, entry_var in campos_semana.items():
                    participantes[parte_key] = entry_var.get().strip()
                
                semana['Participantes'] = participantes
                
                # Salvar no banco de dados
                ano = datetime.datetime.now().year
                dados_reuniao = {
                    'ano': ano,
                    'semana': semana['semana'],
                    'data_reuniao': datetime.datetime.now().isoformat(),
                    'presidente': participantes.get('Presidente', 'não possui'),
                    'oracao_inicial': participantes.get('OracaoInicial', 'não possui'),
                    'tesouro': participantes.get('Tesouro', 'não possui'),
                    'joias_espirituais': participantes.get('Joias', 'não possui'),
                    'leitura_biblia': participantes.get('Leitura', 'não possui'),
                    'escola': {
                        'primeira_parte': participantes.get('IniciandoConversa', 'não possui'),
                        'segunda_parte': participantes.get('CultivandoInteresse', 'não possui'),
                        'terceira_parte': participantes.get('EstudoDiscurso', 'não possui'),
                        'quarta_parte': participantes.get('Escola4', 'não possui')
                    },
                    'nossa_vida_crista': {
                        'primeira_parte': participantes.get('Nvc1', 'não possui'),
                        'segunda_parte': participantes.get('Nvc2', 'não possui')
                    },
                    'estudo_congregacao': participantes.get('Estudo', 'não possui'),
                    'oracao_final': participantes.get('OracaoFinal', participantes.get('Presidente', 'não possui'))
                }
                
                resultado = db_ops.salvar_reuniao(dados_reuniao)
                if resultado['success']:
                    print(f"Reunião da semana {semana['semana']} salva com sucesso")
                else:
                    print(f"Erro ao salvar reunião da semana {semana['semana']}: {resultado['message']}")
            
            resultado_salvar[0] = True
            modal.destroy()
            temp_root.destroy()
        
        def cancelar():
            resultado_salvar[0] = False
            modal.destroy()
            temp_root.destroy()
        
        ttk.Button(
            button_frame,
            text="Salvar e Continuar",
            command=salvar_alteracoes,
            bootstyle="success",
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=cancelar,
            bootstyle="secondary",
            width=20
        ).pack(side=LEFT)
        
        # Centralizar janela
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (900 // 2)
        y = (modal.winfo_screenheight() // 2) - (700 // 2)
        modal.geometry(f"900x700+{x}+{y}")
        
        # Aguardar fechamento da janela
        modal.wait_window()
        
        return resultado_salvar[0]
                
    def criarDocumentoApartirDoObjeto(partesPorSemana , preencherPubs , nomeEv , idiomaEv):
        print("Criando Documento")
        idioma = idiomaEv
        filename = nomeEv
        # Seleciona o Template de acordo com Idioma escolhido
        if idioma == "pt" :
                template_filename = "Templates/Template_PT.docx"
        
        # Nome do arquivo para gravaçao do documento
        nomeArquivo = filename + ".docx"


        # Lendo o modelo do Word Selecionado
        doc = docx.Document(template_filename) 

        # Variavel que susbtitui no Word
        pagina = 'p'

        for semana in partesPorSemana:
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                        if str(pagina) + "01" in run.text:
                                        run.text = run.text.replace(str(pagina) + "01", semana['semana']) 
                        if str(pagina) + "02" in run.text:
                                        run.text = run.text.replace(str(pagina) + "02", semana['capituloVersiculo'])
                        if str(pagina) + "03" in run.text:
                                        run.text = run.text.replace(str(pagina) + "03", semana['canticoInicial'])
                        if str(pagina) + "06" in run.text:
                                        run.text = run.text.replace(str(pagina) + "06", semana['tesouro'])
                        if str(pagina) + "08" in run.text:
                                        run.text = run.text.replace(str(pagina) + "08", semana['perguntaJoias'])
                        if str(pagina) + "12" in run.text:
                                        run.text = run.text.replace(str(pagina) + "12", semana['leituraSemana'] + ")")
                        if str(pagina) + "13" in run.text:
                                        run.text = run.text.replace(str(pagina) + "13", semana['iniciandoConversa'])
                        if str(pagina) + "14" in run.text:
                                        run.text = run.text.replace(str(pagina) + "14", semana['cultivandoInteresse'])
                        if str(pagina) + "15" in run.text:
                                        run.text = run.text.replace(str(pagina) + "15", semana['estudoDiscurso'])
                        if str(pagina) + "16" in run.text:
                                        run.text = run.text.replace(str(pagina) + "16", semana['escola4'])
                        if str(pagina) + "18" in run.text:
                                        run.text = run.text.replace(str(pagina) + "18", semana['canticoMeio'])
                        if str(pagina) + "19" in run.text:
                                        run.text = run.text.replace(str(pagina) + "19", semana['nvcP1'])
                        if str(pagina) + "20" in run.text:
                                        run.text = run.text.replace(str(pagina) + "20", semana['nvcP2'])
                        if str(pagina) + "21" in run.text:
                                        run.text = run.text.replace(str(pagina) + "21", semana['estudo'])
                        if str(pagina) + "23" in run.text:
                                        run.text = run.text.replace(str(pagina) + "23", semana['canticoFinal'])
                        if preencherPubs:   
                            if str(pagina) + "34" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "34", semana['Participantes']['Presidente'])                     
                            if str(pagina) + "35" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "35", semana['Participantes']['OracaoInicial'])         
                            if str(pagina) + "36" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "36", semana['Participantes']['Tesouro'])
                            if str(pagina) + "37" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "37", semana['Participantes']['Joias'])
                            if str(pagina) + "38" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "38", semana['Participantes']['Leitura'])
                            if str(pagina) + "39" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "39", semana['Participantes']['IniciandoConversa'])
                            if str(pagina) + "40" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "40", semana['Participantes']['CultivandoInteresse'])                        
                            if str(pagina) + "41" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "41", semana['Participantes']['EstudoDiscurso'])                        
                            if str(pagina) + "42" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "42", semana['Participantes']['Escola4'])                        
                            if str(pagina) + "43" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "43", semana['Participantes']['Nvc1'])                        
                            if str(pagina) + "44" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "44", semana['Participantes']['Nvc2'])                        
                            if str(pagina) + "45" in run.text:
                                                    run.text = run.text.replace(str(pagina) + "45", semana['Participantes']['Estudo']) 

            pagina = chr(ord(pagina) + 1)
            
        doc.save("documentosCriados/" + nomeArquivo)
        # Exibindo mensagem de sucesso
        print("Programaçao Criada com Sucesso na pasta DocumentosCriados com Nome:", str(nomeArquivo))
        
        
        subprocess.run(["start", "documentosCriados/" + nomeArquivo], shell=True)                   
    
    
    def atualizarHistoricoPublicadores(partesPorSemana):
        for semana in partesPorSemana:
            participantes = semana['Participantes']
            
            # Primeiro salva a reunião completa
            ano = datetime.datetime.now().year
            dados_reuniao = {
                'ano': ano,
                'semana': semana['semana'],
                'data_reuniao': datetime.datetime.now().isoformat(),
                'presidente': participantes['Presidente'],
                'oracao_inicial': participantes['OracaoInicial'],
                'tesouro': participantes['Tesouro'],
                'joias_espirituais': participantes['Joias'],
                'leitura_biblia': participantes['Leitura'],
                'escola': {
                    'primeira_parte': participantes['IniciandoConversa'],
                    'segunda_parte': participantes['CultivandoInteresse'],
                    'terceira_parte': participantes['EstudoDiscurso'],
                    'quarta_parte': participantes['Escola4']
                },
                'nossa_vida_crista': {
                    'primeira_parte': participantes['Nvc1'],
                    'segunda_parte': participantes['Nvc2']
                },
                'estudo_congregacao': participantes['Estudo'],
                'oracao_final': participantes['Presidente'] 
            }
            
            # Salva a reunião no banco
            # Nota: salvar_reuniao() já atualiza o histórico dos publicadores automaticamente
            # via _atualizar_historico_publicadores(), então não é necessário chamar update_parte() novamente
            resultado = db_ops.salvar_reuniao(dados_reuniao)
            if resultado['success']:
                print(f"Reunião da semana {semana['semana']} salva com sucesso")
            else:
                print(f"Erro ao salvar reunião da semana {semana['semana']}: {resultado['message']}")
        
        print("Historico Atualizado com Sucesso")    