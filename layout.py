import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
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
        tree.heading("data", text="Data da Reunião", anchor=CENTER)
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
            semana_ano = valores[2]  # "Semana X/YYYY"
            
            # Extrair ano
            ano = int(semana_ano.split('/')[1])
            # A semana agora é a data formatada
            semana = data.upper()  # Convertendo para maiúsculo para garantir consistência
            
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
                # Buscar reuniões
                from database import db_ops
                reunioes = db_ops.listar_reunioes(
                    ano=int(ano) if ano else None,
                    limite=100,
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
                    
                    # Formatar data
                    data_formatada = f"{data_inicio.day} de {data_inicio.strftime('%B').lower()} a {data_fim.day} de {data_fim.strftime('%B').lower()}"
                    
                    # Verificar filtro de mês
                    if mes and data_inicio.strftime("%B").lower() != mes.lower():
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
        def enviar():
            # pegue os dados inseridos pelo usuário e envie para o back-end
            url = entry_url.get()
            nome_arquivo = entry_nome.get()
            idioma = variavel.get()
            utilizarBase = utilizar_base_var.get()
            qtdSemanas = int(entry_qtdSemanas.get())
            print(url, nome_arquivo, idioma, utilizarBase)
            s140.s140.gerar_s140(url, nome_arquivo, idioma, utilizarBase, qtdSemanas)
            
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
        
        ttk.Button(
            button_frame,
            text="Gerar Reunião",
            command=enviar,
            bootstyle="success",
            padding=(20, 15)
        ).pack(anchor=CENTER)
        
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
        
        # Frame para os gráficos
        graphs_frame = ttk.Frame(main_container)
        graphs_frame.pack(fill=BOTH, expand=YES)
        
        # Importar matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib
        matplotlib.use('TkAgg')
        
        def atualizar_grafico(*args):
            # Limpar frame de gráficos
            for widget in graphs_frame.winfo_children():
                widget.destroy()
            
            # Criar nova figura
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if current_dashboard.get() == "participacoes":
                # Obter dados dos publicadores
                db = DatabaseOperations()
                publicadores = db.getAllPub()
                
                # Preparar dados para o gráfico
                dados = []
                
                for pub in publicadores:
                    dados.append({
                        'nome': pub['nome'],
                        'participacoes': len(pub.get('historico', []))
                    })
                
                # Ordenar do maior para o menor
                dados.sort(key=lambda x: x['participacoes'], reverse=True)
                
                # Separar dados ordenados
                nomes = [d['nome'] for d in dados]
                participacoes = [d['participacoes'] for d in dados]
                
                # Criar gráfico de barras
                bars = ax.bar(nomes, participacoes)
                
                # Configurar o gráfico
                ax.set_title('Número de Participações por Publicador')
                ax.set_xlabel('Publicadores')
                ax.set_ylabel('Número de Participações')
                plt.xticks(rotation=45, ha='right')
            
            else:  # participacoes por reuniao
                # Obter dados das reuniões diretamente do banco de dados
                db = DatabaseOperations()
                print("Iniciando contagem de participações por reunião...")
                participacoes_mensais = db.contar_reunioes_por_publicador()
                print(f"Participações mensais obtidas: {len(participacoes_mensais)} publicadores encontrados")
                
                # Se não houver dados, mostrar mensagem
                if not participacoes_mensais:
                    print("Nenhuma participação encontrada!")
                    ax.text(0.5, 0.5, "Nenhum dado de participação encontrado", 
                            ha='center', va='center', fontsize=14, color='gray',
                            transform=ax.transAxes)
                    plt.tight_layout()
                    canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
                    return
                
                # Vamos imprimir os primeiros itens para debug
                print("Amostra de dados obtidos:")
                for i, (nome, meses) in enumerate(list(participacoes_mensais.items())[:3]):
                    print(f"Publicador: {nome}, Meses: {meses}")
                
                # Agregar todos os meses
                total_participacoes = {}
                for nome, meses in participacoes_mensais.items():
                    total_participacoes[nome] = sum(meses.values())
                
                # Obter os 10 publicadores com mais participações
                top_publicadores = sorted(
                    total_participacoes.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                
                print(f"Top 10 publicadores: {top_publicadores}")
                
                # Lista de todos os meses (ordenados cronologicamente)
                todos_meses = set()
                for nome, meses in participacoes_mensais.items():
                    todos_meses.update(meses.keys())
                
                print(f"Meses encontrados: {todos_meses}")
                
                # Ordenar meses (formato MM/AAAA)
                try:
                    meses_ordenados = sorted(
                        todos_meses,
                        key=lambda x: (
                            # Se for no formato MM/AAAA
                            int(x.split('/')[1]) * 100 + int(x.split('/')[0]) 
                            if '/' in x and x.split('/')[0].isdigit() and x.split('/')[1].isdigit()
                            # Caso contrário, ordenar como string
                            else 0
                        )
                    )
                    print(f"Meses ordenados: {meses_ordenados}")
                except Exception as e:
                    print(f"Erro ao ordenar meses: {e}")
                    print(f"Meses problemáticos: {todos_meses}")
                    # Fallback: usar os meses sem ordenação
                    meses_ordenados = list(todos_meses)
                
                # Criar gráfico agrupado por mês para os top 10 publicadores
                largura_barra = 0.08  # Ajustar conforme necessário
                indices = range(len(meses_ordenados))
                
                try:
                    # Criar uma barra para cada publicador em cada mês
                    for i, (nome, _) in enumerate(top_publicadores):
                        valores = []
                        for mes in meses_ordenados:
                            # Obter o número de reuniões que o publicador participou neste mês
                            valores.append(participacoes_mensais.get(nome, {}).get(mes, 0))
                        
                        # Posições das barras
                        posicoes = [idx + i * largura_barra for idx in indices]
                        
                        # Criar barras
                        ax.bar(
                            posicoes,
                            valores,
                            largura_barra,
                            label=nome
                        )
                    
                    # Configurar eixos
                    ax.set_xticks([idx + (len(top_publicadores) - 1) * largura_barra / 2 for idx in indices])
                    ax.set_xticklabels(meses_ordenados, rotation=45, ha='right')
                    
                    # Configurar o gráfico
                    ax.set_title('Participações em Reuniões por Mês - Top 10 Publicadores')
                    ax.set_xlabel('Mês')
                    ax.set_ylabel('Número de Reuniões')
                    ax.legend(fontsize='small')
                    
                    print("Gráfico criado com sucesso!")
                except Exception as e:
                    print(f"Erro ao criar gráfico: {e}")
                    ax.text(0.5, 0.5, f"Erro ao criar gráfico: {str(e)}", 
                            ha='center', va='center', fontsize=12, color='red',
                            transform=ax.transAxes)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Criar canvas para exibir o gráfico
            canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        
        # Configurar trace para atualizar o gráfico quando mudar o dashboard
        current_dashboard.trace_add("write", atualizar_grafico)
        
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
