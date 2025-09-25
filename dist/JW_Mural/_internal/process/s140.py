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
from docx.enum.text import WD_ALIGN_PARAGRAPH

class s140:
    def gerar_s140(urlEv, nomeEv, idiomaEv , preencherPubs, qntdSemanas):
        ## Busca Soup das Semanas
       
        listaSoupSemanas = s140.buscarSoupDasSemnas(urlEv, qntdSemanas)
       
        partesPorSemana = s140.extrair_partes(listaSoupSemanas)
       
        if preencherPubs:
            s140.solicitarNomePublicadorPartes(partesPorSemana)
            
        s140.criarDocumentoApartirDoObjeto(partesPorSemana , preencherPubs , nomeEv , idiomaEv)
        
        if preencherPubs:
            s140.atualizarHistoricoPublicadores(partesPorSemana)
           
               
       
            
        
        
    def extrair_partes(listaSoupSemanas):
        listaPartesPorSemana = []
        
        for soup in listaSoupSemanas:
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
                    
   
    def buscarSoupDasSemnas(urlEv, qntdSemanas):
        urlEnviada = urlEv
        
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
                
        listaSoupSemanas = []
        
        for i in range(x, y):
            url = base_url + "/" + str(i)
            print("Iniciando o webscrapper: " + url )
            soupSemana = webscrapper.webscrapper.executar(url)
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
                'Estudo': nome_estudo
            }
            
            semana['Participantes'] = participantes
            
        return partesPorSemana
                                        

                
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
                'oracao_final': 'não possui'  # Campo obrigatório, mas não preenchido no S-140
            }
            
            # Salva a reunião no banco
            resultado = db_ops.salvar_reuniao(dados_reuniao)
            if resultado['success']:
                print(f"Reunião da semana {semana['semana']} salva com sucesso")
            else:
                print(f"Erro ao salvar reunião da semana {semana['semana']}: {resultado['message']}")
            
            # Atualiza histórico individual dos participantes
            if participantes['Presidente'] != "não possui":
                db_ops.update_parte(participantes['Presidente'], "Presidente", semana['semana'])
            if participantes['OracaoInicial'] != "não possui":
                db_ops.update_parte(participantes['OracaoInicial'], "Oração Inicial", semana['semana'])
            if participantes['Tesouro'] != "não possui":
                db_ops.update_parte(participantes['Tesouro'], "Tesouro", semana['semana'])
            if participantes['Joias'] != "não possui":
                db_ops.update_parte(participantes['Joias'], "Joias", semana['semana'])
            if participantes['Leitura'] != "não possui":
                db_ops.update_parte(participantes['Leitura'], "Leitura", semana['semana'])
            if participantes['IniciandoConversa'] != "não possui":
                db_ops.update_parte(participantes['IniciandoConversa'], "Iniciando Conversa", semana['semana'])
            if participantes['CultivandoInteresse'] != "não possui":
                db_ops.update_parte(participantes['CultivandoInteresse'], "Cultivando Interesse", semana['semana'])
            if participantes['EstudoDiscurso'] != "não possui":
                db_ops.update_parte(participantes['EstudoDiscurso'], "Estudo/Discurso", semana['semana'])
            if participantes['Escola4'] != "não possui":
                db_ops.update_parte(participantes['Escola4'], "Escola 4ª Parte", semana['semana'])
            if participantes['Nvc1'] != "não possui":
                db_ops.update_parte(participantes['Nvc1'], "Nossa Vida Cristã 1ª Parte", semana['semana'])
            if participantes['Nvc2'] != "não possui":
                db_ops.update_parte(participantes['Nvc2'], "Nossa Vida Cristã 2ª Parte", semana['semana'])
            if participantes['Estudo'] != "não possui":
                db_ops.update_parte(participantes['Estudo'], "Estudo de Congregação", semana['semana'])
        
        print("Historico Atualizado com Sucesso")    