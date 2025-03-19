import tkinter as tk
from tkinter import *
import connetion_DB as post

class janelas:
    def solicitar_nome_publicador(parte, nomes_publicadores , semana):       
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

    def verificarInclusaoPublicador(nome , parte , semana):
        def on_yes():
            post.post(nome, False)
            post.update_parte(nome, parte, semana)
            
            print(f"Publicador {nome} adicionado ao banco de dados.")
            root.destroy()

        def on_no():
            root.destroy()

        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal   
        top = tk.Toplevel(root)
        top.title("Confirmação")
        top.geometry("300x150")
        # Sempre aparecer no meio do desktop
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        label = tk.Label(top, text=f"Publicador {nome} não está no banco de dados. Deseja adicionar?")
        label.pack(pady=10)

        button_frame = tk.Frame(top)
        button_frame.pack(pady=10)

        yes_button = tk.Button(button_frame, text="Sim", command=on_yes)
        yes_button.pack(side=tk.LEFT, padx=5)

        no_button = tk.Button(button_frame, text="Não", command=on_no)
        no_button.pack(side=tk.LEFT, padx=5)

        root.wait_window(top)