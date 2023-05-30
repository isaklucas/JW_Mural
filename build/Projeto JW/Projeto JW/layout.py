import tkinter as tk
from tkinter import *
import JW_Mural
import connetion_DB
import webbrowser
import time




class LoadingScreen():
    def __init__(self):
        super().__init__()
        self.title("Loading")
        self.geometry("300x300")
        self.config(bg='black')
        self.loading_label = tk.Label(self, text="Loading...", bg='white')
        self.loading_label.pack(side="top", fill="both", expand=True)
        self.loading_image = tk.PhotoImage(file="loading.gif")
        self.loading_image_label = tk.Label(self, image=self.loading_image, bg='white')
        self.loading_image_label.pack(side="bottom", fill="both", expand=True)
        
    def update_loading_text(self, text):
        self.loading_label.config(text=text)
        self.update()
    
    
def publicadores():
    def salvar_publicador():
        nome = nome_entry.get()
        batizado = batizado_var.get()
        connetion_DB.post(nome , batizado)
        nome_entry.delete(0, END)
        batizado_var.set(False)
        
    
       
    publicadores_criar = tk.Toplevel(janela)
    publicadores_criar.title("publicadores_criar")
    publicadores_criar.geometry("300x300")
    
    label = tk.Label(publicadores_criar, text="publicadores_criar")
    label.grid(row=0, column=0, sticky="W")
    
    nome_label = tk.Label(publicadores_criar, text="Nome:")
    nome_entry = tk.Entry(publicadores_criar)

    batizado_label = tk.Label(publicadores_criar, text="Batizado:")
    batizado_var = tk.BooleanVar()
    batizado_checkbox = tk.Checkbutton(publicadores_criar, variable=batizado_var)



    nome_label.grid(row=1, column=0, sticky="W")
    nome_entry.grid(row=1, column=1)

    batizado_label.grid(row=2, column=0, sticky="W")
    batizado_checkbox.grid(row=2, column=1)

    salvar_button = tk.Button(publicadores_criar, text="Salvar", command=salvar_publicador)
    salvar_button.grid(row=4, column=1, pady=10)
    
    listbox = Listbox(publicadores_criar)
    listbox.grid(row=5, column=0,  columnspan=3, sticky="W")
    
    results = connetion_DB.getAllPub()
    for result in results:
        listbox.insert(END, result)

def historico():
    historico = tk.Toplevel(janela)
    historico.title("Histórico")
    # Adicione widgets para implementar a funcionalidade aqui
    label = tk.Label(historico, text="Histórico")
    label.pack()

def criar_quadro_de_anuncio():
    
    def enviar():
        # pegue os dados inseridos pelo usuário e envie para o back-end
        url = entry_url.get()
        nome_arquivo = entry_nome.get()
        idioma = variavel.get()
        print(url, nome_arquivo, idioma)
        JW_Mural.MyApp.run(url, nome_arquivo, idioma)
        
    quadro_de_anuncio = tk.Toplevel(janela)
   
    quadro_de_anuncio.title("Quadro de Anúncio")
    
    label = tk.Label(quadro_de_anuncio, text="Criar Reuniao de meio de semana")
    label.pack()
   
    label_url = tk.Label(quadro_de_anuncio, text="URL:")
    label_url.pack()

    entry_url = tk.Entry(quadro_de_anuncio)
    entry_url.pack()

    label_nome = tk.Label(quadro_de_anuncio, text="Nome do arquivo:")
    label_nome.pack()

    entry_nome = tk.Entry(quadro_de_anuncio)
    entry_nome.pack()

    label_idioma = tk.Label(quadro_de_anuncio, text="Idioma:")
    label_idioma.pack()

    variavel = tk.StringVar(quadro_de_anuncio)
    variavel.set("pt")

    option_menu = tk.OptionMenu(quadro_de_anuncio, variavel, "pt")
    option_menu.pack()

    botao_enviar = tk.Button(quadro_de_anuncio, text="Enviar", command=enviar)
    botao_enviar.pack(pady='30')
    
    quadro_de_anuncio.geometry("300x300")
    

janela = tk.Tk()
janela.geometry("300x300")
janela.config(bg='white')

botao1 = tk.Button(janela, text="Criar Reuniao de meio de semana", command=criar_quadro_de_anuncio )

botao2 = tk.Button(janela, text="Publicadores", command=publicadores , state= "disabled")

botao3 = tk.Button(janela, text="Histórico", command=historico , state= "disabled")


botao1.pack(pady='10')
botao2.pack()
botao3.pack(pady='10')




janela.mainloop()
