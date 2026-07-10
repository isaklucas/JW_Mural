"""dashboards

Tela extraída de layout.py (SDD 03) — mixin de ModernApp.
Código movido verbatim; `self` e navegação inalterados.
"""
from views._shared import *  # noqa: F401,F403


class DashboardsMixin:
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

        ttk.Button(
            menu_frame,
            text="Designações Salão",
            command=lambda: current_dashboard.set("salao"),
            bootstyle="info-outline",
            width=20
        ).pack(side=LEFT, padx=5)

        # Frame para filtro de parte (apenas para dashboard de participações)
        filtro_frame = ttk.Frame(main_container)
        # Não empacotar inicialmente, será mostrado apenas quando necessário
        
        # Lista de partes disponíveis
        partes_disponiveis = [
            "Todas as Partes",
            "Todas as Partes Menos Oração",
            "Todas as Partes Menos Final de Semana",
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

            # Dashboard de Designações Salão (usa Treeview, não matplotlib)
            if current_dashboard.get() == "salao":
                filtro_frame.pack_forget()
                dados = dashboard_service.contar_designacoes_por_publicador()
                dados_sorted = sorted(dados.items(), key=lambda x: x[1]['total'], reverse=True)
                cols = ("nome", "audio", "video", "microfone", "indicadores", "total")
                tree_salao = ttk.Treeview(graphs_frame, columns=cols, show="headings",
                                          bootstyle="primary", height=18)
                tree_salao.heading("nome", text="Nome")
                tree_salao.heading("audio", text="Áudio")
                tree_salao.heading("video", text="Vídeo")
                tree_salao.heading("microfone", text="Microfone")
                tree_salao.heading("indicadores", text="Indicadores")
                tree_salao.heading("total", text="Total")
                tree_salao.column("nome", width=200, anchor=W)
                for c in ("audio", "video", "microfone", "indicadores", "total"):
                    tree_salao.column(c, width=90, anchor=CENTER)
                for nome, counts in dados_sorted:
                    tree_salao.insert("", "end", values=(
                        nome, counts['audio'], counts['video'],
                        counts['microfone'], counts['indicadores'], counts['total']
                    ))
                sb_salao = ttk.Scrollbar(graphs_frame, orient="vertical",
                                         command=tree_salao.yview, bootstyle="primary-round")
                sb_salao.pack(side=RIGHT, fill=Y)
                tree_salao.configure(yscrollcommand=sb_salao.set)
                tree_salao.pack(fill=BOTH, expand=YES)
                return

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
                elif parte_filtro == "Todas as Partes Menos Final de Semana":
                    parte_para_busca = "__EXCLUIR_FINAL_SEMANA__"
                else:
                    parte_para_busca = parte_filtro
                
                # Obter dados usando o novo método
                participacoes_dict = dashboard_service.contar_participacoes_por_parte(parte=parte_para_busca)
                
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
                total_reunioes, participacoes_unicas = dashboard_service.contar_participacoes_unicas_por_reuniao()
                
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

