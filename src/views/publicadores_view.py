"""publicadores, historico_publicadores

Tela extraída de layout.py (SDD 03) — mixin de ModernApp.
Código movido verbatim; `self` e navegação inalterados.
"""
from views._shared import *  # noqa: F401,F403


class PublicadoresMixin:
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
        search_entry.pack(side=LEFT, expand=YES, fill=X, padx=(0, 10))
        
        # Frame para filtros de Ancião e Servo Ministerial
        filtros_frame = ttk.LabelFrame(main_container, text="Filtros", padding=10)
        filtros_frame.pack(fill=X, pady=(0, 10))
        
        # Variáveis para os filtros
        filtrar_anciao_var = ttk.BooleanVar()
        filtrar_servo_var = ttk.BooleanVar()
        
        # Checkboxes para filtros
        ttk.Checkbutton(
            filtros_frame,
            text="Ancião",
            variable=filtrar_anciao_var,
            bootstyle="primary-round-toggle"
        ).pack(side=LEFT, padx=(0, 20))
        
        ttk.Checkbutton(
            filtros_frame,
            text="Servo Ministerial",
            variable=filtrar_servo_var,
            bootstyle="primary-round-toggle"
        ).pack(side=LEFT, padx=(0, 20))
        
        # Botão para limpar filtros
        ttk.Button(
            filtros_frame,
            text="Limpar Filtros",
            command=lambda: [filtrar_anciao_var.set(False), filtrar_servo_var.set(False), atualizar_lista()],
            bootstyle="secondary-outline",
            width=15
        ).pack(side=LEFT)
        
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
            ).grid(row=1, column=0, columnspan=2, pady=10, sticky="w")
            
            # Sexo
            ttk.Label(
                fields_frame,
                text="Sexo:",
                font=("Helvetica", 12),
                bootstyle="secondary"
            ).grid(row=2, column=0, padx=(0, 10), pady=10, sticky="w")
            
            sexo_var = ttk.StringVar(value="Masculino")
            sexo_combo = ttk.Combobox(
                fields_frame,
                textvariable=sexo_var,
                values=["Masculino", "Feminino"],
                width=20,
                state="readonly",
                bootstyle="primary"
            )
            sexo_combo.grid(row=2, column=1, sticky="w", pady=10)
            
            # Frame para permissões
            permissoes_frame = ttk.LabelFrame(fields_frame, text="Permissões", padding=10)
            permissoes_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
            
            # Variáveis para permissões
            permissao_escola_var = ttk.BooleanVar(value=True)
            permissao_oracao_var = ttk.BooleanVar(value=True)
            permissao_leitura_var = ttk.BooleanVar(value=True)
            permissao_leitura_sentinela_var = ttk.BooleanVar(value=False)
            permissao_presidente_final_semana_var = ttk.BooleanVar(value=False)
            permissao_audio_video_var = ttk.BooleanVar(value=False)
            permissao_indicador_var = ttk.BooleanVar(value=False)
            permissao_microfone_var = ttk.BooleanVar(value=False)

            # Linha 1: permissões gerais
            add_perm_linha1 = ttk.Frame(permissoes_frame)
            add_perm_linha1.pack(fill=X)

            ttk.Checkbutton(
                add_perm_linha1,
                text="Parte da Escola",
                variable=permissao_escola_var,
                bootstyle="primary-round-toggle"
            ).pack(side=LEFT, padx=(0, 12))

            ttk.Checkbutton(
                add_perm_linha1,
                text="Oração",
                variable=permissao_oracao_var,
                bootstyle="primary-round-toggle"
            ).pack(side=LEFT, padx=(0, 12))

            ttk.Checkbutton(
                add_perm_linha1,
                text="Leitura do Livro",
                variable=permissao_leitura_var,
                bootstyle="primary-round-toggle"
            ).pack(side=LEFT, padx=(0, 12))

            ttk.Checkbutton(
                add_perm_linha1,
                text="Leitura da Sentinela",
                variable=permissao_leitura_sentinela_var,
                bootstyle="primary-round-toggle"
            ).pack(side=LEFT, padx=(0, 12))

            ttk.Checkbutton(
                add_perm_linha1,
                text="Presidente Final de Semana",
                variable=permissao_presidente_final_semana_var,
                bootstyle="primary-round-toggle"
            ).pack(side=LEFT)

            # Linha 2: permissões de salão
            add_perm_linha2 = ttk.Frame(permissoes_frame)
            add_perm_linha2.pack(fill=X, pady=(8, 0))

            ttk.Label(
                add_perm_linha2,
                text="Salão:",
                font=("Helvetica", 10),
                bootstyle="secondary"
            ).pack(side=LEFT, padx=(0, 8))

            ttk.Checkbutton(
                add_perm_linha2,
                text="Áudio/Vídeo",
                variable=permissao_audio_video_var,
                bootstyle="primary-round-toggle"
            ).pack(side=LEFT, padx=(0, 12))

            ttk.Checkbutton(
                add_perm_linha2,
                text="Indicador",
                variable=permissao_indicador_var,
                bootstyle="primary-round-toggle"
            ).pack(side=LEFT, padx=(0, 12))

            ttk.Checkbutton(
                add_perm_linha2,
                text="Microfone",
                variable=permissao_microfone_var,
                bootstyle="primary-round-toggle"
            ).pack(side=LEFT)
            
            # Frame do botão
            button_frame = ttk.Frame(modal_container)
            button_frame.pack(fill=X, pady=(20, 0))
            
            def adicionar_publicador():
                nome = nome_entry.get()
                batizado = batizado_var.get()
                sexo = sexo_var.get()
                permissoes = {
                    "parte_escola": permissao_escola_var.get(),
                    "oracao": permissao_oracao_var.get(),
                    "leitura_livro": permissao_leitura_var.get(),
                    "leitura_sentinela": permissao_leitura_sentinela_var.get(),
                    "presidente_final_semana": permissao_presidente_final_semana_var.get(),
                    "audio_video": permissao_audio_video_var.get(),
                    "indicador": permissao_indicador_var.get(),
                    "microfone": permissao_microfone_var.get()
                }
                if nome.strip():
                    publicador_service.adicionar(nome, batizado, sexo=sexo, permissoes=permissoes)
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
            largura_janela = 650
            altura_janela = 520
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
            columns=("nome", "batizado", "anciao", "servo_ministerial", "ultima_parte"),
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
        tabela.heading("anciao", text="Ancião", anchor=CENTER)
        tabela.heading("servo_ministerial", text="Servo Ministerial", anchor=CENTER)
        tabela.heading("ultima_parte", text="Última Parte", anchor=W)
        
        # Configurar largura e alinhamento das colunas
        tabela.column("nome", width=200, anchor=W)
        tabela.column("batizado", width=80, anchor=CENTER)
        tabela.column("anciao", width=80, anchor=CENTER)
        tabela.column("servo_ministerial", width=120, anchor=CENTER)
        tabela.column("ultima_parte", width=200, anchor=W)
        
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
                results = publicador_service.listar()
                
                # Filtra baseado na busca por nome
                termo_busca = search_var.get().lower()
                if termo_busca and termo_busca != "buscar publicador...":
                    results = [r for r in results if termo_busca in r["nome"].lower()]
                
                # Filtra por Ancião e/ou Servo Ministerial
                filtrar_anciao = filtrar_anciao_var.get()
                filtrar_servo = filtrar_servo_var.get()
                
                if filtrar_anciao and filtrar_servo:
                    # Se ambos estiverem marcados, mostrar quem é Ancião OU Servo Ministerial
                    results = [r for r in results if r.get("Anciao", False) or r.get("Servo_Ministerial", False)]
                elif filtrar_anciao:
                    # Se apenas Ancião estiver marcado
                    results = [r for r in results if r.get("Anciao", False)]
                elif filtrar_servo:
                    # Se apenas Servo Ministerial estiver marcado
                    results = [r for r in results if r.get("Servo_Ministerial", False)]
                
                # Ordenação
                results.sort(key=lambda x: x["nome"].lower())
                
                # Atualiza a tabela
                for i, result in enumerate(results):
                    row_tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
                    tabela.insert("", "end", values=(
                        result["nome"],
                        "Sim" if result.get("batizado", False) else "Não",
                        "Sim" if result.get("Anciao", False) else "Não",
                        "Sim" if result.get("Servo_Ministerial", False) else "Não",
                        result.get("ultima_parte", "N/A")
                    ), tags=row_tags)
                
                # Se não houver resultados, mostra uma mensagem na tabela
                if not results:
                    tabela.insert("", "end", values=("Nenhum publicador encontrado", "", "", "", ""))
            
            except Exception as e:
                print(f"Erro ao atualizar lista: {e}")
                tabela.insert("", "end", values=(f"Erro ao carregar publicadores: {str(e)}", "", "", "", ""))
        
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
                publicador = next((p for p in publicador_service.listar() if p["nome"] == selected_item['nome']), None)
                
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
                    ).grid(row=1, column=0, columnspan=2, pady=10, sticky="w")
                    
                    # Ancião
                    anciao_var = ttk.BooleanVar(value=publicador.get("Anciao", False))
                    ttk.Checkbutton(
                        fields_frame,
                        text="Ancião",
                        variable=anciao_var,
                        bootstyle="primary-round-toggle"
                    ).grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
                    
                    # Servo Ministerial
                    servo_ministerial_var = ttk.BooleanVar(value=publicador.get("Servo_Ministerial", False))
                    ttk.Checkbutton(
                        fields_frame,
                        text="Servo Ministerial",
                        variable=servo_ministerial_var,
                        bootstyle="primary-round-toggle"
                    ).grid(row=3, column=0, columnspan=2, pady=10, sticky="w")
                    
                    # Sexo
                    ttk.Label(
                        fields_frame,
                        text="Sexo:",
                        font=("Helvetica", 12),
                        bootstyle="secondary"
                    ).grid(row=4, column=0, padx=(0, 10), pady=10, sticky="w")
                    
                    sexo_var = ttk.StringVar(value=publicador.get("sexo", "Masculino"))
                    sexo_combo = ttk.Combobox(
                        fields_frame,
                        textvariable=sexo_var,
                        values=["Masculino", "Feminino"],
                        width=20,
                        state="readonly",
                        bootstyle="primary"
                    )
                    sexo_combo.grid(row=4, column=1, sticky="w", pady=10)
                    
                    # Frame para permissões
                    permissoes_frame = ttk.LabelFrame(fields_frame, text="Permissões", padding=10)
                    permissoes_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
                    
                    # Obter permissões do publicador ou usar valores padrão
                    permissoes_publicador = publicador.get("permissoes", {
                        "parte_escola": True,
                        "oracao": True,
                        "leitura_livro": True,
                        "leitura_sentinela": False,
                        "presidente_final_semana": False,
                        "audio_video": False,
                        "indicador": False,
                        "microfone": False
                    })

                    # Variáveis para permissões
                    permissao_escola_var = ttk.BooleanVar(value=permissoes_publicador.get("parte_escola", True))
                    permissao_oracao_var = ttk.BooleanVar(value=permissoes_publicador.get("oracao", True))
                    permissao_leitura_var = ttk.BooleanVar(value=permissoes_publicador.get("leitura_livro", True))
                    permissao_leitura_sentinela_var = ttk.BooleanVar(value=permissoes_publicador.get("leitura_sentinela", False))
                    permissao_presidente_final_semana_var = ttk.BooleanVar(value=permissoes_publicador.get("presidente_final_semana", False))
                    permissao_audio_video_var = ttk.BooleanVar(value=permissoes_publicador.get("audio_video", False))
                    permissao_indicador_var = ttk.BooleanVar(value=permissoes_publicador.get("indicador", False))
                    permissao_microfone_var = ttk.BooleanVar(value=permissoes_publicador.get("microfone", False))
                    
                    # Linha 1: permissões gerais
                    perm_linha1 = ttk.Frame(permissoes_frame)
                    perm_linha1.pack(fill=X)

                    ttk.Checkbutton(
                        perm_linha1,
                        text="Parte da Escola",
                        variable=permissao_escola_var,
                        bootstyle="primary-round-toggle"
                    ).pack(side=LEFT, padx=(0, 12))

                    ttk.Checkbutton(
                        perm_linha1,
                        text="Oração",
                        variable=permissao_oracao_var,
                        bootstyle="primary-round-toggle"
                    ).pack(side=LEFT, padx=(0, 12))

                    ttk.Checkbutton(
                        perm_linha1,
                        text="Leitura do Livro",
                        variable=permissao_leitura_var,
                        bootstyle="primary-round-toggle"
                    ).pack(side=LEFT, padx=(0, 12))

                    ttk.Checkbutton(
                        perm_linha1,
                        text="Leitura da Sentinela",
                        variable=permissao_leitura_sentinela_var,
                        bootstyle="primary-round-toggle"
                    ).pack(side=LEFT, padx=(0, 12))

                    ttk.Checkbutton(
                        perm_linha1,
                        text="Presidente Final de Semana",
                        variable=permissao_presidente_final_semana_var,
                        bootstyle="primary-round-toggle"
                    ).pack(side=LEFT)

                    # Linha 2: permissões de salão
                    perm_linha2 = ttk.Frame(permissoes_frame)
                    perm_linha2.pack(fill=X, pady=(8, 0))

                    ttk.Label(
                        perm_linha2,
                        text="Salão:",
                        font=("Helvetica", 10),
                        bootstyle="secondary"
                    ).pack(side=LEFT, padx=(0, 8))

                    ttk.Checkbutton(
                        perm_linha2,
                        text="Áudio/Vídeo",
                        variable=permissao_audio_video_var,
                        bootstyle="primary-round-toggle"
                    ).pack(side=LEFT, padx=(0, 12))

                    ttk.Checkbutton(
                        perm_linha2,
                        text="Indicador",
                        variable=permissao_indicador_var,
                        bootstyle="primary-round-toggle"
                    ).pack(side=LEFT, padx=(0, 12))

                    ttk.Checkbutton(
                        perm_linha2,
                        text="Microfone",
                        variable=permissao_microfone_var,
                        bootstyle="primary-round-toggle"
                    ).pack(side=LEFT)

                    # Última parte (somente leitura)
                    if "ultima_parte" in publicador:
                        ttk.Label(
                            fields_frame,
                            text="Última Parte:",
                            font=("Helvetica", 12),
                            bootstyle="secondary"
                        ).grid(row=6, column=0, padx=(0, 10), pady=10, sticky="w")
                        
                        ttk.Label(
                            fields_frame,
                            text=publicador.get("ultima_parte", "N/A"),
                            font=("Helvetica", 12),
                            bootstyle="primary"
                        ).grid(row=6, column=1, sticky="w", pady=10)
                    
                    # Botões
                    button_frame = ttk.Frame(edit_container)
                    button_frame.pack(fill=X, pady=(20, 0))
                    
                    def salvar_alteracoes():
                        novo_nome = nome_entry.get()
                        batizado = batizado_var.get()
                        anciao = anciao_var.get()
                        servo_ministerial = servo_ministerial_var.get()
                        sexo = sexo_var.get()
                        permissoes = {
                            "parte_escola": permissao_escola_var.get(),
                            "oracao": permissao_oracao_var.get(),
                            "leitura_livro": permissao_leitura_var.get(),
                            "leitura_sentinela": permissao_leitura_sentinela_var.get(),
                            "presidente_final_semana": permissao_presidente_final_semana_var.get(),
                            "audio_video": permissao_audio_video_var.get(),
                            "indicador": permissao_indicador_var.get(),
                            "microfone": permissao_microfone_var.get()
                        }
                        
                        if novo_nome.strip():
                            # Se o nome mudou, precisamos excluir o antigo e criar um novo
                            if novo_nome != selected_item['nome']:
                                # Buscar dados do publicador antigo para preservar histórico
                                publicador_antigo = next((p for p in publicador_service.listar() if p["nome"] == selected_item['nome']), None)
                                historico_antigo = publicador_antigo.get("historico", []) if publicador_antigo else []
                                ultima_parte_antiga = publicador_antigo.get("ultima_parte", "") if publicador_antigo else ""
                                
                                # Deletar o antigo
                                publicador_service.excluir(selected_item['nome'])
                                
                                # Criar novo com os dados atualizados
                                publicador_service.adicionar(novo_nome, batizado, sexo=sexo, permissoes=permissoes)
                                
                                # Atualizar campos adicionais e histórico
                                publicador_service.atualizar(novo_nome, batizado=batizado, anciao=anciao, servo_ministerial=servo_ministerial)
                                
                                # Restaurar histórico se houver
                                if historico_antigo or ultima_parte_antiga:
                                    try:
                                        publicador_service.restaurar_historico(
                                            novo_nome, historico_antigo, ultima_parte_antiga)
                                    except Exception as e:
                                        logger.error(f"Erro ao restaurar histórico: {str(e)}")
                            else:
                                # Atualizar todos os campos
                                publicador_service.atualizar(
                                    selected_item['nome'], 
                                    batizado=batizado, 
                                    anciao=anciao, 
                                    servo_ministerial=servo_ministerial,
                                    sexo=sexo,
                                    permissoes=permissoes
                                )
                            
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
                    largura_janela = 650
                    altura_janela = 620
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
                    publicador_service.excluir(selected_item['nome'])
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
                    resultado = publicador_service.resetar_todo_historico()
                    
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
        
        # Configurar campo de busca e filtros
        search_var.trace("w", lambda *args: atualizar_lista())
        filtrar_anciao_var.trace("w", lambda *args: atualizar_lista())
        filtrar_servo_var.trace("w", lambda *args: atualizar_lista())
        
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
                # Buscar histórico do publicador
                historico = publicador_service.buscar_historico(nome_publicador)
                
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
                publicadores = publicador_service.listar()
                
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

