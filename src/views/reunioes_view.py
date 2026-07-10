"""criar_quadro_de_anuncio, criar_reuniao_final_semana

Tela extraída de layout.py (SDD 03) — mixin de ModernApp.
Código movido verbatim; `self` e navegação inalterados.
"""
from views._shared import *  # noqa: F401,F403


class ReunioesMixin:
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
        fields_frame.pack(fill=X, pady=(0, 20))
        
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
        ).grid(row=4, column=0, columnspan=2, pady=10, sticky="w")
        
        # Checkbox para gerar com publicadores automaticamente
        gerar_com_publicadores_var = ttk.BooleanVar()
        ttk.Checkbutton(
            fields_frame,
            text="Gerar com Publicadores (Seleção Automática)",
            variable=gerar_com_publicadores_var,
            bootstyle="primary-round-toggle"
        ).grid(row=5, column=0, columnspan=2, pady=10, sticky="w")
        
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
        
        progress_var = tk.DoubleVar(value=0)
        loading_progress = ttk.Progressbar(
            loading_frame,
            mode='determinate',
            bootstyle="info-striped",
            length=400,
            maximum=100,
            variable=progress_var
        )
        status_label = ttk.Label(
            loading_frame,
            text="",
            font=("Helvetica", 10),
            bootstyle="secondary"
        )
        
        def mostrar_loading():
            gerar_btn.configure(state="disabled")
            button_frame.pack_forget()
            loading_label.pack(pady=(15, 5))
            progress_var.set(0)
            loading_progress.pack(pady=(0, 5))
            status_label.configure(text="Iniciando...")
            status_label.pack(pady=(0, 15))
            loading_frame.pack(fill=X, pady=(20, 0))
            button_frame.pack(fill=X, pady=(10, 0))
            quadro_de_anuncio.update_idletasks()
            quadro_de_anuncio.update()

        def esconder_loading():
            loading_label.pack_forget()
            loading_progress.pack_forget()
            status_label.pack_forget()
            loading_frame.pack_forget()
            gerar_btn.configure(state="normal")
            quadro_de_anuncio.update_idletasks()
            quadro_de_anuncio.update()
        
        def processar_geracao(url, nome_arquivo, idioma, utilizarBase, gerarComPublicadores, qtdSemanas):
            """Executa a geração em thread separada"""
            def atualizar_progresso(texto, valor):
                def _update(t=texto, v=valor):
                    progress_var.set(v)
                    status_label.configure(text=t)
                    quadro_de_anuncio.update_idletasks()
                quadro_de_anuncio.after(0, _update)

            try:
                print(url, nome_arquivo, idioma, utilizarBase, gerarComPublicadores)

                s140.s140.gerar_s140(url, nome_arquivo, idioma, utilizarBase, gerarComPublicadores, qtdSemanas, progress_cb=atualizar_progresso)
                
                # Esconder loading e mostrar sucesso
                quadro_de_anuncio.after(0, esconder_loading)
                quadro_de_anuncio.after(0, lambda: Messagebox.show_info(
                    "Documento gerado com sucesso!",
                    "Sucesso"
                ))
                
            except Exception as e:
                # Esconder loading e mostrar erro
                erro_msg = str(e)
                quadro_de_anuncio.after(0, esconder_loading)
                quadro_de_anuncio.after(0, lambda: Messagebox.show_error(
                    f"Erro ao gerar documento:\n{erro_msg}",
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
            gerarComPublicadores = gerar_com_publicadores_var.get()
            qtdSemanas = int(entry_qtdSemanas.get())
            
            # Validar: se gerar com publicadores, deve estar marcado "utilizar base"
            if gerarComPublicadores and not utilizarBase:
                Messagebox.show_warning(
                    "Para usar 'Gerar com Publicadores', é necessário marcar 'Utilizar base de publicadores'.",
                    "Validação"
                )
                return
            
            # Mostrar loading imediatamente (antes de iniciar a thread)
            print("Mostrando loading...")
            mostrar_loading()
            print("Loading mostrado")
            
            # Executar em thread separada
            thread = threading.Thread(target=processar_geracao, args=(url, nome_arquivo, idioma, utilizarBase, gerarComPublicadores, qtdSemanas), daemon=True)
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
        
        # Centralizar a janela sem travar tamanho (janela cresce ao exibir loading)
        quadro_de_anuncio.update_idletasks()
        width = quadro_de_anuncio.winfo_reqwidth()
        height = quadro_de_anuncio.winfo_reqheight()
        x = (quadro_de_anuncio.winfo_screenwidth() // 2) - (width // 2)
        y = (quadro_de_anuncio.winfo_screenheight() // 2) - (height // 2)
        quadro_de_anuncio.geometry(f"+{x}+{y}")

    def criar_reuniao_final_semana(self):
        """Janela para criar reunião de final de semana."""
        janela = ttk.Toplevel(self.root)
        janela.title("Criar Reunião Final de Semana")
        janela.geometry("600x420")
        janela.grab_set()

        main_container = ttk.Frame(janela, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        ttk.Label(main_container, text="Criar Reunião Final de Semana", font=("Helvetica", 20, "bold"), bootstyle="primary").pack(pady=(0, 20))
        
        fields = ttk.Frame(main_container)
        fields.pack(fill=BOTH, expand=YES, pady=(0, 20))
        fields.grid_columnconfigure(1, weight=1)
        
        ttk.Label(fields, text="URL:", font=("Helvetica", 12), bootstyle="secondary").grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
        entry_url = ttk.Entry(fields, width=50, bootstyle="primary")
        entry_url.grid(row=0, column=1, sticky="ew", pady=10)
        entry_url.insert(0, "https://wol.jw.org/pt/wol/meetings/r5/lp-t/2026/6")
        
        ttk.Label(fields, text="Nome do Arquivo:", font=("Helvetica", 12), bootstyle="secondary").grid(row=1, column=0, padx=(0, 10), pady=10, sticky="w")
        entry_nome = ttk.Entry(fields, width=50, bootstyle="primary")
        entry_nome.grid(row=1, column=1, sticky="ew", pady=10)
        
        ttk.Label(fields, text="Idioma:", font=("Helvetica", 12), bootstyle="secondary").grid(row=2, column=0, padx=(0, 10), pady=10, sticky="w")
        idioma_var = ttk.StringVar(value="pt")
        ttk.Combobox(fields, textvariable=idioma_var, values=["pt"], state="readonly", width=10, bootstyle="primary").grid(row=2, column=1, sticky="w", pady=10)
        
        auto_presidente_var = ttk.BooleanVar()
        auto_leitor_var = ttk.BooleanVar()
        ttk.Checkbutton(fields, text="Seleção automática do Presidente", variable=auto_presidente_var, bootstyle="primary-round-toggle").grid(row=3, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Checkbutton(fields, text="Seleção automática do Leitor da Sentinela", variable=auto_leitor_var, bootstyle="primary-round-toggle").grid(row=4, column=0, columnspan=2, pady=5, sticky="w")
        
        loading_frame = ttk.Frame(main_container)
        loading_label = ttk.Label(loading_frame, text="Gerando documento...", font=("Helvetica", 14, "bold"), bootstyle="info")
        loading_progress = ttk.Progressbar(loading_frame, mode='indeterminate', bootstyle="info-striped", length=400)
        
        def processar():
            def cleanup():
                loading_progress.stop()
                loading_label.pack_forget()
                loading_progress.pack_forget()
                loading_frame.pack_forget()
                gerar_btn.configure(state="normal")

            def continuar_na_main_thread(semanas):
                """Executa modal dirigente, modal dados, geração dos dois docs e salvamento na thread principal."""
                try:
                    dirigente = final_semana.FinalSemana.solicitar_dirigente_sentinela(janela)
                    if dirigente is None:
                        cleanup()
                        return
                    if not final_semana.FinalSemana.solicitar_dados_usuario(semanas, parent=janela):
                        cleanup()
                        return
                    nome_base = entry_nome.get().strip()
                    final_semana.FinalSemana.criar_documento_sentinela(semanas, nome_base, dirigente)
                    final_semana.FinalSemana.criar_documento_oradores(semanas, nome_base)
                    final_semana.FinalSemana.salvar_historico_final_semana(semanas, nome_base, dirigente)
                    Messagebox.show_info("Documentos gerados com sucesso!", "Sucesso")
                except Exception as e:
                    Messagebox.show_error(f"Erro:\n{str(e)}", "Erro", parent=janela)
                    logger.error(f"Erro ao gerar final de semana: {str(e)}")
                finally:
                    cleanup()

            try:
                # Fase 1 (thread): scraping e seleção - sem GUI (9 semanas)
                semanas = final_semana.FinalSemana.buscar_titulos_meetings(entry_url.get().strip(), 9)
                if not semanas:
                    raise ValueError("Não foi possível extrair os títulos da Sentinela. Verifique a URL.")
                if auto_presidente_var.get():
                    final_semana.FinalSemana.selecionar_presidente_automaticamente(semanas)
                if auto_leitor_var.get():
                    final_semana.FinalSemana.selecionar_leitor_automaticamente(semanas)
                janela.after(0, lambda s=semanas: continuar_na_main_thread(s))
            except Exception as e:
                err_msg = str(e)
                janela.after(0, lambda m=err_msg: Messagebox.show_error(f"Erro:\n{m}", "Erro", parent=janela))
                logger.error(f"Erro ao gerar final de semana: {err_msg}")
                janela.after(0, cleanup)
        
        def enviar():
            if not entry_url.get().strip():
                Messagebox.show_warning("Preencha a URL.", "Campo Obrigatório", parent=janela)
                return
            if not entry_nome.get().strip():
                Messagebox.show_warning("Preencha o nome do arquivo.", "Campo Obrigatório", parent=janela)
                return
            gerar_btn.configure(state="disabled")
            loading_label.pack(pady=(15, 10))
            loading_progress.pack(pady=(0, 15))
            loading_frame.pack(fill=X, pady=(20, 0))
            loading_progress.start(10)
            janela.update_idletasks()
            threading.Thread(target=processar, daemon=True).start()
        
        gerar_btn = ttk.Button(main_container, text="Gerar Reunião", bootstyle="success", padding=(20, 15), command=enviar)
        gerar_btn.pack(pady=(20, 0))
        
        ttk.Button(main_container, text="Voltar", command=janela.destroy, bootstyle="secondary", width=15).pack(side=BOTTOM, pady=(20, 0))
        
        janela.update_idletasks()
        w, h = 600, 400
        x = (janela.winfo_screenwidth() // 2) - (w // 2)
        y = (janela.winfo_screenheight() // 2) - (h // 2)
        janela.geometry(f"{w}x{h}+{x}+{y}")

