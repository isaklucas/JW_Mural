import requests
from bs4 import BeautifulSoup
import docx
import os
import subprocess
import re






class MyApp:
        def run(urlEv, nomeEv, idiomaEv):
                
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
                                        tesouro = tesouroTemp
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
                                        # Itere sobre as tags h3.
                                        for tag_h3 in tags_h3:
                                        # Verifique se a tag h3 tem a classe dc-icon--music.
                                                if "dc-icon--music" in tag_h3.get("class", []):
                                                        # Incrementa o contador ao encontrar uma tag dc-icon--music.
                                                        contador_dc_icon_music += 1
                                                        
                                                        # Verifica se já encontramos a segunda tag dc-icon--music.
                                                        if contador_dc_icon_music == 2:
                                                                # Encontramos a segunda tag dc-icon--music, agora gravamos o conteúdo das próximas três tags.
                                                                index_tag_atual = tags_h3.index(tag_h3)
                                                                proximas_tags = tags_h3[index_tag_atual + 1:index_tag_atual + 4]  # Pega as próximas três tags.
                                                                
                                                                # Grava o conteúdo nas variáveis correspondentes.
                                                                nvcP1 = proximas_tags[0].get_text() if len(proximas_tags) > 0 else "não possui"
                                                                nvcP2 = proximas_tags[1].get_text() if len(proximas_tags) > 1 else "não possui"
                                                                estudo = proximas_tags[2].get_text() if len(proximas_tags) > 2 else "não possui"
                                                                
                                                                break
                                                                                
                                        
                                        ## Ajuste caso nao aja parte 2
                                        if 'Estudo bíblico' in nvcP2:
                                                estudo = nvcP2 
                                                nvcP2 = "não possue esta Parte"
                                        
                                        print('nvcP1 : ' + nvcP1)
                                        print('nvcP2 : ' + nvcP2)
                                        print('estudo  : ' + estudo)
                                        
                                        canticoFinalTemp = tags_h3[-3].get_text().split('|')
                                        canticoFinal = canticoFinalTemp[1]
                                        print('Cantico Final : ' + canticoFinal)
                                                
 
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
                                                                


                                       
                                                                
                               
                                
                                pagina = chr(ord(pagina) + 1)

                
                if not os.path.exists("documentosCriados"):
                        os.makedirs("documentosCriados")

                doc.save("documentosCriados/" + nomeArquivo)
                # Exibindo mensagem de sucesso
                print("Programaçao Criada com Sucesso na pasta DocumentosCriados com Nome:", str(nomeArquivo))
                
                
                subprocess.run(["start", "documentosCriados/" + nomeArquivo], shell=True)
                


