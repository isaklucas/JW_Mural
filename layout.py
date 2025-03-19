import tkinter as tk
from tkinter import *
import JW_Mural
import connetion_DB
import webbrowser
import time
import process.s140 as s140




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
        connetion_DB.post(nome, batizado)
        nome_entry.delete(0, END)
        batizado_var.set(False)
        atualizar_lista()
    
    def excluir_publicador(pub_id):
        print("Excluindo publicador", pub_id)
        connetion_DB.delete(pub_id)
        atualizar_lista()

    def atualizar_lista():
        for widget in lista_frame.winfo_children():
            widget.destroy()
        
        headers = ["Nome", "Batizado", "Ultima Parte", "Ações"]
        for col, header in enumerate(headers):
            tk.Label(lista_frame, text=header, font=('bold'), borderwidth=1, relief="solid").grid(row=0, column=col, sticky="W")
        
        results = connetion_DB.getAllPub()
  
        
        for i, result in enumerate(results, start=1):
            tk.Label(lista_frame, text=result["nome"], borderwidth=1, relief="solid").grid(row=i, column=0, sticky="W")
            tk.Label(lista_frame, text="Sim" if result["batizado"] else "Não", borderwidth=1, relief="solid").grid(row=i, column=1, sticky="W")
            tk.Label(lista_frame, text=result.get("ultima_parte", "N/A"), borderwidth=1, relief="solid").grid(row=i, column=2, sticky="W")
            excluir_button = tk.Button(lista_frame, text="Excluir", command=lambda r=result: excluir_publicador(result["nome"]))
            excluir_button.grid(row=i, column=3, sticky="W")

        
    
    publicadores_criar = tk.Toplevel(janela)
    publicadores_criar.title("Publicadores")
    publicadores_criar.geometry("300x300")

    nome_label = tk.Label(publicadores_criar, text="Nome:")
    nome_entry = tk.Entry(publicadores_criar)

    batizado_label = tk.Label(publicadores_criar, text="Batizado:", anchor="w")
    batizado_var = tk.BooleanVar()
    batizado_checkbox = tk.Checkbutton(publicadores_criar, variable=batizado_var)
    batizado_var.set(True)

    salvar_button = tk.Button(publicadores_criar, text="Adicionar", command=salvar_publicador)

    nome_label.grid(row=0, column=0, sticky="W")
    nome_entry.grid(row=0, column=1)
    batizado_label.grid(row=1, column=0, sticky="W")
    batizado_checkbox.grid(row=1, column=1)
    salvar_button.grid(row=2, column=1, pady=10)

    lista_frame = tk.Frame(publicadores_criar)
    lista_frame.grid(row=3, column=0, columnspan=2, sticky="W")

    atualizar_lista()
    

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
        utilizarBase = utilizar_base_var.get()
        qtdSemanas = int(entry_qtdSemanas.get())
        print(url, nome_arquivo, idioma , utilizarBase)
        s140.s140.gerar_s140(url, nome_arquivo, idioma , utilizarBase , qtdSemanas)
        
    quadro_de_anuncio = tk.Toplevel(janela)
   
    quadro_de_anuncio.title("Quadro de Anúncio")
    
    label = tk.Label(quadro_de_anuncio, text="Criar Reuniao de meio de semana")
    label.pack()
   
    label_url = tk.Label(quadro_de_anuncio, text="URL:")
    label_url.pack()

    entry_url = tk.Entry(quadro_de_anuncio)
    entry_url.pack()
    
    label_url = tk.Label(quadro_de_anuncio, text="Quantidade de Semanas")
    label_url.pack()

    entry_qtdSemanas = tk.Entry(quadro_de_anuncio)
    entry_qtdSemanas.pack()

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
    
    # Crie um CheckBox que pergunta se quer utilizar base de publicadores
    utilizar_base_var = tk.BooleanVar()
    utilizar_base_checkbox = tk.Checkbutton(quadro_de_anuncio, text="Utilizar base de publicadores", variable=utilizar_base_var)
    utilizar_base_checkbox.pack()
    

    botao_enviar = tk.Button(quadro_de_anuncio, text="Enviar", command=enviar)
    botao_enviar.pack(pady='30')
    
    quadro_de_anuncio.geometry("300x300")
    

janela = tk.Tk()
janela.geometry("300x300")
janela.config(bg='white')

botao1 = tk.Button(janela, text="Criar Reuniao de meio de semana", command=criar_quadro_de_anuncio )

botao2 = tk.Button(janela, text="Publicadores", command=publicadores)

botao3 = tk.Button(janela, text="Histórico", command=historico , state= "disabled")


botao1.pack(pady='10')
botao2.pack()
botao3.pack(pady='10')




janela.mainloop()
