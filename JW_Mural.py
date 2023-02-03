import requests
from bs4 import BeautifulSoup
import docx
import aspose.words as aw

base_url = "https://wol.jw.org/pt/wol/meetings/r5/lp-t/2023/"
template_filename = "Template.docx"
filename_template = "Vd_Crista.docx"

# Lendo o modelo do Word
template = docx.Document(template_filename)

doc = docx.Document(template_filename) 

pagina = 'p'
for i in range(6, 11):
    url = base_url + str(i)
    
    print("Criando semana: " + str(i) )

    
    
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
       
        semana = soup.find(id="p1").get_text()
        livro = soup.find(id="p2").get_text()
        canticoInicial = soup.find(id="p3").get_text()
        tesouro = soup.find(id="p6").get_text()
        perguntaJoias = soup.find(id="p8").get_text()
        leituraSemana = soup.find(id="p12").get_text()
        canticoMeio = soup.find(id="p18").get_text()
        nvcP1temp = soup.find(id="p19").get_text().split('(')
        nvcP2temp = soup.find(id="p20").get_text().split('(')
        estudo = soup.find(id="p21").get_text()
        canticoFinal = soup.find(id="p23")

        nvcP1 = nvcP1temp[0]
        nvcP2 = nvcP2temp[0]
        

        if canticoFinal != None and nvcP2 != "\nSua resposta\n\n":
            canticoFinal = soup.find(id="p23").get_text()

            # Criando uma cópia do modelo
            
            
            # Localizando os campos de substituição no modelo
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    if str(pagina) + "01" in run.text:
                            run.text = run.text.replace(str(pagina) + "01", semana) 
                    if str(pagina) + "02" in run.text:
                            run.text = run.text.replace(str(pagina) + "02", livro)
                    if str(pagina) + "03" in run.text:
                            run.text = run.text.replace(str(pagina) + "03", canticoInicial)
                    if str(pagina) + "06" in run.text:
                            run.text = run.text.replace(str(pagina) + "06", tesouro)
                    if str(pagina) + "08" in run.text:
                            run.text = run.text.replace(str(pagina) + "08", perguntaJoias)
                    if str(pagina) + "12" in run.text:
                            run.text = run.text.replace(str(pagina) + "12", leituraSemana)
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


        if canticoFinal == None :
            estudo = soup.find(id="p20").get_text()
            canticoFinal = soup.find(id="p22").get_text()

            
            
            # Localizando os campos de substituição no modelo
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    if str(pagina) + "01" in run.text:
                            run.text = run.text.replace(str(pagina) + "01", semana) 
                    if str(pagina) + "02" in run.text:
                            run.text = run.text.replace(str(pagina) + "02", livro)
                    if str(pagina) + "03" in run.text:
                            run.text = run.text.replace(str(pagina) + "03", canticoInicial)
                    if str(pagina) + "06" in run.text:
                            run.text = run.text.replace(str(pagina) + "06", tesouro)
                    if str(pagina) + "08" in run.text:
                            run.text = run.text.replace(str(pagina) + "08", perguntaJoias)
                    if str(pagina) + "12" in run.text:
                            run.text = run.text.replace(str(pagina) + "12" , leituraSemana)
                    if str(pagina) + "18" in run.text:
                            run.text = run.text.replace(str(pagina) + "18" , canticoMeio)
                    if str(pagina) + "19" in run.text:
                            run.text = run.text.replace(str(pagina) + "19" , nvcP1)
                    if str(pagina) + "20" in run.text:
                            run.text = run.text.replace(str(pagina) + "20" , "Nao possue essa parte")
                    if str(pagina) + "21" in run.text:
                            run.text = run.text.replace(str(pagina) + "21" , estudo)
                    if str(pagina) + "23" in run.text:
                            run.text = run.text.replace(str(pagina) + "23" , canticoFinal)
  
        
        if nvcP2 == "\nSua resposta\n\n":

            nvcP2 = soup.find(id="p21").get_text()
            estudo = soup.find(id="p22").get_text()
            canticoFinal = soup.find(id="p24").get_text()

           
            
            # Localizando os campos de substituição no modelo
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    if str(pagina) + "01" in run.text:
                            run.text = run.text.replace(str(pagina) + "01", semana) 
                    if str(pagina) + "02" in run.text:
                            run.text = run.text.replace(str(pagina) + "02", livro)
                    if str(pagina) + "03" in run.text:
                            run.text = run.text.replace(str(pagina) + "03", canticoInicial)
                    if str(pagina) + "06" in run.text:
                            run.text = run.text.replace(str(pagina) + "06", tesouro)
                    if str(pagina) + "08" in run.text:
                            run.text = run.text.replace(str(pagina) + "08", perguntaJoias)
                    if str(pagina) + "12" in run.text:
                            run.text = run.text.replace(str(pagina) + "12" , leituraSemana)
                    if str(pagina) + "18" in run.text:
                            run.text = run.text.replace(str(pagina) + "18" , canticoMeio)
                    if str(pagina) + "19" in run.text:
                            run.text = run.text.replace(str(pagina) + "19" , nvcP1)
                    if str(pagina) + "20" in run.text:
                            run.text = run.text.replace(str(pagina) + "20" , "Nao possue essa parte")
                    if str(pagina) + "21" in run.text:
                            run.text = run.text.replace(str(pagina) + "21" , estudo)
                    if str(pagina) + "23" in run.text:
                            run.text = run.text.replace(str(pagina) + "23" , canticoFinal)          
        pagina = chr(ord(pagina) + 1)

    
    
   
doc.save(filename_template)
# Exibindo mensagem de sucesso
print("Texto gravado com sucesso em", str(filename_template))  