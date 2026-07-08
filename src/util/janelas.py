import tkinter as tk
import ttkbootstrap as ttk
from database import post, update_parte  # Importação correta
from ttkbootstrap.constants import *

class janelas:
    def solicitar_nome_publicador(parte, nomes_publicadores, semana):       
        root = ttk.Window()
        root.withdraw()  # Esconde a janela principal
        
        nome = None  # Variável para armazenar o nome selecionado
        janela_fechada = False  # Variável de controle
        
        def on_submit():
            nonlocal nome, janela_fechada
            nome = entry.get()
            janela_fechada = True
            top.destroy()
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

        top = ttk.Toplevel(root)
        top.title(f"Semana: {semana} - {parte}")
        
        # Container principal
        main_container = ttk.Frame(top, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Título
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text=f"Selecionar Publicador",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # Frame para os campos
        fields_frame = ttk.Frame(main_container)
        fields_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
        
        # Subtítulo com a parte e semana
        ttk.Label(
            fields_frame,
            text=f"Semana {semana} - {parte}",
            font=("Helvetica", 12),
            bootstyle="secondary"
        ).pack(pady=(0, 10))
        
        # Campo de busca
        entry = ttk.Entry(
            fields_frame,
            width=40,
            bootstyle="primary"
        )
        entry.pack(fill=X, pady=(0, 10))
        entry.focus_set()
        entry.bind("<KeyRelease>", update_listbox)
        
        # Lista de publicadores
        listbox = tk.Listbox(
            fields_frame,
            height=8,
            font=("Helvetica", 10)
        )
        listbox.pack(fill=BOTH, expand=YES, pady=(0, 10))
        listbox.bind("<<ListboxSelect>>", on_listbox_select)
        
        for nome in nomes_publicadores:
            listbox.insert(tk.END, nome)
            
        # Botão de confirmar
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Confirmar",
            command=on_submit,
            bootstyle="success",
            padding=(20, 10)
        ).pack(anchor=CENTER)
        
        # Centralizar a janela
        top.update_idletasks()
        width = 500
        height = 500
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configurar o protocolo de fechamento da janela
        def on_closing():
            nonlocal janela_fechada
            janela_fechada = True
            top.destroy()
            root.destroy()
        
        top.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Esperar a janela ser fechada
        while not janela_fechada:
            root.update()
        
        return nome

    def verificarInclusaoPublicador(nome, parte, semana):
        # Verificar se o nome é vazio, só tem espaços em branco ou é "não possui"
        if not nome or nome.strip() == "" or nome.lower() == "não possui":
            print(f"Ignorando nome: {nome}")
            return  # Ignora e retorna sem fazer nada
        
        janela_fechada = False  # Declarando a variável aqui
        resposta = None  # Para armazenar a resposta do usuário
        batizado = True  # Valor padrão para batizado
        
        def on_yes():
            nonlocal janela_fechada, resposta, batizado
            batizado = var_batizado.get()
            post(nome, batizado)  # Adiciona o publicador com status de batizado
            update_parte(nome, parte, semana)  # Atualiza o histórico
            print(f"Publicador {nome} adicionado ao banco de dados. Batizado: {batizado}")
            resposta = True
            janela_fechada = True
            top.destroy()
            root.destroy()

        def on_no():
            nonlocal janela_fechada, resposta
            resposta = False
            janela_fechada = True
            top.destroy()
            root.destroy()

        root = ttk.Window()
        root.withdraw()  # Esconde a janela principal
        
        top = ttk.Toplevel(root)
        top.title("Confirmação")
        
        # Container principal
        main_container = ttk.Frame(top, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Mensagem
        ttk.Label(
            main_container,
            text=f"Publicador {nome} não está no banco de dados.",
            font=("Helvetica", 12),
            bootstyle="primary",
            wraplength=300
        ).pack(pady=(0, 5))
        
        ttk.Label(
            main_container,
            text="Deseja adicionar?",
            font=("Helvetica", 12),
            bootstyle="secondary"
        ).pack(pady=(0, 10))
        
        # Frame para checkbox de batizado
        checkbox_frame = ttk.Frame(main_container)
        checkbox_frame.pack(fill=X, pady=(0, 10))
        
        var_batizado = tk.BooleanVar(value=True)  # Valor padrão True
        ttk.Checkbutton(
            checkbox_frame,
            text="Batizado",
            variable=var_batizado,
            bootstyle="primary"
        ).pack(pady=(0, 10))
        
        # Frame para botões
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Sim",
            command=on_yes,
            bootstyle="success",
            padding=(20, 10)
        ).pack(side=LEFT, padx=5, expand=True)
        
        ttk.Button(
            button_frame,
            text="Não",
            command=on_no,
            bootstyle="danger",
            padding=(20, 10)
        ).pack(side=LEFT, padx=5, expand=True)
        
        # Centralizar a janela
        top.update_idletasks()
        width = 400
        height = 250  # Aumentei a altura para acomodar o checkbox
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configurar o protocolo de fechamento da janela
        def on_closing():
            nonlocal janela_fechada, resposta
            resposta = False
            janela_fechada = True
            top.destroy()
            root.destroy()
        
        top.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Esperar a janela ser fechada
        while not janela_fechada:
            root.update()
            
        return resposta