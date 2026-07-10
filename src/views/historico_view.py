"""historico, historico_final_semana

Tela extraída de layout.py (SDD 03) — mixin de ModernApp.
Código movido verbatim; `self` e navegação inalterados.
"""
from views._shared import *  # noqa: F401,F403


class HistoricoMixin:
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
                # Buscar reunião usando semana e ano
                reuniao = reuniao_service.buscar(ano, semana)
                
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
                limite = 10000 if not ano and not mes else 100
                reunioes = reuniao_service.listar(
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
            publicadores = publicador_service.listar()
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
                    resultado = reuniao_service.salvar(dados_reuniao)
                    
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

    def historico_final_semana(self):
        """Exibe histórico de reuniões de final de semana."""
        hist_window = ttk.Toplevel(self.root)
        hist_window.title("Histórico Final de Semana")
        hist_window.geometry("900x600")
        
        main = ttk.Frame(hist_window, padding=20)
        main.pack(fill=BOTH, expand=YES)
        
        ttk.Label(main, text="Histórico de Reuniões Final de Semana", font=("Helvetica", 20, "bold"), bootstyle="primary").pack(pady=(0, 20))
        
        filtro_frame = ttk.Frame(main)
        filtro_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(filtro_frame, text="Ano:", bootstyle="secondary").pack(side=LEFT, padx=(0, 5))
        ano_var = ttk.StringVar(value=str(datetime.datetime.now().year))
        ano_combo = ttk.Combobox(filtro_frame, textvariable=ano_var, width=8, values=[str(y) for y in range(2020, 2031)])
        ano_combo.pack(side=LEFT, padx=(0, 15))
        ttk.Label(filtro_frame, text="Mês:", bootstyle="secondary").pack(side=LEFT, padx=(0, 5))
        mes_var = ttk.StringVar(value="")
        mes_combo = ttk.Combobox(filtro_frame, textvariable=mes_var, width=10, values=["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
        mes_combo.pack(side=LEFT, padx=(0, 10))
        
        tree_frame = ttk.Frame(main)
        tree_frame.pack(fill=BOTH, expand=YES, pady=(10, 0))
        columns = ("ano", "mes", "arquivo", "data")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        tree.heading("ano", text="Ano")
        tree.heading("mes", text="Mês")
        tree.heading("arquivo", text="Arquivo")
        tree.heading("data", text="Data Criação")
        tree.column("ano", width=80)
        tree.column("mes", width=80)
        tree.column("arquivo", width=300)
        tree.column("data", width=180)
        tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
        scroll.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=scroll.set)
        
        def mostrar_detalhes_final_semana(item):
            valores = tree.item(item)['values']
            if len(valores) < 2:
                return
            try:
                ano = int(valores[0])
                mes = int(valores[1])
            except (ValueError, TypeError):
                return
            reuniao = reuniao_service.buscar_final_semana(ano, mes)
            detalhes_window = ttk.Toplevel(hist_window)
            detalhes_window.title(f"Detalhes da Reunião - {valores[2]} ({ano}/{mes})")
            detalhes_window.geometry("650x450")
            det_main = ttk.Frame(detalhes_window, padding=20)
            det_main.pack(fill=BOTH, expand=YES)
            ttk.Label(det_main, text=f"Detalhes da Reunião - {valores[2]}", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=(0, 20))
            det_frame = ttk.Frame(det_main)
            det_frame.pack(fill=BOTH, expand=YES)
            det_tree = ttk.Treeview(det_frame, columns=("parte", "participante"), show="headings", bootstyle="primary", height=15)
            det_tree.heading("parte", text="Parte", anchor=CENTER)
            det_tree.heading("participante", text="Participante", anchor=CENTER)
            det_tree.column("parte", width=250, anchor=W)
            det_tree.column("participante", width=300, anchor=W)
            det_scroll = ttk.Scrollbar(det_frame, orient=VERTICAL, command=det_tree.yview, bootstyle="primary-round")
            det_scroll.pack(side=RIGHT, fill=Y)
            det_tree.configure(yscrollcommand=det_scroll.set)
            det_tree.pack(fill=BOTH, expand=YES, padx=(0, 10))
            if reuniao:
                if reuniao.get('dirigente'):
                    det_tree.insert("", END, values=("Dirigente de Sentinela", reuniao.get('dirigente')), tags=('evenrow',))
                if reuniao.get('semanas'):
                    meses_pt = {
                        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                    }
                    nome_mes = meses_pt.get(reuniao.get('mes'), str(reuniao.get('mes', '')))
                    ano_reuniao = reuniao.get('ano', '')
                    for i, semana in enumerate(reuniao['semanas']):
                        campo_semana = (semana.get('semana') or '').strip()
                        if campo_semana and len(campo_semana) <= 30 and " de " in campo_semana:
                            rotulo = campo_semana
                        else:
                            rotulo = f"Semana {i+1} de {nome_mes} de {ano_reuniao}"
                        detalhes = [
                            (f"{rotulo} - Título Estudo", semana.get('titulo_estudo', '')),
                            (f"{rotulo} - Tema Discurso", semana.get('tema_discurso', '')),
                            (f"{rotulo} - Orador", semana.get('orador', '')),
                            (f"{rotulo} - Presidente", semana.get('presidente', '')),
                            (f"{rotulo} - Leitor Sentinela", semana.get('leitor_sentinela', ''))
                        ]
                        for j, (parte, participante) in enumerate(detalhes):
                            if participante:
                                tag = 'evenrow' if (i * 5 + j) % 2 == 0 else 'oddrow'
                                det_tree.insert("", END, values=(parte, participante), tags=(tag,))
                    det_tree.tag_configure('evenrow', background='#f0f0f0')
                    det_tree.tag_configure('oddrow', background='white')
            if not reuniao or not reuniao.get('semanas'):
                ttk.Label(det_main, text="Nenhum detalhe encontrado para esta reunião.", bootstyle="danger").pack(pady=20)

            btn_frame = ttk.Frame(det_main)
            btn_frame.pack(side=BOTTOM, pady=(20, 0))

            def ao_excluir():
                r = Messagebox.yesno("Excluir esta reunião do histórico? As participações (Leitura Sentinela e Presidente) serão removidas do histórico de cada publicador.", title="Confirmar exclusão")
                if r != "Yes":
                    return
                resultado = reuniao_service.excluir_final_semana(ano, mes)
                if resultado.get("success"):
                    Messagebox.ok("Reunião excluída. O histórico dos publicadores foi atualizado.", title="Excluído")
                    detalhes_window.destroy()
                    carregar()
                else:
                    Messagebox.show_error(resultado.get("message", "Erro ao excluir."), title="Erro")

            def ao_editar():
                import copy
                semanas_copy = copy.deepcopy(reuniao.get("semanas", []))
                if not final_semana.FinalSemana.solicitar_dados_usuario(semanas_copy, parent=detalhes_window):
                    return
                reuniao_service.excluir_final_semana(ano, mes)
                nome_arquivo = reuniao.get("nome_arquivo", "")
                dirigente = reuniao.get("dirigente", "")
                dados = {
                    "ano": ano,
                    "mes": mes,
                    "nome_arquivo": nome_arquivo,
                    "dirigente": dirigente,
                    "semanas": semanas_copy,
                    "data_criacao": reuniao.get("data_criacao", ""),
                }
                reuniao_service.salvar_final_semana(dados)
                try:
                    final_semana.FinalSemana.criar_documento_sentinela(semanas_copy, nome_arquivo, dirigente)
                    final_semana.FinalSemana.criar_documento_oradores(semanas_copy, nome_arquivo)
                except Exception as ex:
                    logger.exception("Erro ao gerar documentos na edição")
                    Messagebox.show_warning(f"Reunião atualizada no banco, mas os documentos Word não foram gerados: {ex}", title="Aviso")
                else:
                    Messagebox.ok("Reunião atualizada. Documentos Sentinela e Oradores gerados em documentosCriados/.", title="Atualizado")
                detalhes_window.destroy()
                carregar()

            ttk.Button(btn_frame, text="Editar", command=ao_editar, bootstyle="info", width=12).pack(side=LEFT, padx=(0, 10))
            ttk.Button(btn_frame, text="Excluir", command=ao_excluir, bootstyle="danger", width=12).pack(side=LEFT, padx=(0, 10))
            ttk.Button(btn_frame, text="Voltar", command=detalhes_window.destroy, bootstyle="secondary", width=12).pack(side=LEFT)
            detalhes_window.update_idletasks()
            w, h = 650, 450
            x = (detalhes_window.winfo_screenwidth() // 2) - (w // 2)
            y = (detalhes_window.winfo_screenheight() // 2) - (h // 2)
            detalhes_window.geometry(f"{w}x{h}+{x}+{y}")
            detalhes_window.transient(hist_window)
            detalhes_window.grab_set()
        
        def on_tree_click(event):
            item = tree.identify_row(event.y)
            if item:
                mostrar_detalhes_final_semana(item)
        
        tree.bind("<ButtonRelease-1>", on_tree_click)
        
        def carregar():
            for item in tree.get_children():
                tree.delete(item)
            ano = int(ano_var.get()) if ano_var.get().isdigit() else None
            mes = int(mes_var.get()) if mes_var.get().isdigit() else None
            reunioes = reuniao_service.listar_final_semana(ano=ano, mes=mes, limite=100)
            for r in reunioes:
                data_criacao = r.get("data_criacao", "")[:19].replace("T", " ") if r.get("data_criacao") else ""
                tree.insert("", END, values=(r.get("ano", ""), r.get("mes", ""), r.get("nome_arquivo", ""), data_criacao))
        
        ttk.Button(main, text="Filtrar", command=carregar, bootstyle="primary").pack(pady=(10, 0))
        carregar()
        
        hist_window.update_idletasks()
        x = (hist_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (hist_window.winfo_screenheight() // 2) - (600 // 2)
        hist_window.geometry(f"900x600+{x}+{y}")

