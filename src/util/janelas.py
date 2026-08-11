import tkinter as tk
import ttkbootstrap as ttk
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

    # `verificarInclusaoPublicador` foi removida: publicadores desconhecidos passaram
    # a ser criados direto em `DatabaseOperations` (batizado=True), sem diálogo — a
    # janela abria a partir de threads de background e travava a UI.
