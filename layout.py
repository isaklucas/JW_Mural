import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import tkinter as tk
import webbrowser
import time
import process.s140 as s140
from PIL import Image, ImageTk
import os
from database import post, getAllPub, delete
from database.db_operations import DatabaseOperations
import util.janelas as janelas
from util.startup_manager import initialize_application
import sys
import logging
import datetime
import threading

logger = logging.getLogger(__name__)

class ModernApp:
    def __init__(self, root):
        self.root = root
        # Configuração da janela principal com tema moderno
        self.root.iconbitmap("assets/icon.ico") if os.path.exists("assets/icon.ico") else None
        
        # Configuração do container principal
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # Título principal
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="JW Mural",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Sistema de Gerenciamento de Reuniões",
            font=("Helvetica", 12),
            bootstyle="secondary"
        )
        subtitle_label.pack()
        
        # Container para os cards
        self.cards_frame = ttk.Frame(self.main_frame, bootstyle="light")
        self.cards_frame.pack(fill=BOTH, expand=YES)
        
        # Criação dos cards
        self.create_card(
            "Criar Reunião",
            "Gere documentos para reuniões de meio de semana",
            "primary",
            self.criar_quadro_de_anuncio,
            0, 0
        )
        
        self.create_card(
            "Publicadores",
            "Gerencie a lista de publicadores",
            "info",
            self.publicadores,
            0, 1
        )
        
        self.create_card(
            "Histórico",
            "Visualize o histórico de reuniões",
            "warning",
            self.historico,
            1, 0
        )
        
        self.create_card(
            "Histórico de Publicadores",
            "Visualize o histórico de partes dos publicadores",
            "success",
            self.historico_publicadores,
            1, 1
        )
        
        self.create_card(
            "Dashboards",
            "Visualize estatísticas e gráficos",
            "danger",
            self.dashboards,
            2, 0
        )
        
        # Rodapé
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill=X, pady=(20, 0))
        
        version_label = ttk.Label(
            footer_frame,
            text="Versão 1.0",
            bootstyle="secondary"
        )
        version_label.pack(side=RIGHT)

    def create_card(self, title, description, style, command, row, col):
        """Cria um card estilizado com título, descrição e botão"""
        # Card principal com preenchimento maior e bordas arredondadas
        card = ttk.Frame(
            self.cards_frame,
            bootstyle="light",  # Alterado para light (branco)
            padding=20
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configurar o grid para expandir igualmente
        self.cards_frame.grid_columnconfigure(col, weight=1)
        self.cards_frame.grid_rowconfigure(row, weight=1)
        
        # Container para conteúdo do card com estilo
        content_frame = ttk.Frame(
            card,
            bootstyle="light"  # Alterado para light (branco)
        )
        content_frame.pack(fill=BOTH, expand=YES)
        
        # Título do card
        title_label = ttk.Label(
            content_frame,
            text=title,
            font=("Helvetica", 18, "bold"),
            bootstyle="primary",  # Mantém a cor primária apenas no texto
            justify="center"
        )
        title_label.pack(anchor=CENTER, pady=(0, 10), fill=X)
        
        # Descrição
        desc_label = ttk.Label(
            content_frame,
            text=description,
            wraplength=300,
            bootstyle="secondary",  # Cor secundária para descrição
            justify="center"
        )
        desc_label.pack(anchor=CENTER, pady=(0, 20), fill=X)
        
        # Frame para o botão (para centralizar)
        button_frame = ttk.Frame(
            content_frame,
            bootstyle="light"  # Alterado para light (branco)
        )
        button_frame.pack(side=BOTTOM, fill=X, pady=(10, 0))
        
        # Botão com estilo outline e hover
        access_button = ttk.Button(
            button_frame,
            text="ACESSAR",
            bootstyle=f"{style}-outline",
            command=command,
            padding=(20, 15)
        )
        access_button.pack(anchor=CENTER)
        
        # Configurar o hover do botão
        def on_enter(e):
            access_button.configure(bootstyle=style)
        
        def on_leave(e):
            access_button.configure(bootstyle=f"{style}-outline")
        
        access_button.bind("<Enter>", on_enter)
        access_button.bind("<Leave>", on_leave)

    def publicadores(self):
        # Criar janela de publicadores
        publicadores_window = ttk.Toplevel(self.root)
        publicadores_window.title("Gerenciar Publicadores")
        publicadores_window.geometry("800x600")
        
        # Container principal
        main_container = ttk.Frame(publicadores_window, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Título
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="Gerenciar Publicadores",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # Frame de busca
        search_frame = ttk.Frame(main_container)
        search_frame.pack(fill=X, pady=(0, 10))
        
        search_var = ttk.StringVar()
        
        # Campo de busca
        search_entry = ttk.Entry(
            search_frame,
            textvariable=search_var,
            width=40,
            bootstyle="primary"
        )
        search_entry.pack(side=LEFT, expand=YES, fill=X)
        
        def abrir_modal_adicionar():
            # Criar janela modal
            modal = ttk.Toplevel(publicadores_window)
            modal.title("Adicionar Publicador")
            
            # Container principal
            modal_container = ttk.Frame(modal, padding=20)
            modal_container.pack(fill=BOTH, expand=YES)
            
            # Título
            modal_title_frame = ttk.Frame(modal_container)
            modal_title_frame.pack(fill=X, pady=(0, 20))
            
            ttk.Label(
                modal_title_frame,
                text="Adicionar Publicador",
                font=("Helvetica", 20, "bold"),
                bootstyle="primary"
            ).pack(side=LEFT)
            
            # Frame para os campos
            fields_frame = ttk.Frame(modal_container)
            fields_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
            
            # Configurar grid para campos
            fields_frame.grid_columnconfigure(1, weight=1)
            
            # Nome
            ttk.Label(
                fields_frame,
                text="Nome:",
                font=("Helvetica", 12),
                bootstyle="secondary"
            ).grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
            
            nome_entry = ttk.Entry(
                fields_frame,
                width=40,
                bootstyle="primary"
            )
            nome_entry.grid(row=0, column=1, sticky="ew", pady=10)
            
            # Batizado
            batizado_var = ttk.BooleanVar(value=True)
            ttk.Checkbutton(
                fields_frame,
                text="Batizado",
                variable=batizado_var,
                bootstyle="primary-round-toggle"
            ).grid(row=1, column=0, columnspan=2, pady=20, sticky="w")
            
            # Frame do botão
            button_frame = ttk.Frame(modal_container)
            button_frame.pack(fill=X, pady=(20, 0))
            
            def adicionar_publicador():
                nome = nome_entry.get()
                batizado = batizado_var.get()
                if nome.strip():
                    from database import db_ops
                    db_ops.post(nome, batizado)
                    atualizar_lista()
                    modal.destroy()
            
            ttk.Button(
                button_frame,
                text="Adicionar",
                command=adicionar_publicador,
                bootstyle="success",
                padding=(20, 10)
            ).pack(side=LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancelar",
                command=modal.destroy,
                bootstyle="secondary",
                padding=(20, 10)
            ).pack(side=LEFT, padx=5)
            
            # Centralizar a janela
            modal.update_idletasks()
            largura_janela = 500
            altura_janela = 300
            x_centralizado = int((modal.winfo_screenwidth() / 2) - (largura_janela / 2))
            y_centralizado = int((modal.winfo_screenheight() / 2) - (altura_janela / 2))
            modal.geometry(f"{largura_janela}x{altura_janela}+{x_centralizado}+{y_centralizado}")
            modal.transient(publicadores_window)
            modal.grab_set()
            
            # Foco no campo de nome
            nome_entry.focus()
        
        # Botão de adicionar publicador
        ttk.Button(
            search_frame,
            text="Adicionar Publicador",
            command=abrir_modal_adicionar,
            bootstyle="primary"
        ).pack(side=RIGHT, padx=(5, 0))
        
        # Botão limpar busca
        clear_button = ttk.Button(
            search_frame,
            text="✕",
            command=lambda: [search_var.set(""), search_entry.insert(0, "Buscar publicador...")],
            bootstyle="secondary-link",
            width=3
        )
        clear_button.pack(side=LEFT, padx=5)
        
        # Frame para a tabela
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill=BOTH, expand=YES)
        
        # Configurar tabela
        tabela = ttk.Treeview(
            table_frame,
            columns=("nome", "batizado", "ultima_parte"),
            show="headings",
            height=15,
            bootstyle="primary"
        )
        
        # Estilo para as linhas alternadas
        tabela.tag_configure('oddrow', background='#f0f0f0')
        tabela.tag_configure('evenrow', background='white')
        
        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tabela.yview,
            bootstyle="primary-round"
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        tabela.configure(yscrollcommand=scrollbar.set)
        
        # Configurar colunas
        tabela.heading("nome", text="Nome", anchor=W)
        tabela.heading("batizado", text="Batizado", anchor=CENTER)
        tabela.heading("ultima_parte", text="Última Parte", anchor=W)
        
        # Configurar largura e alinhamento das colunas
        tabela.column("nome", width=300, anchor=W)
        tabela.column("batizado", width=100, anchor=CENTER)
        tabela.column("ultima_parte", width=300, anchor=W)
        
        tabela.pack(fill=BOTH, expand=YES, padx=(0, 10))
        
        # Frame para botões de ação
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=X, pady=(10, 0))
        
        # Variável para armazenar o item selecionado
        selected_item = {'nome': None}
        
        def atualizar_lista():
            try:
                # Limpa a tabela
                for item in tabela.get_children():
                    tabela.delete(item)
                
                # Obtém todos os publicadores
                from database import db_ops
                results = db_ops.getAllPub()
                
                # Filtra baseado na busca
                termo_busca = search_var.get().lower()
                if termo_busca and termo_busca != "buscar publicador...":
                    results = [r for r in results if termo_busca in r["nome"].lower()]
                
                # Ordenação
                results.sort(key=lambda x: x["nome"].lower())
                
                # Atualiza a tabela
                for i, result in enumerate(results):
                    row_tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
                    tabela.insert("", "end", values=(
                        result["nome"],
                        "Sim" if result["batizado"] else "Não",
                        result.get("ultima_parte", "N/A")
                    ), tags=row_tags)
                
                # Se não houver resultados, mostra uma mensagem na tabela
                if not results:
                    tabela.insert("", "end", values=("Nenhum publicador encontrado", "", ""))
            
            except Exception as e:
                print(f"Erro ao atualizar lista: {e}")
                tabela.insert("", "end", values=(f"Erro ao carregar publicadores: {str(e)}", "", ""))
        
        def on_select(event):
            selected = tabela.selection()
            if selected:
                item = tabela.item(selected[0])
                selected_item['nome'] = item['values'][0]
                editar_btn.configure(state="normal")
                excluir_btn.configure(state="disabled")
                excluir_btn.configure(state="normal")
            else:
                selected_item['nome'] = None
                editar_btn.configure(state="disabled")
                excluir_btn.configure(state="disabled")
        
        def editar_selecionado():
            if selected_item['nome']:
                # Criar janela modal
                modal = ttk.Toplevel(publicadores_window)
                modal.title("Editar Publicador")
                
                # Container principal
                edit_container = ttk.Frame(modal, padding=20)
                edit_container.pack(fill=BOTH, expand=YES)
                
                # Título
                title_frame = ttk.Frame(edit_container)
                title_frame.pack(fill=X, pady=(0, 20))
                
                ttk.Label(
                    title_frame,
                    text=f"Editar Publicador - {selected_item['nome']}",
                    font=("Helvetica", 20, "bold"),
                    bootstyle="primary"
                ).pack(side=LEFT)
                
                # Frame para os campos
                fields_frame = ttk.Frame(edit_container)
                fields_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
                
                # Configurar grid para campos
                fields_frame.grid_columnconfigure(1, weight=1)
                
                # Buscar dados atuais do publicador
                from database import db_ops
                publicador = next((p for p in db_ops.getAllPub() if p["nome"] == selected_item['nome']), None)
                
                if publicador:
                    # Nome
                    ttk.Label(
                        fields_frame,
                        text="Nome:",
                        font=("Helvetica", 12),
                        bootstyle="secondary"
                    ).grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
                    
                    nome_entry = ttk.Entry(
                        fields_frame,
                        width=40,
                        bootstyle="primary"
                    )
                    nome_entry.insert(0, publicador["nome"])
                    nome_entry.grid(row=0, column=1, sticky="ew", pady=10)
                    
                    # Batizado
                    batizado_var = ttk.BooleanVar(value=publicador.get("batizado", False))
                    ttk.Checkbutton(
                        fields_frame,
                        text="Batizado",
                        variable=batizado_var,
                        bootstyle="primary-round-toggle"
                    ).grid(row=1, column=0, columnspan=2, pady=20, sticky="w")
                    
                    # Última parte (somente leitura)
                    if "ultima_parte" in publicador:
                        ttk.Label(
                            fields_frame,
                            text="Última Parte:",
                            font=("Helvetica", 12),
                            bootstyle="secondary"
                        ).grid(row=2, column=0, padx=(0, 10), pady=10, sticky="w")
                        
                        ttk.Label(
                            fields_frame,
                            text=publicador.get("ultima_parte", "N/A"),
                            font=("Helvetica", 12),
                            bootstyle="primary"
                        ).grid(row=2, column=1, sticky="w", pady=10)
                    
                    # Botões
                    button_frame = ttk.Frame(edit_container)
                    button_frame.pack(fill=X, pady=(20, 0))
                    
                    def salvar_alteracoes():
                        novo_nome = nome_entry.get()
                        batizado = batizado_var.get()
                        
                        if novo_nome.strip():
                            from database import db_ops
                            # Se o nome mudou, precisamos excluir o antigo e criar um novo
                            if novo_nome != selected_item['nome']:
                                db_ops.delete(selected_item['nome'])
                                db_ops.post(novo_nome, batizado)
                            else:
                                # Se só mudou o status de batizado
                                db_ops.update_batismo(selected_item['nome'], batizado)
                            
                            atualizar_lista()
                            modal.destroy()
                    
                    ttk.Button(
                        button_frame,
                        text="Salvar",
                        command=salvar_alteracoes,
                        bootstyle="success",
                        padding=(20, 10)
                    ).pack(side=LEFT, padx=5)
                    
                    ttk.Button(
                        button_frame,
                        text="Cancelar",
                        command=modal.destroy,
                        bootstyle="secondary",
                        padding=(20, 10)
                    ).pack(side=LEFT, padx=5)
                    
                    # Centralizar a janela
                    modal.update_idletasks()
                    largura_janela = 500
                    altura_janela = 350
                    x_centralizado = int((modal.winfo_screenwidth() / 2) - (largura_janela / 2))
                    y_centralizado = int((modal.winfo_screenheight() / 2) - (altura_janela / 2))
                    modal.geometry(f"{largura_janela}x{altura_janela}+{x_centralizado}+{y_centralizado}")
                    modal.transient(publicadores_window)
                    modal.grab_set()
                    
                    # Foco no campo de nome
                    nome_entry.focus()
        
        def excluir_selecionado():
            if selected_item['nome']:
                # Criar janela de confirmação customizada
                dialog = ttk.Toplevel(publicadores_window)
                dialog.title("Confirmar Exclusão")
                
                # Tornar a janela modal
                dialog.transient(publicadores_window)
                dialog.grab_set()
                
                # Container principal
                dialog_frame = ttk.Frame(dialog, padding=20)
                dialog_frame.pack(fill=BOTH, expand=YES)
                
                # Mensagem
                ttk.Label(
                    dialog_frame,
                    text=f"Deseja realmente excluir o publicador {selected_item['nome']}?",
                    font=("Helvetica", 12),
                    wraplength=300
                ).pack(pady=(0, 20))
                
                # Frame para botões
                button_frame = ttk.Frame(dialog_frame)
                button_frame.pack(fill=X)
                
                # Variável para armazenar a resposta
                resposta = {'valor': False}
                
                def confirmar():
                    resposta['valor'] = True
                    dialog.destroy()
                
                def cancelar():
                    dialog.destroy()
                
                # Botões
                ttk.Button(
                    button_frame,
                    text="Sim",
                    command=confirmar,
                    bootstyle="danger",
                    width=10
                ).pack(side=LEFT, padx=5)
                
                ttk.Button(
                    button_frame,
                    text="Não",
                    command=cancelar,
                    bootstyle="secondary",
                    width=10
                ).pack(side=LEFT)
                
                # Centralizar a janela
                dialog.update_idletasks()
                width = 400
                height = 150
                x = publicadores_window.winfo_x() + (publicadores_window.winfo_width() // 2) - (width // 2)
                y = publicadores_window.winfo_y() + (publicadores_window.winfo_height() // 2) - (height // 2)
                dialog.geometry(f"{width}x{height}+{x}+{y}")
                
                # Esperar pela resposta
                dialog.wait_window()
                
                # Se confirmou, excluir
                if resposta['valor']:
                    from database import db_ops
                    db_ops.delete(selected_item['nome'])
                    atualizar_lista()
                    selected_item['nome'] = None
                    editar_btn.configure(state="disabled")
                    excluir_btn.configure(state="disabled")
        
        # Binding para seleção
        tabela.bind('<<TreeviewSelect>>', on_select)
        
        # Botões de ação
        editar_btn = ttk.Button(
            action_frame,
            text="Editar",
            command=editar_selecionado,
            bootstyle="primary",
            state="disabled",
            width=15
        )
        editar_btn.pack(side=LEFT, padx=5)
        
        excluir_btn = ttk.Button(
            action_frame,
            text="Excluir",
            command=excluir_selecionado,
            bootstyle="danger",
            state="disabled",
            width=15
        )
        excluir_btn.pack(side=LEFT, padx=5)
        
        # Botão de resetar histórico (separado visualmente)
        def resetar_historico():
            # Criar janela de confirmação
            dialog = ttk.Toplevel(publicadores_window)
            dialog.title("Confirmar Reset de Histórico")
            
            # Tornar a janela modal
            dialog.transient(publicadores_window)
            dialog.grab_set()
            
            # Container principal
            dialog_frame = ttk.Frame(dialog, padding=20)
            dialog_frame.pack(fill=BOTH, expand=YES)
            
            # Mensagem de aviso
            ttk.Label(
                dialog_frame,
                text="⚠️ ATENÇÃO: Esta operação é IRREVERSÍVEL!",
                font=("Helvetica", 14, "bold"),
                bootstyle="danger"
            ).pack(pady=(0, 10))
            
            ttk.Label(
                dialog_frame,
                text="Esta ação irá:\n• Limpar o histórico de TODOS os publicadores\n• Remover TODAS as reuniões cadastradas",
                font=("Helvetica", 11),
                wraplength=400,
                justify="center"
            ).pack(pady=(0, 20))
            
            ttk.Label(
                dialog_frame,
                text="Deseja realmente continuar?",
                font=("Helvetica", 12, "bold"),
                bootstyle="warning"
            ).pack(pady=(0, 20))
            
            # Frame para botões
            button_frame = ttk.Frame(dialog_frame)
            button_frame.pack(fill=X)
            
            # Variável para armazenar a resposta
            resposta = {'valor': False}
            
            def confirmar():
                resposta['valor'] = True
                dialog.destroy()
            
            def cancelar():
                dialog.destroy()
            
            # Botões
            ttk.Button(
                button_frame,
                text="Sim, Resetar Tudo",
                command=confirmar,
                bootstyle="danger",
                width=20
            ).pack(side=LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancelar",
                command=cancelar,
                bootstyle="secondary",
                width=15
            ).pack(side=LEFT, padx=5)
            
            # Centralizar a janela
            dialog.update_idletasks()
            width = 450
            height = 250
            x = publicadores_window.winfo_x() + (publicadores_window.winfo_width() // 2) - (width // 2)
            y = publicadores_window.winfo_y() + (publicadores_window.winfo_height() // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Esperar pela resposta
            dialog.wait_window()
            
            # Se confirmou, executar reset
            if resposta['valor']:
                try:
                    from database import db_ops
                    resultado = db_ops.resetar_todo_historico()
                    
                    if resultado['success']:
                        from ttkbootstrap.dialogs import Messagebox
                        Messagebox.show_info(
                            resultado['message'],
                            "Histórico Resetado",
                            parent=publicadores_window
                        )
                        atualizar_lista()
                    else:
                        from ttkbootstrap.dialogs import Messagebox
                        Messagebox.show_error(
                            resultado['message'],
                            "Erro ao Resetar",
                            parent=publicadores_window
                        )
                except Exception as e:
                    from ttkbootstrap.dialogs import Messagebox
                    Messagebox.show_error(
                        f"Erro ao resetar histórico: {str(e)}",
                        "Erro",
                        parent=publicadores_window
                    )
        
        # Separador visual
        ttk.Separator(action_frame, orient="vertical").pack(side=LEFT, fill=Y, padx=10)
        
        resetar_btn = ttk.Button(
            action_frame,
            text="Resetar Todo Histórico",
            command=resetar_historico,
            bootstyle="danger-outline",
            width=20
        )
        resetar_btn.pack(side=LEFT, padx=5)
        
        # Botão de voltar
        voltar_btn = ttk.Button(
            main_container,
            text="Voltar",
            command=publicadores_window.destroy,
            bootstyle="secondary",
            width=15
        )
        voltar_btn.pack(side=BOTTOM, pady=(20, 0))
        
        # Configurar campo de busca
        search_var.trace("w", lambda *args: atualizar_lista())
        
        # Ícone ou label de busca
        ttk.Label(
            search_frame,
            text="🔍",
            font=("Helvetica", 12),
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(0, 5))
        
        # Texto placeholder usando bind
        search_entry.insert(0, "Buscar publicador...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, END) if search_entry.get() == "Buscar publicador..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Buscar publicador...") if search_entry.get() == "" else None)
        
        # Carregar dados iniciais
        atualizar_lista()
        
        # Centralizar a janela
        publicadores_window.update_idletasks()
        width = publicadores_window.winfo_width()
        height = publicadores_window.winfo_height()
        x = (publicadores_window.winfo_screenwidth() // 2) - (width // 2)
        y = (publicadores_window.winfo_screenheight() // 2) - (height // 2)
        publicadores_window.geometry(f"{width}x{height}+{x}+{y}")

    def historico(self):
        # Configuração da janela
        historico_window = ttk.Toplevel(self.root)
        historico_window.title("Histórico de Reuniões")
        historico_window.geometry("1024x768")
        
        # Container principal
        main_container = ttk.Frame(historico_window, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Título
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="Histórico de Reuniões",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # Frame de busca e filtros
        search_frame = ttk.Frame(main_container)
        search_frame.pack(fill=X, pady=(0, 20))
        
        # Filtro por mês
        ttk.Label(
            search_frame,
            text="Mês:",
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(0, 10))
        
        mes_var = ttk.StringVar()
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_combo = ttk.Combobox(
            search_frame,
            textvariable=mes_var,
            values=meses,
            width=15,
            state="readonly",
            bootstyle="primary"
        )
        mes_combo.pack(side=LEFT, padx=(0, 20))
        
        # Filtro por ano
        ttk.Label(
            search_frame,
            text="Ano:",
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(0, 10))
        
        ano_var = ttk.StringVar()
        ano_combo = ttk.Combobox(
            search_frame,
            textvariable=ano_var,
            values=[str(datetime.datetime.now().year - i) for i in range(5)],
            width=10,
            state="readonly",
            bootstyle="primary"
        )
        ano_combo.pack(side=LEFT, padx=(0, 20))
        ano_combo.set(str(datetime.datetime.now().year))
        
        # Botão de buscar
        ttk.Button(
            search_frame,
            text="Buscar",
            command=lambda: carregar_reunioes(),
            bootstyle="primary",
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        # Botão de limpar filtros
        ttk.Button(
            search_frame,
            text="Limpar Filtros",
            command=lambda: [mes_var.set(""), ano_var.set(str(datetime.datetime.now().year)), carregar_reunioes()],
            bootstyle="secondary-outline",
            width=20
        ).pack(side=LEFT)
        
        # Frame para a tabela
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill=BOTH, expand=YES)
        
        # Criar Treeview
        colunas = ("data", "presidente", "semana_ano", "detalhes")
        tree = ttk.Treeview(
            table_frame,
            columns=colunas,
            show="headings",
            bootstyle="primary",
            height=20
        )
        
        # Configurar colunas
        tree.heading("data", text="Data de Criação", anchor=CENTER)
        tree.heading("presidente", text="Presidente", anchor=CENTER)
        tree.heading("semana_ano", text="Semana/Ano", anchor=CENTER)
        tree.heading("detalhes", text="Detalhes", anchor=CENTER)
        
        # Configurar largura das colunas
        tree.column("data", width=300, anchor=CENTER)
        tree.column("presidente", width=300, anchor=CENTER)
        tree.column("semana_ano", width=150, anchor=CENTER)
        tree.column("detalhes", width=100, anchor=CENTER)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview,
            bootstyle="primary-round"
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(fill=BOTH, expand=YES)
        
        def mostrar_detalhes(item):
            # Obter dados da reunião selecionada
            valores = tree.item(item)['values']
            data = valores[0]  # Data formatada
            semana_ano = valores[2]  # "Semana 9-15 DE JUNHO/2025"
            
            # Extrair semana e ano do formato "Semana 9-15 DE JUNHO/2025"
            # Remover "Semana " do início e dividir por "/"
            partes = semana_ano.replace("Semana ", "").split('/')
            semana = partes[0].strip()  # Extrair a semana (ex: "9-15 DE JUNHO")
            ano = int(partes[1])  # Extrair o ano
            
            # Criar janela de detalhes
            detalhes_window = ttk.Toplevel(historico_window)
            detalhes_window.title(f"Detalhes da Reunião - {data}")
            detalhes_window.geometry("600x400")
            
            # Container principal
            main_container = ttk.Frame(detalhes_window, padding=20)
            main_container.pack(fill=BOTH, expand=YES)
            
            # Título
            ttk.Label(
                main_container,
                text=f"Detalhes da Reunião - {data}",
                font=("Helvetica", 16, "bold"),
                bootstyle="primary"
            ).pack(pady=(0, 20))
            
            # Frame para os detalhes
            detalhes_frame = ttk.Frame(main_container)
            detalhes_frame.pack(fill=BOTH, expand=YES)
            
            # Criar Treeview para detalhes
            detalhes_tree = ttk.Treeview(
                detalhes_frame,
                columns=("parte", "participante"),
                show="headings",
                bootstyle="primary",
                height=12
            )
            
            # Configurar colunas
            detalhes_tree.heading("parte", text="Parte", anchor=CENTER)
            detalhes_tree.heading("participante", text="Participante", anchor=CENTER)
            
            # Configurar largura das colunas
            detalhes_tree.column("parte", width=250, anchor=W)
            detalhes_tree.column("participante", width=250, anchor=W)
            
            # Adicionar scrollbar
            scrollbar = ttk.Scrollbar(
                detalhes_frame,
                orient="vertical",
                command=detalhes_tree.yview,
                bootstyle="primary-round"
            )
            scrollbar.pack(side=RIGHT, fill=Y)
            detalhes_tree.configure(yscrollcommand=scrollbar.set)
            detalhes_tree.pack(fill=BOTH, expand=YES, padx=(0, 10))
            
            try:
                from database import db_ops
                # Buscar reunião usando semana e ano
                reuniao = db_ops.buscar_reuniao(ano, semana)
                
                if reuniao:
                    # Lista de todas as partes com seus participantes
                    detalhes = [
                        ("Presidente", reuniao['presidente']),
                        ("Oração Inicial", reuniao['oracao_inicial']),
                        ("Tesouro", reuniao['tesouro']),
                        ("Joias Espirituais", reuniao['joias_espirituais']),
                        ("Leitura da Bíblia", reuniao['leitura_biblia']),
                        ("Escola - Primeira Parte", reuniao['escola']['primeira_parte']),
                        ("Escola - Segunda Parte", reuniao['escola']['segunda_parte']),
                        ("Escola - Terceira Parte", reuniao['escola']['terceira_parte']),
                        ("Escola - Quarta Parte", reuniao['escola']['quarta_parte']),
                        ("Nossa Vida Cristã - Primeira Parte", reuniao['nossa_vida_crista']['primeira_parte']),
                        ("Nossa Vida Cristã - Segunda Parte", reuniao['nossa_vida_crista']['segunda_parte']),
                        ("Estudo de Congregação", reuniao['estudo_congregacao']),
                        ("Oração Final", reuniao['oracao_final'])
                    ]
                    
                    # Filtrar partes que não são "não possui" e inserir na tabela com cores alternadas
                    for i, (parte, participante) in enumerate(detalhes):
                        if participante != "não possui":
                            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                            detalhes_tree.insert("", END, values=(parte, participante), tags=(tag,))
                    
                    # Configurar cores alternadas
                    detalhes_tree.tag_configure('evenrow', background='#f0f0f0')
                    detalhes_tree.tag_configure('oddrow', background='white')
                else:
                    ttk.Label(
                        main_container,
                        text=f"Nenhum detalhe encontrado para {semana}/{ano}",
                        bootstyle="danger"
                    ).pack(pady=20)
            
            except Exception as e:
                logger.error(f"Erro ao carregar detalhes: {str(e)}")
                ttk.Label(
                    main_container,
                    text=f"Erro ao carregar detalhes: {str(e)}",
                    bootstyle="danger"
                ).pack(pady=20)
            
            # Botão de voltar
            ttk.Button(
                main_container,
                text="Voltar",
                command=detalhes_window.destroy,
                bootstyle="secondary",
                width=15
            ).pack(side=BOTTOM, pady=(20, 0))
            
            # Centralizar a janela
            detalhes_window.update_idletasks()
            width = detalhes_window.winfo_width()
            height = detalhes_window.winfo_height()
            x = (detalhes_window.winfo_screenwidth() // 2) - (width // 2)
            y = (detalhes_window.winfo_screenheight() // 2) - (height // 2)
            detalhes_window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Tornar a janela modal
            detalhes_window.transient(historico_window)
            detalhes_window.grab_set()
        
        def carregar_reunioes():
            # Limpar tabela
            for item in tree.get_children():
                tree.delete(item)
            
            # Obter filtros
            mes = mes_var.get()
            ano = ano_var.get() if ano_var.get() else None
            
            try:
                # Buscar reuniões - quando não há filtros, usar limite alto para retornar todas
                from database import db_ops
                limite = 10000 if not ano and not mes else 100
                reunioes = db_ops.listar_reunioes(
                    ano=int(ano) if ano else None,
                    limite=limite,
                    pagina=1
                )
                
                if not reunioes:
                    tree.insert("", END, values=("Nenhuma reunião encontrada", "", "", ""))
                    return
                
                # Adicionar reuniões na tabela
                for reuniao in reunioes:
                    # Converter data para formato desejado
                    data_reuniao = datetime.datetime.fromisoformat(reuniao['data_reuniao'])
                    semana = reuniao['semana']
                    ano = reuniao['ano']
                    
                    # Calcular datas da semana
                    data_inicio = data_reuniao - datetime.timedelta(days=data_reuniao.weekday())
                    data_fim = data_inicio + datetime.timedelta(days=6)
                    
                    # Mapeamento de meses em português para números
                    meses_pt = {
                        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
                    }
                    
                    # Formatar data usando nomes de meses em português
                    nome_mes_inicio = list(meses_pt.keys())[data_inicio.month - 1]
                    nome_mes_fim = list(meses_pt.keys())[data_fim.month - 1]
                    data_formatada = f"{data_inicio.day} de {nome_mes_inicio} a {data_fim.day} de {nome_mes_fim}"
                    
                    # Verificar filtro de mês usando número do mês
                    if mes:
                        mes_filtro_num = meses_pt.get(mes.lower())
                        if mes_filtro_num and data_inicio.month != mes_filtro_num:
                            continue
                    
                    # Inserir na tabela com ícone de seta
                    tree.insert("", END, values=(
                        data_formatada,
                        reuniao['presidente'],
                        f"Semana {semana}/{ano}",
                        "↗"  # Ícone de seta diagonal para cima
                    ))
            
            except Exception as e:
                logger.error(f"Erro ao carregar reuniões: {str(e)}")
                tree.insert("", END, values=(f"Erro ao carregar reuniões: {str(e)}", "", "", ""))
        
        # Configurar evento de clique na linha
        def on_tree_click(event):
            item = tree.identify_row(event.y)
            if item:
                mostrar_detalhes(item)
        
        tree.bind("<ButtonRelease-1>", on_tree_click)
        
        # Função para criar reunião manual (definida dentro do escopo)
        def criar_reuniao_manual_interna():
            # Criar janela modal
            criar_window = ttk.Toplevel(historico_window)
            criar_window.title("Criar Reunião Manual")
            criar_window.geometry("900x800")
            
            # Container principal com scroll
            main_container_criar = ttk.Frame(criar_window, padding=20)
            main_container_criar.pack(fill=BOTH, expand=YES)
            
            # Título
            title_frame_criar = ttk.Frame(main_container_criar)
            title_frame_criar.pack(fill=X, pady=(0, 20))
            
            ttk.Label(
                title_frame_criar,
                text="Criar Reunião Manual",
                font=("Helvetica", 20, "bold"),
                bootstyle="primary"
            ).pack(side=LEFT)
            
            # Frame para seleção de data
            data_frame = ttk.LabelFrame(main_container_criar, text="Seleção de Semana", padding=15)
            data_frame.pack(fill=X, pady=(0, 20))
            
            # Campo para selecionar a segunda-feira da semana
            ttk.Label(
                data_frame,
                text="Data da Segunda-feira:",
                bootstyle="secondary"
            ).pack(side=LEFT, padx=(0, 10))
            
            data_segunda_var = ttk.StringVar()
            data_segunda_entry = ttk.Entry(
                data_frame,
                textvariable=data_segunda_var,
                width=15,
                bootstyle="primary"
            )
            data_segunda_entry.pack(side=LEFT, padx=(0, 10))
            # Calcular próxima segunda-feira
            hoje = datetime.datetime.now()
            dias_para_segunda = (7 - hoje.weekday()) % 7
            if dias_para_segunda == 0 and hoje.weekday() != 0:
                dias_para_segunda = 7
            proxima_segunda = hoje + datetime.timedelta(days=dias_para_segunda)
            data_segunda_entry.insert(0, proxima_segunda.strftime("%d/%m/%Y"))
            
            # Botão para calcular semana
            def calcular_semana():
                try:
                    # Converter data de entrada
                    data_str = data_segunda_var.get().strip()
                    data_segunda = datetime.datetime.strptime(data_str, "%d/%m/%Y")
                    
                    # Garantir que é segunda-feira (ajustar se necessário)
                    dias_para_segunda = (data_segunda.weekday()) % 7
                    if dias_para_segunda != 0:
                        data_segunda = data_segunda - datetime.timedelta(days=dias_para_segunda)
                        data_segunda_var.set(data_segunda.strftime("%d/%m/%Y"))
                    
                    # Calcular domingo (6 dias depois)
                    data_domingo = data_segunda + datetime.timedelta(days=6)
                    
                    # Mapeamento de meses em português
                    meses_pt = {
                        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                    }
                    
                    # Formatar semana no padrão do banco: "9-15 DE JUNHO"
                    if data_segunda.month == data_domingo.month:
                        semana_formatada = f"{data_segunda.day}-{data_domingo.day} DE {meses_pt[data_segunda.month].upper()}"
                    else:
                        # Se a semana cruza meses, usar o mês da segunda-feira
                        semana_formatada = f"{data_segunda.day}-{data_domingo.day} DE {meses_pt[data_segunda.month].upper()}"
                    
                    semana_label_var.set(semana_formatada)
                    
                except Exception as e:
                    from ttkbootstrap.dialogs import Messagebox
                    Messagebox.show_error(f"Erro ao calcular semana: {str(e)}", "Erro", parent=criar_window)
            
            ttk.Button(
                data_frame,
                text="Calcular Semana",
                command=calcular_semana,
                bootstyle="primary-outline"
            ).pack(side=LEFT, padx=(0, 10))
            
            # Label para mostrar a semana formatada
            semana_label_var = ttk.StringVar(value="")
            semana_label = ttk.Label(
                data_frame,
                textvariable=semana_label_var,
                font=("Helvetica", 11, "bold"),
                bootstyle="info"
            )
            semana_label.pack(side=LEFT, padx=(10, 0))
            
            # Calcular semana inicial
            calcular_semana()
            
            # Buscar lista de publicadores
            from database import db_ops
            publicadores = db_ops.getAllPub()
            nomes_publicadores = ["não possui"] + [pub['nome'] for pub in publicadores]
            
            # Frame para campos de partes (com scroll)
            scroll_frame = ttk.Frame(main_container_criar)
            scroll_frame.pack(fill=BOTH, expand=YES)
            
            # Canvas para scroll
            canvas = tk.Canvas(scroll_frame)
            scrollbar_criar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_criar.set)
            
            # Frame para partes
            partes_frame = ttk.LabelFrame(scrollable_frame, text="Partes da Reunião", padding=15)
            partes_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
            
            # Dicionário para armazenar os comboboxes
            partes_widgets = {}
            
            # Lista de partes na ordem correta
            partes_lista = [
                ("presidente", "Presidente"),
                ("oracao_inicial", "Oração Inicial"),
                ("tesouro", "Tesouro"),
                ("joias_espirituais", "Joias Espirituais"),
                ("leitura_biblia", "Leitura da Bíblia"),
                ("escola_primeira_parte", "Escola - Primeira Parte"),
                ("escola_segunda_parte", "Escola - Segunda Parte"),
                ("escola_terceira_parte", "Escola - Terceira Parte"),
                ("escola_quarta_parte", "Escola - Quarta Parte"),
                ("nvc_primeira_parte", "Nossa Vida Cristã - Primeira Parte"),
                ("nvc_segunda_parte", "Nossa Vida Cristã - Segunda Parte"),
                ("estudo_congregacao", "Estudo de Congregação"),
                ("oracao_final", "Oração Final")
            ]
            
            # Criar campos para cada parte usando Entry + Listbox (similar à tela de criar reunião)
            for i, (key, label) in enumerate(partes_lista):
                row_frame = ttk.Frame(partes_frame)
                row_frame.pack(fill=X, pady=5)
                
                ttk.Label(
                    row_frame,
                    text=f"{label}:",
                    width=30,
                    anchor=W,
                    bootstyle="secondary"
                ).pack(side=LEFT, padx=(0, 10))
                
                # Frame para Entry e Listbox
                input_frame = ttk.Frame(row_frame)
                input_frame.pack(side=LEFT, fill=X, expand=YES)
                
                parte_var = ttk.StringVar(value="não possui")
                parte_entry = ttk.Entry(
                    input_frame,
                    textvariable=parte_var,
                    width=40,
                    bootstyle="primary"
                )
                parte_entry.pack(fill=X, expand=YES)
                
                # Listbox para mostrar opções filtradas
                parte_listbox = tk.Listbox(
                    input_frame,
                    height=5,
                    font=("Helvetica", 10)
                )
                parte_listbox.pack_forget()  # Inicialmente escondido
                
                # Criar classe para manter estado de cada campo
                class CampoPublicador:
                    def __init__(self, entry, listbox, valores_completos):
                        self.entry = entry
                        self.listbox = listbox
                        self.valores_completos = valores_completos
                        self.listbox_visivel = False
                    
                    def update_listbox(self, event=None):
                        texto_atual = self.entry.get().lower()
                        
                        # Se houver "/", pegar apenas o último termo após a barra
                        if '/' in texto_atual:
                            texto_atual = texto_atual.split('/')[-1].strip()
                        
                        # Limpar listbox
                        self.listbox.delete(0, tk.END)
                        
                        # Filtrar valores
                        if texto_atual:
                            valores_filtrados = [v for v in self.valores_completos if texto_atual in v.lower()]
                        else:
                            valores_filtrados = self.valores_completos
                        
                        # Adicionar valores filtrados ao listbox
                        for valor in valores_filtrados:
                            self.listbox.insert(tk.END, valor)
                        
                        # Mostrar/ocultar listbox baseado em se há valores
                        if valores_filtrados and texto_atual:
                            if not self.listbox_visivel:
                                self.listbox.pack(fill=X, expand=YES)
                                self.listbox_visivel = True
                        else:
                            if self.listbox_visivel:
                                self.listbox.pack_forget()
                                self.listbox_visivel = False
                    
                    def on_listbox_select(self, event):
                        selection = self.listbox.curselection()
                        if selection:
                            index = selection[0]
                            selected_name = self.listbox.get(index)
                            current_text = self.entry.get()
                            
                            # Se houver "/", adicionar após a barra
                            if '/' in current_text:
                                parts = current_text.split('/')
                                # Manter tudo antes da última barra e adicionar o novo nome
                                if len(parts) > 1:
                                    # Pegar tudo antes da última barra
                                    antes_barra = '/'.join(parts[:-1])
                                    self.entry.delete(0, tk.END)
                                    self.entry.insert(0, antes_barra + ' / ' + selected_name)
                                else:
                                    self.entry.delete(0, tk.END)
                                    self.entry.insert(0, parts[0] + ' / ' + selected_name)
                            else:
                                # Se não houver "/", substituir
                                self.entry.delete(0, tk.END)
                                self.entry.insert(0, selected_name)
                            
                            # Ocultar listbox após seleção
                            self.listbox.pack_forget()
                            self.listbox_visivel = False
                            # Focar no entry novamente
                            self.entry.focus_set()
                    
                    def on_focus_out(self, event):
                        # Ocultar listbox quando perder foco
                        if self.listbox_visivel:
                            self.listbox.pack_forget()
                            self.listbox_visivel = False
                
                # Criar instância do campo
                campo = CampoPublicador(parte_entry, parte_listbox, nomes_publicadores)
                
                # Bind eventos
                parte_entry.bind('<KeyRelease>', campo.update_listbox)
                parte_listbox.bind('<<ListboxSelect>>', campo.on_listbox_select)
                parte_listbox.bind('<Double-Button-1>', campo.on_listbox_select)
                parte_entry.bind('<FocusOut>', campo.on_focus_out)
                
                partes_widgets[key] = parte_var
            
            canvas.pack(side=LEFT, fill=BOTH, expand=YES)
            scrollbar_criar.pack(side=RIGHT, fill=Y)
            
            # Frame para botões
            button_frame_criar = ttk.Frame(main_container_criar)
            button_frame_criar.pack(fill=X, pady=(20, 0))
            
            def salvar_reuniao():
                try:
                    # Validar data
                    data_str = data_segunda_var.get().strip()
                    data_segunda = datetime.datetime.strptime(data_str, "%d/%m/%Y")
                    
                    # Garantir que é segunda-feira
                    dias_para_segunda = (data_segunda.weekday()) % 7
                    if dias_para_segunda != 0:
                        data_segunda = data_segunda - datetime.timedelta(days=dias_para_segunda)
                        data_segunda_var.set(data_segunda.strftime("%d/%m/%Y"))
                    
                    # Calcular domingo
                    data_domingo = data_segunda + datetime.timedelta(days=6)
                    
                    # Formatar semana
                    meses_pt = {
                        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                    }
                    
                    # Formatar semana no padrão do banco: "9-15 DE JUNHO"
                    if data_segunda.month == data_domingo.month:
                        semana_formatada = f"{data_segunda.day}-{data_domingo.day} DE {meses_pt[data_segunda.month].upper()}"
                    else:
                        # Se a semana cruza meses, usar o mês da segunda-feira
                        semana_formatada = f"{data_segunda.day}-{data_domingo.day} DE {meses_pt[data_segunda.month].upper()}"
                    
                    semana = semana_formatada
                    ano = data_segunda.year
                    
                    # Preparar dados da reunião
                    dados_reuniao = {
                        'ano': ano,
                        'semana': semana,
                        'data_reuniao': data_segunda.isoformat(),  # Data da segunda-feira
                        'presidente': partes_widgets['presidente'].get().strip() or "não possui",
                        'oracao_inicial': partes_widgets['oracao_inicial'].get().strip() or "não possui",
                        'tesouro': partes_widgets['tesouro'].get().strip() or "não possui",
                        'joias_espirituais': partes_widgets['joias_espirituais'].get().strip() or "não possui",
                        'leitura_biblia': partes_widgets['leitura_biblia'].get().strip() or "não possui",
                        'escola': {
                            'primeira_parte': partes_widgets['escola_primeira_parte'].get().strip() or "não possui",
                            'segunda_parte': partes_widgets['escola_segunda_parte'].get().strip() or "não possui",
                            'terceira_parte': partes_widgets['escola_terceira_parte'].get().strip() or "não possui",
                            'quarta_parte': partes_widgets['escola_quarta_parte'].get().strip() or "não possui"
                        },
                        'nossa_vida_crista': {
                            'primeira_parte': partes_widgets['nvc_primeira_parte'].get().strip() or "não possui",
                            'segunda_parte': partes_widgets['nvc_segunda_parte'].get().strip() or "não possui"
                        },
                        'estudo_congregacao': partes_widgets['estudo_congregacao'].get().strip() or "não possui",
                        'oracao_final': partes_widgets['oracao_final'].get().strip() or "não possui"
                    }
                    
                    # Salvar reunião
                    resultado = db_ops.salvar_reuniao(dados_reuniao)
                    
                    if resultado['success']:
                        # Recarregar lista de reuniões antes de fechar a janela
                        carregar_reunioes()
                        # Mostrar mensagem de sucesso usando a janela pai
                        from ttkbootstrap.dialogs import Messagebox
                        Messagebox.show_info(
                            f"Reunião criada com sucesso!\nSemana: {semana}\nAno: {ano}",
                            "Sucesso",
                            parent=historico_window
                        )
                        criar_window.destroy()
                    else:
                        from ttkbootstrap.dialogs import Messagebox
                        Messagebox.show_error(
                            resultado['message'],
                            "Erro ao Salvar",
                            parent=historico_window
                        )
                        
                except ValueError as ve:
                    from ttkbootstrap.dialogs import Messagebox
                    Messagebox.show_error(
                        f"Data inválida. Use o formato DD/MM/AAAA",
                        "Erro de Validação",
                        parent=historico_window
                    )
                except Exception as e:
                    from ttkbootstrap.dialogs import Messagebox
                    Messagebox.show_error(
                        f"Erro ao salvar reunião: {str(e)}",
                        "Erro",
                        parent=historico_window
                    )
            
            ttk.Button(
                button_frame_criar,
                text="Salvar Reunião",
                command=salvar_reuniao,
                bootstyle="success",
                width=20
            ).pack(side=LEFT, padx=5)
            
            ttk.Button(
                button_frame_criar,
                text="Cancelar",
                command=criar_window.destroy,
                bootstyle="secondary",
                width=15
            ).pack(side=LEFT, padx=5)
            
            # Centralizar janela
            criar_window.update_idletasks()
            width = criar_window.winfo_width()
            height = criar_window.winfo_height()
            x = (criar_window.winfo_screenwidth() // 2) - (width // 2)
            y = (criar_window.winfo_screenheight() // 2) - (height // 2)
            criar_window.geometry(f"{width}x{height}+{x}+{y}")
            criar_window.transient(historico_window)
            criar_window.grab_set()
            
            # Foco no campo de data
            data_segunda_entry.focus()
        
        # Botão de criar reunião
        ttk.Button(
            title_frame,
            text="Criar Reunião",
            command=criar_reuniao_manual_interna,
            bootstyle="success",
            width=20
        ).pack(side=RIGHT, padx=(10, 0))
        
        # Botão de voltar
        voltar_btn = ttk.Button(
            main_container,
            text="Voltar",
            command=historico_window.destroy,
            bootstyle="secondary",
            width=15
        )
        voltar_btn.pack(side=BOTTOM, pady=(20, 0))
        
        # Carregar dados iniciais
        carregar_reunioes()
        
        # Centralizar a janela
        historico_window.update_idletasks()
        width = historico_window.winfo_width()
        height = historico_window.winfo_height()
        x = (historico_window.winfo_screenwidth() // 2) - (width // 2)
        y = (historico_window.winfo_screenheight() // 2) - (height // 2)
        historico_window.geometry(f"{width}x{height}+{x}+{y}")

    def criar_quadro_de_anuncio(self):
        quadro_de_anuncio = ttk.Toplevel(self.root)
        quadro_de_anuncio.title("Criar Reunião")
        
        # Container principal
        main_container = ttk.Frame(quadro_de_anuncio, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Título
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="Criar Reunião de Meio de Semana",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # Frame para os campos
        fields_frame = ttk.Frame(main_container)
        fields_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
        
        # Configurar grid para campos
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # URL
        ttk.Label(
            fields_frame,
            text="URL:",
            font=("Helvetica", 12),
            bootstyle="secondary"
        ).grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
        
        entry_url = ttk.Entry(
            fields_frame,
            width=50,
            bootstyle="primary"
        )
        entry_url.grid(row=0, column=1, sticky="ew", pady=10)
        
        # Quantidade de Semanas
        ttk.Label(
            fields_frame,
            text="Quantidade de Semanas:",
            font=("Helvetica", 12),
            bootstyle="secondary"
        ).grid(row=1, column=0, padx=(0, 10), pady=10, sticky="w")
        
        entry_qtdSemanas = ttk.Entry(
            fields_frame,
            width=10,
            bootstyle="primary"
        )
        entry_qtdSemanas.grid(row=1, column=1, sticky="w", pady=10)
        
        # Nome do Arquivo
        ttk.Label(
            fields_frame,
            text="Nome do Arquivo:",
            font=("Helvetica", 12),
            bootstyle="secondary"
        ).grid(row=2, column=0, padx=(0, 10), pady=10, sticky="w")
        
        entry_nome = ttk.Entry(
            fields_frame,
            width=50,
            bootstyle="primary"
        )
        entry_nome.grid(row=2, column=1, sticky="ew", pady=10)
        
        # Idioma
        ttk.Label(
            fields_frame,
            text="Idioma:",
            font=("Helvetica", 12),
            bootstyle="secondary"
        ).grid(row=3, column=0, padx=(0, 10), pady=10, sticky="w")
        
        variavel = ttk.StringVar(quadro_de_anuncio)
        variavel.set("pt")
        
        idioma_combo = ttk.Combobox(
            fields_frame,
            textvariable=variavel,
            values=["pt"],
            state="readonly",
            width=10,
            bootstyle="primary"
        )
        idioma_combo.grid(row=3, column=1, sticky="w", pady=10)
        
        # Checkbox para base de publicadores
        utilizar_base_var = ttk.BooleanVar()
        ttk.Checkbutton(
            fields_frame,
            text="Utilizar base de publicadores",
            variable=utilizar_base_var,
            bootstyle="primary-round-toggle"
        ).grid(row=4, column=0, columnspan=2, pady=20, sticky="w")
        
        # Botão de enviar
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=X, pady=(20, 0))
        
        gerar_btn = ttk.Button(
            button_frame,
            text="Gerar Reunião",
            bootstyle="success",
            padding=(20, 15)
        )
        gerar_btn.pack(anchor=CENTER)
        
        # Frame para loading (sempre presente, mas inicialmente vazio)
        loading_frame = ttk.Frame(main_container)
        # Criar elementos do loading (inicialmente não empacotados)
        loading_label = ttk.Label(
            loading_frame,
            text="Gerando documento... Por favor, aguarde.",
            font=("Helvetica", 14, "bold"),
            bootstyle="info"
        )
        
        # Progressbar indeterminado para efeito de loading
        loading_progress = ttk.Progressbar(
            loading_frame,
            mode='indeterminate',
            bootstyle="info-striped",
            length=400
        )
        
        def mostrar_loading():
            """Mostra o indicador de loading"""
            # Desabilitar botão primeiro
            gerar_btn.configure(state="disabled")
            # Remover temporariamente o button_frame para inserir o loading
            button_frame.pack_forget()
            # Empacotar elementos do loading no frame
            loading_label.pack(pady=(15, 10))
            loading_progress.pack(pady=(0, 15))
            # Mostrar o frame de loading
            loading_frame.pack(fill=X, pady=(20, 0))
            # Recolocar o button_frame após o loading
            button_frame.pack(fill=X, pady=(10, 0))
            # Iniciar animação do progressbar
            loading_progress.start(10)
            # Forçar atualização imediata da interface
            quadro_de_anuncio.update_idletasks()
            quadro_de_anuncio.update()
        
        def esconder_loading():
            """Esconde o indicador de loading"""
            loading_progress.stop()  # Para animação do progressbar
            # Remover elementos do loading
            loading_label.pack_forget()
            loading_progress.pack_forget()
            # Esconder o frame de loading
            loading_frame.pack_forget()
            gerar_btn.configure(state="normal")
            # Forçar atualização da interface
            quadro_de_anuncio.update_idletasks()
            quadro_de_anuncio.update()
        
        def processar_geracao(url, nome_arquivo, idioma, utilizarBase, qtdSemanas):
            """Executa a geração em thread separada"""
            try:
                print(url, nome_arquivo, idioma, utilizarBase)
                
                # Executar a geração
                s140.s140.gerar_s140(url, nome_arquivo, idioma, utilizarBase, qtdSemanas)
                
                # Esconder loading e mostrar sucesso
                quadro_de_anuncio.after(0, esconder_loading)
                quadro_de_anuncio.after(0, lambda: Messagebox.show_info(
                    "Documento gerado com sucesso!",
                    "Sucesso"
                ))
                
            except Exception as e:
                # Esconder loading e mostrar erro
                quadro_de_anuncio.after(0, esconder_loading)
                quadro_de_anuncio.after(0, lambda: Messagebox.show_error(
                    f"Erro ao gerar documento:\n{str(e)}",
                    "Erro"
                ))
                logger.error(f"Erro ao gerar reunião: {str(e)}")
        
        def enviar():
            """Inicia o processo de geração em thread separada"""
            # Validar campos obrigatórios
            if not entry_url.get().strip():
                Messagebox.show_warning("Por favor, preencha a URL.", "Campo Obrigatório")
                return
            if not entry_nome.get().strip():
                Messagebox.show_warning("Por favor, preencha o nome do arquivo.", "Campo Obrigatório")
                return
            try:
                qtd = int(entry_qtdSemanas.get())
                if qtd <= 0:
                    Messagebox.show_warning("A quantidade de semanas deve ser maior que zero.", "Valor Inválido")
                    return
            except ValueError:
                Messagebox.show_warning("Por favor, insira um número válido para a quantidade de semanas.", "Valor Inválido")
                return
            
            # Pegar os dados antes de iniciar a thread
            url = entry_url.get()
            nome_arquivo = entry_nome.get()
            idioma = variavel.get()
            utilizarBase = utilizar_base_var.get()
            qtdSemanas = int(entry_qtdSemanas.get())
            
            # Mostrar loading imediatamente (antes de iniciar a thread)
            print("Mostrando loading...")
            mostrar_loading()
            print("Loading mostrado")
            
            # Executar em thread separada
            thread = threading.Thread(target=processar_geracao, args=(url, nome_arquivo, idioma, utilizarBase, qtdSemanas), daemon=True)
            thread.start()
            print("Thread iniciada")
        
        gerar_btn.configure(command=enviar)
        
        # Botão de voltar
        voltar_btn = ttk.Button(
            main_container,
            text="Voltar",
            command=quadro_de_anuncio.destroy,
            bootstyle="secondary",
            width=15
        )
        voltar_btn.pack(side=BOTTOM, pady=(20, 0))
        
        # Centralizar a janela
        quadro_de_anuncio.update_idletasks()
        width = quadro_de_anuncio.winfo_width()
        height = quadro_de_anuncio.winfo_height()
        x = (quadro_de_anuncio.winfo_screenwidth() // 2) - (width // 2)
        y = (quadro_de_anuncio.winfo_screenheight() // 2) - (height // 2)
        quadro_de_anuncio.geometry(f"{width}x{height}+{x}+{y}")

    def historico_publicadores(self):
        # Configuração da janela
        historico_pub_window = ttk.Toplevel(self.root)
        historico_pub_window.title("Histórico de Publicadores")
        historico_pub_window.geometry("1024x768")
        
        # Container principal
        main_container = ttk.Frame(historico_pub_window, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Título
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="Histórico de Publicadores",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # Frame de busca e filtros
        search_frame = ttk.Frame(main_container)
        search_frame.pack(fill=X, pady=(0, 20))
        
        # Campo de busca
        ttk.Label(
            search_frame,
            text="Buscar publicador:",
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(0, 10))
        
        search_var = ttk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=search_var,
            width=40,
            bootstyle="primary"
        )
        search_entry.pack(side=LEFT, padx=(0, 20))
        
        # Frame para a tabela
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill=BOTH, expand=YES)
        
        # Criar Treeview
        colunas = ("nome", "batizado", "ultima_parte", "detalhes")
        tree = ttk.Treeview(
            table_frame,
            columns=colunas,
            show="headings",
            bootstyle="primary",
            height=20
        )
        
        # Configurar colunas
        tree.heading("nome", text="Nome", anchor=CENTER)
        tree.heading("batizado", text="Batizado", anchor=CENTER)
        tree.heading("ultima_parte", text="Última Parte", anchor=CENTER)
        tree.heading("detalhes", text="Detalhes", anchor=CENTER)
        
        # Configurar largura das colunas
        tree.column("nome", width=300, anchor=CENTER)
        tree.column("batizado", width=100, anchor=CENTER)
        tree.column("ultima_parte", width=300, anchor=CENTER)
        tree.column("detalhes", width=100, anchor=CENTER)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview,
            bootstyle="primary-round"
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(fill=BOTH, expand=YES)
        
        def mostrar_detalhes_publicador(item):
            # Obter dados do publicador selecionado
            valores = tree.item(item)['values']
            nome_publicador = valores[0]
            
            # Criar janela de detalhes
            detalhes_window = ttk.Toplevel(historico_pub_window)
            detalhes_window.title(f"Detalhes do Publicador - {nome_publicador}")
            detalhes_window.geometry("800x600")
            
            # Container principal
            detalhes_container = ttk.Frame(detalhes_window, padding=20)
            detalhes_container.pack(fill=BOTH, expand=YES)
            
            # Título
            ttk.Label(
                detalhes_container,
                text=f"Histórico de Partes - {nome_publicador}",
                font=("Helvetica", 16, "bold"),
                bootstyle="primary"
            ).pack(pady=(0, 20))
            
            # Frame para a tabela de detalhes
            detalhes_table_frame = ttk.Frame(detalhes_container)
            detalhes_table_frame.pack(fill=BOTH, expand=YES)
            
            # Criar Treeview para detalhes
            detalhes_tree = ttk.Treeview(
                detalhes_table_frame,
                columns=("data", "parte"),
                show="headings",
                bootstyle="primary",
                height=15
            )
            
            # Configurar colunas
            detalhes_tree.heading("data", text="Data", anchor=CENTER)
            detalhes_tree.heading("parte", text="Parte", anchor=CENTER)
            
            # Configurar largura das colunas
            detalhes_tree.column("data", width=300, anchor=W)
            detalhes_tree.column("parte", width=400, anchor=W)
            
            # Adicionar scrollbar
            detalhes_scrollbar = ttk.Scrollbar(
                detalhes_table_frame,
                orient="vertical",
                command=detalhes_tree.yview,
                bootstyle="primary-round"
            )
            detalhes_scrollbar.pack(side=RIGHT, fill=Y)
            detalhes_tree.configure(yscrollcommand=detalhes_scrollbar.set)
            detalhes_tree.pack(fill=BOTH, expand=YES, padx=(0, 10))
            
            try:
                from database import db_ops
                # Buscar histórico do publicador
                historico = db_ops.buscar_historico_publicador(nome_publicador)
                
                if historico:
                    # Ordenar histórico por data (mais recente primeiro)
                    historico_ordenado = sorted(historico, key=lambda x: x['data'], reverse=True)
                    
                    # Inserir dados na tabela com cores alternadas
                    for i, registro in enumerate(historico_ordenado):
                        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                        detalhes_tree.insert("", END, values=(
                            registro['data'],
                            registro['parte']
                        ), tags=(tag,))
                    
                    # Configurar cores alternadas
                    detalhes_tree.tag_configure('evenrow', background='#f0f0f0')
                    detalhes_tree.tag_configure('oddrow', background='white')
                else:
                    detalhes_tree.insert("", END, values=(
                        "Nenhum histórico encontrado",
                        ""
                    ))
            
            except Exception as e:
                logger.error(f"Erro ao carregar histórico do publicador: {str(e)}")
                detalhes_tree.insert("", END, values=(
                    f"Erro ao carregar histórico: {str(e)}",
                    ""
                ))
            
            # Botão de voltar
            ttk.Button(
                detalhes_container,
                text="Voltar",
                command=detalhes_window.destroy,
                bootstyle="secondary",
                width=15
            ).pack(side=BOTTOM, pady=(20, 0))
            
            # Centralizar a janela
            detalhes_window.update_idletasks()
            width = detalhes_window.winfo_width()
            height = detalhes_window.winfo_height()
            x = (detalhes_window.winfo_screenwidth() // 2) - (width // 2)
            y = (detalhes_window.winfo_screenheight() // 2) - (height // 2)
            detalhes_window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Tornar a janela modal
            detalhes_window.transient(historico_pub_window)
            detalhes_window.grab_set()
        
        def carregar_publicadores():
            # Limpar tabela
            for item in tree.get_children():
                tree.delete(item)
            
            try:
                # Buscar publicadores
                from database import db_ops
                publicadores = db_ops.getAllPub()
                
                # Filtrar por busca
                termo_busca = search_var.get().lower()
                if termo_busca:
                    publicadores = [p for p in publicadores if termo_busca in p['nome'].lower()]
                
                if not publicadores:
                    tree.insert("", END, values=("Nenhum publicador encontrado", "", "", ""))
                    return
                
                # Ordenar por nome
                publicadores.sort(key=lambda x: x['nome'].lower())
                
                # Adicionar publicadores na tabela
                for i, pub in enumerate(publicadores):
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    tree.insert("", END, values=(
                        pub['nome'],
                        "Sim" if pub.get('batizado', False) else "Não",
                        pub.get('ultima_parte', 'N/A'),
                        "↗"  # Ícone de seta diagonal para cima
                    ), tags=(tag,))
                
                # Configurar cores alternadas
                tree.tag_configure('evenrow', background='#f0f0f0')
                tree.tag_configure('oddrow', background='white')
            
            except Exception as e:
                logger.error(f"Erro ao carregar publicadores: {str(e)}")
                tree.insert("", END, values=(
                    f"Erro ao carregar publicadores: {str(e)}",
                    "",
                    "",
                    ""
                ))
        
        # Configurar evento de clique na linha
        def on_tree_click(event):
            item = tree.identify_row(event.y)
            if item:
                mostrar_detalhes_publicador(item)
        
        tree.bind("<ButtonRelease-1>", on_tree_click)
        
        # Configurar busca
        search_var.trace("w", lambda *args: carregar_publicadores())
        
        # Botão de voltar
        ttk.Button(
            main_container,
            text="Voltar",
            command=historico_pub_window.destroy,
            bootstyle="secondary",
            width=15
        ).pack(side=BOTTOM, pady=(20, 0))
        
        # Carregar dados iniciais
        carregar_publicadores()
        
        # Centralizar a janela
        historico_pub_window.update_idletasks()
        width = historico_pub_window.winfo_width()
        height = historico_pub_window.winfo_height()
        x = (historico_pub_window.winfo_screenwidth() // 2) - (width // 2)
        y = (historico_pub_window.winfo_screenheight() // 2) - (height // 2)
        historico_pub_window.geometry(f"{width}x{height}+{x}+{y}")

    def dashboards(self):
        # Criar janela de dashboards
        dashboards_window = ttk.Toplevel(self.root)
        dashboards_window.title("Dashboards")
        dashboards_window.geometry("1000x600")
        
        # Container principal
        main_container = ttk.Frame(dashboards_window, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Título
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="Dashboards",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # Menu de navegação
        menu_frame = ttk.Frame(main_container)
        menu_frame.pack(fill=X, pady=(0, 20))
        
        # Variável para controlar o dashboard atual
        current_dashboard = ttk.StringVar(value="participacoes")
        
        # Botões do menu
        ttk.Button(
            menu_frame,
            text="Participações por Publicador",
            command=lambda: current_dashboard.set("participacoes"),
            bootstyle="primary-outline",
            width=25
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            menu_frame,
            text="Participações por Reunião",
            command=lambda: current_dashboard.set("reunioes"),
            bootstyle="primary-outline",
            width=25
        ).pack(side=LEFT, padx=5)
        
        # Frame para filtro de parte (apenas para dashboard de participações)
        filtro_frame = ttk.Frame(main_container)
        # Não empacotar inicialmente, será mostrado apenas quando necessário
        
        # Lista de partes disponíveis
        partes_disponiveis = [
            "Todas as Partes",
            "Todas as Partes Menos Oração",
            "Presidente",
            "Oração Inicial",
            "Tesouro",
            "Joias Espirituais",
            "Leitura da Bíblia",
            "Escola - Primeira Parte",
            "Escola - Segunda Parte",
            "Escola - Terceira Parte",
            "Escola - Quarta Parte",
            "Nossa Vida Cristã - Primeira Parte",
            "Nossa Vida Cristã - Segunda Parte",
            "Estudo de Congregação",
            "Oração Final"
        ]
        
        # Variável para controlar a parte selecionada
        parte_selecionada = ttk.StringVar(value="Todas as Partes")
        
        # Label e combobox para filtro de parte
        ttk.Label(
            filtro_frame,
            text="Filtrar por Parte:",
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(0, 10))
        
        parte_combo = ttk.Combobox(
            filtro_frame,
            textvariable=parte_selecionada,
            values=partes_disponiveis,
            width=30,
            state="readonly",
            bootstyle="primary"
        )
        parte_combo.pack(side=LEFT, padx=(0, 10))
        
        # Frame para os gráficos
        graphs_frame = ttk.Frame(main_container)
        graphs_frame.pack(fill=BOTH, expand=YES)
        
        # Importar matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib
        matplotlib.use('TkAgg')
        
        def atualizar_grafico(*args):
            # Mostrar/ocultar filtro de parte baseado no dashboard selecionado
            if current_dashboard.get() == "participacoes":
                filtro_frame.pack(fill=X, pady=(0, 10), before=graphs_frame)
            else:
                filtro_frame.pack_forget()
            
            # Limpar frame de gráficos
            for widget in graphs_frame.winfo_children():
                widget.destroy()
            
            # Criar nova figura
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if current_dashboard.get() == "participacoes":
                # Obter filtro de parte selecionado
                parte_filtro = parte_selecionada.get()
                
                # Tratar opções especiais
                if parte_filtro == "Todas as Partes":
                    parte_para_busca = None
                elif parte_filtro == "Todas as Partes Menos Oração":
                    parte_para_busca = "__EXCLUIR_ORACOES__"
                else:
                    parte_para_busca = parte_filtro
                
                # Obter dados usando o novo método
                db = DatabaseOperations()
                participacoes_dict = db.contar_participacoes_por_parte(parte=parte_para_busca)
                
                if not participacoes_dict:
                    ax.text(0.5, 0.5, "Nenhuma participação encontrada", 
                            ha='center', va='center', fontsize=14, color='gray',
                            transform=ax.transAxes)
                    plt.tight_layout()
                    canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
                    return
                
                # Limitar aos top 20 publicadores para melhor visualização
                top_publicadores = list(participacoes_dict.items())[:20]
                
                # Separar dados
                nomes = [d[0] for d in top_publicadores]
                participacoes = [d[1] for d in top_publicadores]
                
                # Criar gráfico de barras
                bars = ax.barh(nomes, participacoes)
                
                # Adicionar valores nas barras
                for i, (bar, valor) in enumerate(zip(bars, participacoes)):
                    ax.text(valor, i, f' {valor}', va='center', fontsize=9)
                
                # Configurar o gráfico
                titulo = f'Participações por Publicador'
                if parte_filtro != "Todas as Partes":
                    titulo += f' - {parte_filtro}'
                ax.set_title(titulo, fontsize=12, fontweight='bold')
                ax.set_xlabel('Número de Participações')
                ax.set_ylabel('Publicadores')
                ax.invert_yaxis()  # Inverter para mostrar o maior no topo
                plt.tight_layout()
            
            else:  # participacoes por reuniao
                # Obter dados das reuniões usando o novo método
                db = DatabaseOperations()
                total_reunioes, participacoes_unicas = db.contar_participacoes_unicas_por_reuniao()
                
                # Se não houver dados, mostrar mensagem
                if not participacoes_unicas:
                    ax.text(0.5, 0.5, "Nenhum dado de participação encontrado", 
                            ha='center', va='center', fontsize=14, color='gray',
                            transform=ax.transAxes)
                    plt.tight_layout()
                    canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
                    return
                
                # Limitar aos top 20 publicadores para melhor visualização
                top_publicadores = list(participacoes_unicas.items())[:20]
                
                # Separar dados
                nomes = [d[0] for d in top_publicadores]
                participacoes = [d[1] for d in top_publicadores]
                
                # Criar gráfico de barras horizontal
                bars = ax.barh(nomes, participacoes)
                
                # Adicionar valores nas barras
                for i, (bar, valor) in enumerate(zip(bars, participacoes)):
                    ax.text(valor, i, f' {valor}', va='center', fontsize=9)
                
                # Adicionar texto com total de reuniões no topo do gráfico
                ax.text(0.02, 0.98, f'Total de Reuniões: {total_reunioes}', 
                        transform=ax.transAxes, fontsize=12, fontweight='bold',
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                
                # Configurar o gráfico
                ax.set_title('Participações Únicas por Reunião - Top Publicadores', 
                            fontsize=12, fontweight='bold')
                ax.set_xlabel('Número de Reuniões Participadas')
                ax.set_ylabel('Publicadores')
                ax.invert_yaxis()  # Inverter para mostrar o maior no topo
                plt.tight_layout()
            
            # Ajustar layout
            plt.tight_layout()
            
            # Criar canvas para exibir o gráfico
            canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        
        # Configurar trace para atualizar o gráfico quando mudar o dashboard ou a parte
        current_dashboard.trace_add("write", atualizar_grafico)
        parte_selecionada.trace_add("write", atualizar_grafico)
        
        # Carregar o gráfico inicial
        atualizar_grafico()
        
        # Botão de voltar
        ttk.Button(
            main_container,
            text="Voltar",
            command=dashboards_window.destroy,
            bootstyle="secondary",
            width=15
        ).pack(side=BOTTOM, pady=(20, 0))

if __name__ == "__main__":
    try:
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Criar janela principal com tema
        root = ttk.Window(themename="litera")
        root.title("JW Mural")
        
        # Configurar geometria da janela principal
        window_width = 1024
        window_height = 768
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Criar aplicação
        app = ModernApp(root)
        
        # Forçar atualização da janela principal
        root.update_idletasks()
        root.deiconify()
        root.update()
        
        # Função para iniciar as verificações após a janela principal estar visível
        def start_checks():
            if not initialize_application(root):
                Messagebox.show_error(
                    "Não foi possível inicializar o sistema. Verifique os logs para mais detalhes.",
                    "Erro de Inicialização"
                )
                root.quit()
                sys.exit(1)
        
        # Agendar a inicialização para acontecer após a janela principal estar pronta
        root.after(100, start_checks)
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Erro ao iniciar a aplicação: {str(e)}")
        Messagebox.show_error(
            f"Ocorreu um erro ao iniciar a aplicação:\n{str(e)}",
            "Erro Fatal"
        )
        sys.exit(1)
