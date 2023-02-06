import tkinter as tk
import JW_Mural

def enviar():
    # pegue os dados inseridos pelo usuário e envie para o back-end
    url = entry_url.get()
    nome_arquivo = entry_nome.get()
    idioma = variavel.get()
    print(url, nome_arquivo, idioma)
    JW_Mural.MyApp.run(url, nome_arquivo, idioma)

janela = tk.Tk()
janela.geometry("600x600")

label_url = tk.Label(janela, text="URL:")
label_url.pack()

entry_url = tk.Entry(janela)
entry_url.pack()

label_nome = tk.Label(janela, text="Nome do arquivo:")
label_nome.pack()

entry_nome = tk.Entry(janela)
entry_nome.pack()

label_idioma = tk.Label(janela, text="Idioma:")
label_idioma.pack()

variavel = tk.StringVar(janela)
variavel.set("pt")

option_menu = tk.OptionMenu(janela, variavel, "pt")
option_menu.pack()

botao_enviar = tk.Button(janela, text="Enviar", command=enviar)
botao_enviar.pack()

janela.mainloop()
