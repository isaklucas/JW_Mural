import requests
from bs4 import BeautifulSoup
import docx
import os
import subprocess
import re
import connetion_DB
import tkinter as tk
from tkinter import simpledialog
from enum import Enum
import datetime






class MyApp:
        def run(urlEv, nomeEv, idiomaEv , utilizarBase):
                nomes_publicadores = []
                # busco no banco de dados Crio uma Lista com todos os nomes_publicadores de publicadores
                if utilizarBase:
                        publicadores = connetion_DB.getAllPub()
                        nomes_publicadores = [pub['nome'] for pub in publicadores]
                        print(nomes_publicadores)
   
                # Variaveis digitadas pelo Usuario
                idioma = idiomaEv
                filename = nomeEv
                urlEnviada = urlEv
                
                # Pega a Semana que está na URL
                urlSplit = urlEnviada.split("/")
                semanas = urlSplit[len(urlSplit) - 1]

                # Variaveis utilizadas para os For e montar a Url novamente
                tamanhoURL = len(urlSplit)
                x = int(semanas)
                y = x+5
                base_url = ''

                for v in range(0, tamanhoURL-1) :
                        if v == 0 :
                                base_url = base_url  + urlSplit[v]
                        else : base_url = base_url + "/" + urlSplit[v]


                # Seleciona o Template de acordo com Idioma escolhido
                if idioma == "pt" :
                        template_filename = "Templates/Template_PT.docx"
                
                # Nome do arquivo para gravaçao do documento
                nomeArquivo = filename + ".docx"


                # Lendo o modelo do Word Selecionado
                doc = docx.Document(template_filename) 

                # Variavel que susbtitui no Word
                pagina = 'p'
                
                while x < y:

                        url = base_url + "/" + str(x)
                        print("Criando semana: " + str(x))
                
                        x = x + 1
                        # Fazendo a solicitação HTTP
                        response = requests.get(url)

                        # Verificando se a solicitação foi bem-sucedida
                        if response.status_code == 200:
                        
                                # Analisando o HTML com BeautifulSoup
                                soup = BeautifulSoup(response.text, "html.parser")
                                
                                # Procurando a div com a classe "todayitem"
                                pag = soup.find("div", class_="todayItem")
                                
                                # Extraindo o texto da div
                                text = pag.get_text()  
                        
                                verificaSemana = soup.find(id="p1")
                                
                                if verificaSemana != None:
                                        ## Pega Semana
                                        semana = soup.find(id="p1").get_text() 
                                        print('semana: ' + semana)
                                        
                                        ## Pega Capitulos
                                        capituloVersiculo = soup.find(id="p2").get_text()
                                        print('capitulo e Versiculo: ' + capituloVersiculo)
                                        
                                        ## Pega cantico Inicial
                                        canticoInicialTemp = soup.find(id="p3").get_text().split('|')
                                        canticoInicial = canticoInicialTemp[0]
                                        print('Cantico Inicial: ' + canticoInicial)
                                        
                                        ## Pega Tesouro
                                        tesouroTemp = soup.find(id="p5").get_text()
                                        tesouro = tesouroTemp.split('1.')[1]
                                        print('1. Tesouro : ' + tesouro)
                                        
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
                                                print('Pergunta das joias: ' +perguntaJoias)
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
                                                
                                                print('Leitura da Semana : ' + leituraSemana)
                                        else:
                                                print(f"Div após {topico2} não encontrada na página.")
                                        
                                        
                                        ## Cantico do Meio
                                        Canticos = soup.find_all("h3", class_="dc-icon--music")
                                        canticoMeio = Canticos[1].get_text()
                                        print('Cantico Meio : ' + canticoMeio)
                                        
                                        
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
                                                
                                        
                                                
                                        
                                        print('iniciando Conversa : ' + iniciandoConversa)
                                        print('cultivando Interesse : ' + cultivandoInteresse)
                                        print('estudo ou Discurso  : ' + estudoDiscurso)
                                        print('Escola parte 4 : ' + escola4)
                                        
                                        print('nvcP1 : ' + nvcP1)
                                        print('nvcP2 : ' + nvcP2)
                                        
                                        
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
                                                print('estudo  : ' + estudo)
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
                                        
             
                                        print('Cantico Final : ' + canticoFinal)
                                                                
                                        def solicitar_nome_publicador(parte, nomes_publicadores):
                                                if utilizarBase is False:
                                                        return "nome"
                                                
                                                
                                                root = tk.Tk()
                                                root.withdraw()  # Esconde a janela principal
                                                
                                                

                                                def on_submit():
                                                                nonlocal nome
                                                                nome = entry.get()
                                                                root.destroy()

                                                def update_listbox(*args):
                                                                                search_term = entry.get().lower()
                                                                                listbox.delete(0, tk.END)
                                                                                if '/' in search_term:
                                                                                                                last_term = search_term.split('/')[-1].strip()
                                                                                                                for nome in nomes_publicadores:
                                                                                                                                                if last_term in nome.lower():
                                                                                                                                                                                listbox.insert(tk.END, nome)
                                                                                else:
                                                                                                                for nome in nomes_publicadores:
                                                                                                                                                if search_term in nome.lower():
                                                                                                                                                                                listbox.insert(tk.END, nome)

                                                def on_listbox_select(event):
                                                                                selection = event.widget.curselection()
                                                                                if selection:
                                                                                                                index = selection[0]
                                                                                                                selected_name = event.widget.get(index)
                                                                                                                current_text = entry.get()
                                                                                                                if '/' in current_text:
                                                                                                                                                parts = current_text.split('/')
                                                                                                                                                entry.delete(0, tk.END)
                                                                                                                                                entry.insert(0, parts[0] + ' / ' + selected_name)
                                                                                                                else:
                                                                                                                                                entry.delete(0, tk.END)
                                                                                                                                                entry.insert(0, selected_name)

                                                
                                                top = tk.Toplevel(root)
                                                top.title(f"Semana: {semana} - {parte}")
                                                top.geometry("300x300")
                                                #sempre aparecer no meio do desktop
                                                top.update_idletasks()
                                                width = top.winfo_width()
                                                height = top.winfo_height()
                                                x = (top.winfo_screenwidth() // 2) - (width // 2)
                                                y = (top.winfo_screenheight() // 2) - (height // 2)
                                                top.geometry('{}x{}+{}+{}'.format(width, height, x, y))
                                                
                                                
                                                

                                                label = tk.Label(top, text=f"publicador para a parte {parte}:")
                                                label.pack()

                                                entry = tk.Entry(top)
                                                entry.pack()
                                                entry.focus_set()
                                                entry.bind("<KeyRelease>", update_listbox)

                                                listbox = tk.Listbox(top)
                                                listbox.pack()
                                                listbox.bind("<<ListboxSelect>>", on_listbox_select)

                                                for nome in nomes_publicadores:
                                                                                listbox.insert(tk.END, nome)

                                                submit_button = tk.Button(top, text="OK", command=on_submit)
                                                submit_button.pack()

                                                nome = None
                                                root.wait_window(top)
                                                return nome
                                                
                                        
                                        nome_presidente = solicitar_nome_publicador("Presidente" , nomes_publicadores)
                                        nome_oracaoInicial = solicitar_nome_publicador("Oraçao Inicial" , nomes_publicadores)
                                        nome_tesouro = solicitar_nome_publicador("Tesouro" , nomes_publicadores)
                                        nome_joias = solicitar_nome_publicador("Joias" , nomes_publicadores)
                                        nome_leitura = solicitar_nome_publicador("Leitura" , nomes_publicadores)
                                        nome_iniciandoConversa = solicitar_nome_publicador("Iniciando Conversa" , nomes_publicadores)
                                        nome_cultivandoInteresse = solicitar_nome_publicador("Cultivando Interesse" , nomes_publicadores)
                                        
                                        if estudoDiscurso != "não possui":
                                                nome_estudoDiscurso = solicitar_nome_publicador("Estudo ou Discurso" , nomes_publicadores)
                                        else: 
                                                nome_estudoDiscurso = "não possui"
                                       
                                        if escola4 != "não possui":
                                                nome_escola4 = solicitar_nome_publicador("Escola Parte 4" , nomes_publicadores)
                                        else:
                                                nome_escola4 = "não possui"
                                        
                                        nome_nvc1 = solicitar_nome_publicador("NVC Parte 1" , nomes_publicadores)
                                        
                                        if nvcP2 != "não possue esta Parte":
                                                nome_nvc2 = solicitar_nome_publicador("NVC Parte 2" , nomes_publicadores)
                                        else:
                                                nome_nvc2 = "não possui"
                                        
                                        nome_estudo = solicitar_nome_publicador("Estudo e leitor" , nomes_publicadores)
                                                                   
                                       
                                        for paragraph in doc.paragraphs:
                                                for run in paragraph.runs:
                                                        if str(pagina) + "01" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "01", semana) 
                                                        if str(pagina) + "02" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "02", capituloVersiculo)
                                                        if str(pagina) + "03" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "03", canticoInicial)
                                                        if str(pagina) + "06" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "06", tesouro)
                                                        if str(pagina) + "08" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "08", perguntaJoias)
                                                        if str(pagina) + "12" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "12", leituraSemana + ")")
                                                        if str(pagina) + "13" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "13", iniciandoConversa)
                                                        if str(pagina) + "14" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "14", cultivandoInteresse)
                                                        if str(pagina) + "15" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "15", estudoDiscurso)
                                                        if str(pagina) + "16" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "16", escola4)
                                                        if str(pagina) + "18" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "18", canticoMeio)
                                                        if str(pagina) + "19" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "19", nvcP1)
                                                        if str(pagina) + "20" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "20", nvcP2)
                                                        if str(pagina) + "21" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "21", estudo)
                                                        if str(pagina) + "23" in run.text:
                                                                        run.text = run.text.replace(str(pagina) + "23", canticoFinal)   
                                                        if str(pagina) + "34" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "34", nome_presidente)                     
                                                        if str(pagina) + "35" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "35", nome_oracaoInicial)         
                                                        if str(pagina) + "36" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "36", nome_tesouro)
                                                        if str(pagina) + "37" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "37", nome_joias)
                                                        if str(pagina) + "38" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "38", nome_leitura)
                                                        if str(pagina) + "39" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "39", nome_iniciandoConversa)
                                                        if str(pagina) + "40" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "40", nome_cultivandoInteresse)                        
                                                        if str(pagina) + "41" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "41", nome_estudoDiscurso)                        
                                                        if str(pagina) + "42" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "42", nome_escola4)                        
                                                        if str(pagina) + "43" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "43", nome_nvc1)                        
                                                        if str(pagina) + "44" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "44", nome_nvc2)                        
                                                        if str(pagina) + "45" in run.text:
                                                                                run.text = run.text.replace(str(pagina) + "45", nome_estudo)                        
                                                     
                                        if utilizarBase:
                                                def get_parte_nome(index):
                                                        partes = ["Presidente", "Oraçao Inicial", "Tesouro", "Joias", "Leitura", "Iniciando Conversa", "Cultivando Interesse", "Estudo ou Discurso", "Escola Parte 4", "NVC Parte 1", "NVC Parte 2", "Dirigente ou leitor"]
                                                        return partes[index]
                                                
                                                participantes_na_semana = [nome_presidente, nome_oracaoInicial, nome_tesouro, nome_joias, nome_leitura, nome_iniciandoConversa, nome_cultivandoInteresse, nome_estudoDiscurso, nome_escola4, nome_nvc1, nome_nvc2, nome_estudo]
                                                for index, nome in enumerate(participantes_na_semana):
                                                        if nome != "não possui":
                                                                # nome contem / ?
                                                                if '/' in nome:
                                                                        partes = nome.split('/')
                                                                        for parte in partes:
                                                                                if parte.strip() not in nomes_publicadores:
                                                                                        print(f"O nome '{parte.strip()}' não foi encontrado na lista de publicadores. Adicionando a Base")
                                                                                        connetion_DB.post(parte.strip(), False)
                                                                        
                                                                        partes = [parte.strip() for parte in partes]
                                                                        data_participacao = f"{semana} de {datetime.datetime.now().year}"
                                                                        for parte in partes:
                                                                                connetion_DB.update_parte(parte, get_parte_nome(index), data_participacao)
                                                                        return
                                                                
                                                                elif nome not in nomes_publicadores:
                                                                        print(f"O nome '{nome}' não foi encontrado na lista de publicadores. Adicionando a Base")
                                                                        connetion_DB.post(nome, False)
                                                                        
                                                                ano = datetime.datetime.now().year
                                                                data_participacao = f"{semana} de {ano}"
                                                                parte = get_parte_nome(index)
                                                                connetion_DB.update_parte(nome, parte, data_participacao)        
                                           
                                                     
                                                     
                                                                                
                                pagina = chr(ord(pagina) + 1)

                doc.save("documentosCriados/" + nomeArquivo)
                # Exibindo mensagem de sucesso
                print("Programaçao Criada com Sucesso na pasta DocumentosCriados com Nome:", str(nomeArquivo))
                
                
                subprocess.run(["start", "documentosCriados/" + nomeArquivo], shell=True)                                                      
                                           