"""escolher_modo_final_semana, criar_reuniao_final_semana_minutas, editor_minutas

Modo Minutas (SDD 18) — mixin de ModernApp. O documento do final de semana é
montado a partir do ARQUIVO MODELO (o .docx oficial, guardado no banco): a
aparência vem toda dele; a minuta só diz o que vai em cada coluna.

Fluxo de criação (uma janela, três passos, pré-visualização ao vivo à direita):
    1. Período (bimestre), dirigente, seleção automática -> busca no wol.jw.org
    2. Oradores VINDO (recebendo): tema, orador, presidente, leitor por sábado
    3. Oradores INDO (saindo): congregação de destino por mês, orador e tema por sábado
"""
import copy

from views._shared import *  # noqa: F401,F403
from services.minuta_service import minuta_service, abrir_arquivo
from process.minutas import padrao, periodo
from views.preview_docx import PreviewDocx

NOMES_MESES = [periodo.MESES_PT[m] for m in range(1, 13)]
ATRASO_PREVIEW_MS = 450
SEM_CAMPO = "(em branco)"
ROTULOS_CAMPOS = [SEM_CAMPO] + list(padrao.CAMPOS.values())
CAMPO_POR_ROTULO = {v: k for k, v in padrao.CAMPOS.items()}
CAMPO_POR_ROTULO[SEM_CAMPO] = ''


def _centralizar(janela, w, h):
    janela.update_idletasks()
    w = min(w, janela.winfo_screenwidth() - 40)
    h = min(h, janela.winfo_screenheight() - 80)
    x = (janela.winfo_screenwidth() // 2) - (w // 2)
    y = max(0, (janela.winfo_screenheight() // 2) - (h // 2) - 20)
    janela.geometry(f"{w}x{h}+{x}+{y}")


def _area_rolavel(parent):
    """Canvas + scrollbar com roda do mouse. Retorna o frame interno."""
    externo = ttk.Frame(parent)
    externo.pack(fill=BOTH, expand=YES)
    canvas = tk.Canvas(externo, highlightthickness=0)
    barra = ttk.Scrollbar(externo, orient=VERTICAL, command=canvas.yview)
    interno = ttk.Frame(canvas)
    interno.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    janela_id = canvas.create_window((0, 0), window=interno, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(janela_id, width=e.width))
    canvas.configure(yscrollcommand=barra.set)
    barra.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=YES)

    def _roda(evento):
        canvas.yview_scroll(int(-evento.delta / 120), "units")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _roda))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    return interno


def _campo_autocomplete(parent, valor, sugestoes):
    """Entry com lista de sugestões (mesmo padrão da tela legada)."""
    return final_semana.FinalSemana._criar_campo_autocomplete(parent, (valor or '').strip(), sugestoes)


def _formatar_data(iso):
    try:
        return datetime.date.fromisoformat(iso).strftime('%d/%m/%Y')
    except (TypeError, ValueError):
        return iso or ''


class _PainelPreview:
    """Coluna da direita: escolha do documento + PreviewDocx + 'Abrir no Word'.

    `gerar(chave) -> bytes` produz o .docx atual; `agendar()` re-renderiza com
    atraso (debounce) para não travar a digitação.
    """

    def __init__(self, parent, janela, documentos, gerar):
        self.janela, self.gerar = janela, gerar
        self.documentos = documentos  # {rótulo: chave}
        self._pendente = None
        self._ultimo = None
        barra = ttk.Frame(parent)
        barra.pack(fill=X, pady=(0, 6))
        ttk.Label(barra, text="Pré-visualização:", font=("Helvetica", 10, "bold")).pack(side=LEFT)
        self.doc_var = tk.StringVar(value=next(iter(documentos)))
        cb = ttk.Combobox(barra, textvariable=self.doc_var, values=list(documentos), state="readonly", width=28)
        cb.pack(side=LEFT, padx=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self.atualizar())
        ttk.Button(barra, text="Abrir no Word", bootstyle="info-outline", command=self.abrir_no_word).pack(side=RIGHT)
        self.status = ttk.Label(parent, bootstyle="secondary", font=("Helvetica", 8))
        self.status.pack(fill=X)
        self.preview = PreviewDocx(parent)
        self.preview.pack(fill=BOTH, expand=YES)

    @property
    def chave(self):
        return self.documentos[self.doc_var.get()]

    def agendar(self, *_):
        if self._pendente:
            self.janela.after_cancel(self._pendente)
        self._pendente = self.janela.after(ATRASO_PREVIEW_MS, self.atualizar)

    def atualizar(self):
        self._pendente = None
        if not self.janela.winfo_exists():
            return
        try:
            self._ultimo = self.gerar(self.chave)
        except Exception as e:
            logger.exception("Erro na pré-visualização")
            self._ultimo = None
            self.preview.mostrar_erro(f"Não foi possível montar o documento:\n{e}")
            return
        if self._ultimo is None:
            self.preview.mostrar_erro("A pré-visualização aparece aqui.")
            return
        self.preview.mostrar(self._ultimo)
        self.status.configure(text="Prévia aproximada — o arquivo Word sai exatamente com a formatação do modelo oficial.")

    def abrir_no_word(self):
        if self._ultimo is None:
            self.atualizar()
        if self._ultimo is not None:
            abrir_arquivo(minuta_service.gravar_temporario(f"previa_{self.chave}.docx", self._ultimo))


class MinutasMixin:
    # ------------------------------------------------------------------ menu
    def escolher_modo_final_semana(self):
        """Card 'Criar Reunião Final de Semana': escolhe Minutas (novo) ou Template (legado)."""
        janela = ttk.Toplevel(self.root)
        janela.title("Reunião Final de Semana")
        janela.transient(self.root)
        janela.grab_set()

        corpo = ttk.Frame(janela, padding=25)
        corpo.pack(fill=BOTH, expand=YES)
        ttk.Label(corpo, text="Reunião Final de Semana", font=("Helvetica", 18, "bold"),
                  bootstyle="primary").pack(pady=(0, 20))

        def ir(acao):
            janela.destroy()
            acao()

        ttk.Button(corpo, text="Criar reunião (dois meses)", bootstyle="success", padding=(20, 12),
                   command=lambda: ir(self.criar_reuniao_final_semana_minutas)).pack(fill=X, pady=5)
        ttk.Label(corpo, text="Preencha oradores vindo e indo e veja o documento ao lado enquanto digita.",
                  bootstyle="secondary", wraplength=380).pack(pady=(0, 12))
        ttk.Button(corpo, text="Modelo do documento", bootstyle="info-outline", padding=(20, 8),
                   command=lambda: ir(self.editor_minutas)).pack(fill=X, pady=5)
        ttk.Separator(corpo).pack(fill=X, pady=15)
        ttk.Button(corpo, text="Modo antigo (template .docx)", bootstyle="secondary-outline", padding=(20, 8),
                   command=lambda: ir(self.criar_reuniao_final_semana)).pack(fill=X, pady=5)
        ttk.Button(corpo, text="Voltar", bootstyle="secondary", command=janela.destroy).pack(pady=(15, 0))
        _centralizar(janela, 460, 420)

    # --------------------------------------------------------------- criação
    def criar_reuniao_final_semana_minutas(self, reuniao=None, ao_concluir=None):
        """Assistente de 3 passos com pré-visualização. `reuniao` (do histórico) = edição."""
        editando = reuniao is not None
        janela = ttk.Toplevel(self.root)
        janela.title("Reunião Final de Semana")
        janela.transient(self.root)
        janela.grab_set()

        try:
            nomes = minuta_service.listas_de_nomes()
        except Exception as e:
            logger.exception("Erro ao carregar listas de nomes")
            nomes = {'ancios': [], 'ancios_servos': [], 'leitores': [], 'temas': []}
            Messagebox.show_warning(f"Não foi possível carregar a lista de publicadores: {e}",
                                    "Aviso", parent=janela)
        try:
            pacotes = {chave: minuta_service.pacote(chave) for chave in padrao.MINUTAS_PADRAO}
        except Exception as e:
            logger.exception("Erro ao carregar minutas")
            pacotes = {}

        hoje = datetime.date.today()
        prox_ano, prox_mes = periodo.meses_do_periodo(hoje.year, hoje.month, 2)[1]
        estado = {
            'meses': minuta_service.meses_da_reuniao(reuniao) if editando else None,
            'periodo_buscado': (reuniao['ano'], reuniao['mes']) if editando else None,
        }

        ano_var = tk.StringVar(value=str(reuniao['ano'] if editando else prox_ano))
        mes_var = tk.StringVar(value=NOMES_MESES[(reuniao['mes'] if editando else prox_mes) - 1])
        dirigente_var = tk.StringVar(value=(reuniao or {}).get('dirigente') or (nomes['ancios'][0] if nomes['ancios'] else ''))
        nome_var = tk.StringVar(value=(reuniao or {}).get('nome_arquivo', ''))
        auto_pres_var = tk.BooleanVar(value=True)
        auto_leitor_var = tk.BooleanVar(value=True)
        nome_editado = [editando]

        paineis = ttk.Panedwindow(janela, orient=HORIZONTAL)
        paineis.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        esquerda = ttk.Frame(paineis)
        direita = ttk.Frame(paineis, padding=(8, 0, 0, 0))
        paineis.add(esquerda, weight=3)
        paineis.add(direita, weight=2)

        cabecalho = ttk.Label(esquerda, font=("Helvetica", 18, "bold"), bootstyle="primary")
        cabecalho.pack(pady=(5, 2), anchor=W)
        subtitulo = ttk.Label(esquerda, bootstyle="secondary")
        subtitulo.pack(pady=(0, 10), anchor=W)
        rodape = ttk.Frame(esquerda, padding=(0, 10, 0, 0))
        rodape.pack(fill=X, side=BOTTOM)
        conteudo = ttk.Frame(esquerda)
        conteudo.pack(fill=BOTH, expand=YES)

        widgets = {}  # coletor do passo atual

        def periodo_escolhido():
            return int(ano_var.get()), NOMES_MESES.index(mes_var.get()) + 1

        def nome_padrao():
            ano, mes = periodo_escolhido()
            return f"Final de Semana {periodo.nome_periodo(periodo.meses_do_periodo(ano, mes, 2))}"

        def limpar():
            for w in conteudo.winfo_children():
                w.destroy()
            for w in rodape.winfo_children():
                w.destroy()
            widgets.clear()

        def coletar():
            """Grava em estado['meses'] o que está nos campos do passo atual."""
            coletor = widgets.get('coletar')
            if coletor:
                coletor()

        def gerar_previa(chave):
            if chave not in pacotes:
                return None
            coletar()
            meses = estado['meses']
            if meses is None:  # passo 1: esqueleto do período escolhido
                ano, mes = periodo_escolhido()
                meses = periodo.montar_periodo(ano, mes, 2)
            return minuta_service.renderizar_pacote(pacotes[chave], meses, dirigente_var.get().strip())

        previa = _PainelPreview(direita, janela,
                                {"Oradores (vindo e indo)": "fds_oradores",
                                 "Estudo de A Sentinela": "fds_sentinela"},
                                gerar_previa)
        for evento in ("<KeyRelease>", "<<ComboboxSelected>>", "<ButtonRelease-1>"):
            janela.bind(evento, previa.agendar, add="+")

        # ---------------- passo 1: período
        def passo_periodo():
            coletar()
            limpar()
            cabecalho.configure(text="1. Período")
            subtitulo.configure(text="As reuniões são geradas de dois em dois meses.")

            form = ttk.Frame(conteudo)
            form.pack(fill=X, pady=10)
            form.grid_columnconfigure(1, weight=1)

            ttk.Label(form, text="Mês inicial:").grid(row=0, column=0, sticky=W, pady=8, padx=(0, 10))
            linha = ttk.Frame(form)
            linha.grid(row=0, column=1, sticky=W)
            cb_mes = ttk.Combobox(linha, textvariable=mes_var, values=NOMES_MESES, state="readonly", width=12)
            cb_mes.pack(side=LEFT)
            cb_ano = ttk.Combobox(linha, textvariable=ano_var, state="readonly", width=7,
                                  values=[str(a) for a in range(hoje.year - 1, hoje.year + 3)])
            cb_ano.pack(side=LEFT, padx=(8, 0))
            lbl_periodo = ttk.Label(form, bootstyle="info", font=("Helvetica", 11, "bold"))
            lbl_periodo.grid(row=1, column=1, sticky=W)

            ttk.Label(form, text="Dirigente de A Sentinela:").grid(row=2, column=0, sticky=W, pady=8, padx=(0, 10))
            ttk.Combobox(form, textvariable=dirigente_var, values=nomes['ancios'], width=35).grid(row=2, column=1, sticky=W)

            ttk.Label(form, text="Nome do arquivo:").grid(row=3, column=0, sticky=W, pady=8, padx=(0, 10))
            entry_nome = ttk.Entry(form, textvariable=nome_var, width=45)
            entry_nome.grid(row=3, column=1, sticky=EW)
            entry_nome.bind("<Key>", lambda e: nome_editado.__setitem__(0, True))

            ttk.Checkbutton(form, text="Escolher o Presidente automaticamente", variable=auto_pres_var,
                            bootstyle="primary-round-toggle").grid(row=4, column=0, columnspan=2, sticky=W, pady=4)
            ttk.Checkbutton(form, text="Escolher o Leitor de A Sentinela automaticamente", variable=auto_leitor_var,
                            bootstyle="primary-round-toggle").grid(row=5, column=0, columnspan=2, sticky=W, pady=4)

            if editando:
                cb_mes.configure(state=DISABLED)
                cb_ano.configure(state=DISABLED)
                ttk.Label(form, text="Editando reunião salva: o período não pode ser trocado.",
                          bootstyle="warning").grid(row=6, column=0, columnspan=2, sticky=W, pady=(10, 0))

            def atualizar_periodo(*_):
                ano, mes = periodo_escolhido()
                lbl_periodo.configure(text=periodo.nome_periodo(periodo.meses_do_periodo(ano, mes, 2)))
                if not nome_editado[0]:
                    nome_var.set(nome_padrao())

            cb_mes.bind("<<ComboboxSelected>>", atualizar_periodo)
            cb_ano.bind("<<ComboboxSelected>>", atualizar_periodo)
            atualizar_periodo()

            progresso = ttk.Progressbar(conteudo, mode='indeterminate', bootstyle="info-striped", length=400)
            status = ttk.Label(conteudo, bootstyle="info")

            def buscar():
                ano, mes = periodo_escolhido()
                if estado['meses'] and estado['periodo_buscado'] == (ano, mes):
                    passo_vindo()
                    return
                if estado['meses'] and not confirmou(Messagebox.yesno(
                        "Trocar o período descarta o que já foi preenchido. Continuar?",
                        "Trocar período", parent=janela)):
                    return
                btn_buscar.configure(state=DISABLED)
                status.configure(text="Buscando os estudos de A Sentinela no wol.jw.org...")
                status.pack(pady=(20, 5))
                progresso.pack()
                progresso.start(10)

                def trabalho():
                    try:
                        meses = minuta_service.buscar_programacao(
                            ano, mes, 2, auto_presidente=auto_pres_var.get(),
                            auto_leitor=auto_leitor_var.get())
                        erro = None
                    except Exception as e:
                        logger.exception("Erro ao buscar programação do final de semana")
                        meses, erro = None, str(e)

                    def fim():
                        if not janela.winfo_exists():
                            return
                        progresso.stop()
                        if erro:
                            btn_buscar.configure(state=NORMAL)
                            status.configure(text="")
                            Messagebox.show_error(f"Erro ao buscar programação:\n{erro}", "Erro", parent=janela)
                            return
                        sem_titulo = [s for m in meses for s in m['semanas'] if not s['titulo_estudo']]
                        if sem_titulo:
                            Messagebox.show_warning(
                                f"{len(sem_titulo)} semana(s) sem título do estudo (wol.jw.org não respondeu "
                                "ou ainda não publicou). Você pode digitar depois.", "Aviso", parent=janela)
                        estado['meses'] = meses
                        estado['periodo_buscado'] = (ano, mes)
                        passo_vindo()

                    janela.after(0, fim)

                threading.Thread(target=trabalho, daemon=True).start()

            texto_btn = "Próximo ▶" if estado['meses'] else "Buscar programação ▶"
            btn_buscar = ttk.Button(rodape, text=texto_btn, bootstyle="success", command=buscar, width=24)
            btn_buscar.pack(side=RIGHT)
            ttk.Button(rodape, text="Cancelar", bootstyle="secondary", command=janela.destroy, width=12).pack(side=LEFT)
            previa.agendar()

        def coletor(campos):
            def _coletar():
                for m, s, entradas in campos:
                    alvo = s if s is not None else m
                    for chave, entry in entradas.items():
                        try:
                            alvo[chave] = entry.get().strip()
                        except tk.TclError:  # widget já destruído
                            return
            return _coletar

        # ---------------- passo 2: oradores vindo
        def passo_vindo():
            coletar()
            limpar()
            cabecalho.configure(text="2. Oradores vindo")
            subtitulo.configure(text="Discurso público, presidente e leitor de cada sábado.")
            area = _area_rolavel(conteudo)
            campos = []

            for m in estado['meses']:
                bloco = ttk.LabelFrame(area, text=f"{periodo.MESES_PT[m['mes']]} {m['ano']}", padding=10)
                bloco.pack(fill=X, pady=8, padx=(0, 10))
                topo = ttk.Frame(bloco)
                topo.pack(fill=X, pady=(0, 6))
                ttk.Label(topo, text="Congregação (recebendo):").pack(side=LEFT)
                e_cong = ttk.Entry(topo, width=40)
                e_cong.insert(0, m.get('congregacao_recebendo', ''))
                e_cong.pack(side=LEFT, padx=(8, 0), fill=X, expand=YES)
                campos.append((m, None, {'congregacao_recebendo': e_cong}))

                for s in m['semanas']:
                    f = ttk.Frame(bloco, padding=(0, 6))
                    f.pack(fill=X)
                    for c in (1, 3, 5):
                        f.grid_columnconfigure(c, weight=1)
                    ttk.Label(f, text=_formatar_data(s['data']), font=("Helvetica", 10, "bold"),
                              bootstyle="primary").grid(row=0, column=0, sticky=W, padx=(0, 10))
                    e_estudo = ttk.Entry(f)
                    e_estudo.insert(0, s.get('titulo_estudo', ''))
                    e_estudo.grid(row=0, column=1, columnspan=5, sticky=EW, pady=2)

                    ttk.Label(f, text="Tema:").grid(row=1, column=0, sticky=W)
                    c_tema, e_tema = _campo_autocomplete(f, s.get('tema_discurso'), nomes['temas'])
                    c_tema.grid(row=1, column=1, columnspan=5, sticky=EW, pady=2)

                    ttk.Label(f, text="Orador:").grid(row=2, column=0, sticky=W)
                    e_orador = ttk.Entry(f, width=18)
                    e_orador.insert(0, s.get('orador', ''))
                    e_orador.grid(row=2, column=1, sticky=EW, pady=2, padx=(0, 8))
                    ttk.Label(f, text="Presidente:").grid(row=2, column=2, sticky=W)
                    c_pres, e_pres = _campo_autocomplete(f, s.get('presidente'), nomes['ancios_servos'])
                    c_pres.grid(row=2, column=3, sticky=EW, pady=2, padx=(4, 8))
                    ttk.Label(f, text="Leitor:").grid(row=2, column=4, sticky=W)
                    c_leit, e_leit = _campo_autocomplete(f, s.get('leitor_sentinela'), nomes['leitores'])
                    c_leit.grid(row=2, column=5, sticky=EW, pady=2, padx=(4, 0))
                    ttk.Separator(bloco).pack(fill=X)
                    campos.append((m, s, {'titulo_estudo': e_estudo, 'tema_discurso': e_tema, 'orador': e_orador,
                                          'presidente': e_pres, 'leitor_sentinela': e_leit}))

            widgets['coletar'] = coletor(campos)
            ttk.Button(rodape, text="◀ Voltar", bootstyle="secondary", command=passo_periodo, width=12).pack(side=LEFT)
            ttk.Button(rodape, text="Próximo: oradores indo ▶", bootstyle="success", command=passo_indo,
                       width=26).pack(side=RIGHT)
            previa.doc_var.set("Oradores (vindo e indo)")
            previa.agendar()

        # ---------------- passo 3: oradores indo
        def passo_indo():
            coletar()
            limpar()
            cabecalho.configure(text="3. Oradores indo")
            subtitulo.configure(text="Oradores daqui enviados a outra congregação. Deixe em branco o que não houver.")
            area = _area_rolavel(conteudo)
            campos = []

            for m in estado['meses']:
                bloco = ttk.LabelFrame(area, text=f"{periodo.MESES_PT[m['mes']]} {m['ano']}", padding=10)
                bloco.pack(fill=X, pady=8, padx=(0, 10))
                bloco.grid_columnconfigure(1, weight=1)
                bloco.grid_columnconfigure(2, weight=2)
                ttk.Label(bloco, text="Indo para a congregação:").grid(row=0, column=0, sticky=W)
                e_cong = ttk.Entry(bloco)
                e_cong.insert(0, m.get('congregacao_saindo', ''))
                e_cong.grid(row=0, column=1, columnspan=2, sticky=EW, pady=(0, 8))
                campos.append((m, None, {'congregacao_saindo': e_cong}))
                ttk.Label(bloco, text="Sábado", bootstyle="secondary").grid(row=1, column=0, sticky=W)
                ttk.Label(bloco, text="Orador", bootstyle="secondary").grid(row=1, column=1, sticky=W)
                ttk.Label(bloco, text="Tema", bootstyle="secondary").grid(row=1, column=2, sticky=W)

                for i, s in enumerate(m['semanas'], start=2):
                    ttk.Label(bloco, text=_formatar_data(s['data']), font=("Helvetica", 10, "bold"),
                              bootstyle="primary").grid(row=i, column=0, sticky=NW, pady=4, padx=(0, 10))
                    c_or, e_or = _campo_autocomplete(bloco, s.get('orador_saindo'), nomes['ancios_servos'])
                    c_or.grid(row=i, column=1, sticky=EW, pady=4, padx=(0, 8))
                    c_te, e_te = _campo_autocomplete(bloco, s.get('tema_saindo'), nomes['temas'])
                    c_te.grid(row=i, column=2, sticky=EW, pady=4)
                    campos.append((m, s, {'orador_saindo': e_or, 'tema_saindo': e_te}))

            widgets['coletar'] = coletor(campos)
            ttk.Button(rodape, text="◀ Voltar", bootstyle="secondary", command=passo_vindo, width=12).pack(side=LEFT)
            ttk.Button(rodape, text="Gerar documentos", bootstyle="success", command=gerar,
                       width=22).pack(side=RIGHT)
            previa.doc_var.set("Oradores (vindo e indo)")
            previa.agendar()

        def gerar():
            coletar()
            ano, mes = estado['meses'][0]['ano'], estado['meses'][0]['mes']
            if not editando and minuta_service.reuniao_existente(ano, mes):
                resp = Messagebox.yesno(
                    f"Já existe reunião salva para {periodo.MESES_PT[mes]} {ano}. Substituir?",
                    "Substituir reunião", parent=janela)
                if not confirmou(resp):
                    return
            janela.configure(cursor="watch")
            janela.update_idletasks()
            try:
                caminhos = minuta_service.gerar_final_semana(
                    estado['meses'], dirigente_var.get().strip(), nome_var.get().strip())
            except Exception as e:
                logger.exception("Erro ao gerar documentos por minuta")
                janela.configure(cursor="")
                Messagebox.show_error(f"Erro ao gerar documentos:\n{e}", "Erro", parent=janela)
                return
            for caminho in caminhos:
                abrir_arquivo(caminho)
            janela.destroy()
            Messagebox.show_info(
                "Documentos gerados e guardados no banco:\n\n" + "\n".join(os.path.basename(c) for c in caminhos),
                "Sucesso")
            if ao_concluir:
                ao_concluir()

        if editando:
            passo_vindo()
        else:
            passo_periodo()
        _centralizar(janela, 1500, 880)

    # ---------------------------------------------------------------- editor
    def editor_minutas(self):
        """Modelo do documento: arquivo Word oficial + o que vai em cada coluna.
        A aparência (imagem, cores, fontes, tamanhos) vem do arquivo Word."""
        janela = ttk.Toplevel(self.root)
        janela.title("Modelo do documento — Final de Semana")
        janela.transient(self.root)
        janela.grab_set()

        try:
            minutas = {m['chave']: m for m in minuta_service.listar_minutas()}
        except Exception as e:
            logger.exception("Erro ao carregar minutas")
            Messagebox.show_error(f"Erro ao carregar minutas: {e}", "Erro", parent=janela)
            janela.destroy()
            return
        for chave in padrao.MINUTAS_PADRAO:
            if minutas.get(chave, {}).get('formato') != padrao.FORMATO:
                minutas[chave] = padrao.minuta_padrao(chave)

        documentos = {(minutas[c].get('nome') or c): c for c in padrao.MINUTAS_PADRAO}
        estado = {'chave': next(iter(documentos.values())), 'minuta': None, 'descricao': {},
                  'cab_vars': [], 'blocos_ui': []}

        paineis = ttk.Panedwindow(janela, orient=HORIZONTAL)
        paineis.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        esquerda = ttk.Frame(paineis)
        direita = ttk.Frame(paineis, padding=(8, 0, 0, 0))
        paineis.add(esquerda, weight=1)
        paineis.add(direita, weight=1)

        topo = ttk.Frame(esquerda)
        topo.pack(fill=X)
        ttk.Label(topo, text="Documento:", font=("Helvetica", 11, "bold")).pack(side=LEFT)
        doc_var = tk.StringVar(value=next(iter(documentos)))
        cb_doc = ttk.Combobox(topo, textvariable=doc_var, values=list(documentos), state="readonly", width=32)
        cb_doc.pack(side=LEFT, padx=8)

        rodape = ttk.Frame(esquerda, padding=(0, 10, 0, 0))
        rodape.pack(fill=X, side=BOTTOM)
        formulario = ttk.Frame(esquerda)
        formulario.pack(fill=BOTH, expand=YES, pady=(8, 0))

        def coletar():
            """Minuta (dict) a partir da tela."""
            m = copy.deepcopy(estado['minuta'])
            textos_modelo = estado['descricao'].get('cabecalho', [])
            cab = [v.get().strip() for v in estado['cab_vars']]
            # Só guarda o que mudou em relação ao modelo (o resto acompanha o arquivo Word).
            m['cabecalho'] = [] if cab == textos_modelo else [
                (novo if novo != original else '') for novo, original in zip(cab, textos_modelo)]
            tabelas = []
            for ui in estado['blocos_ui']:
                tabelas.append({
                    'nome': ui['nome'],
                    'modelo': ui['modelo'],
                    'titulo': ui['titulo'].get().strip(),
                    'campos': [CAMPO_POR_ROTULO.get(v.get(), '') for v in ui['campos']],
                    'omitir_se_vazio': bool(ui['omitir'].get()),
                    'linha_dados': ui['linha_dados'],
                })
            m['tabelas'] = tabelas
            return m

        def gerar_previa(_chave):
            if estado['minuta'] is None:
                return None
            return minuta_service.renderizar_exemplo(coletar())

        previa = _PainelPreview(direita, janela, {"Documento selecionado (dados de exemplo)": "editor"}, gerar_previa)
        for evento in ("<KeyRelease>", "<<ComboboxSelected>>", "<ButtonRelease-1>"):
            janela.bind(evento, previa.agendar, add="+")

        def montar(m):
            """(Re)constrói o formulário para a minuta `m`."""
            estado['minuta'] = copy.deepcopy(m)
            estado['descricao'] = minuta_service.descrever_modelo(m['chave'])
            for w in formulario.winfo_children():
                w.destroy()
            area = _area_rolavel(formulario)
            desc = estado['descricao']
            tabelas_modelo = desc.get('tabelas', [])
            opcoes_tabelas = [f"Tabela {t['indice'] + 1} — {t['titulo'][:55]}" for t in tabelas_modelo]

            # --- arquivo modelo
            info = minuta_service.info_modelo(m['chave'])
            caixa = ttk.LabelFrame(area, text="1. Arquivo modelo (Word oficial)", padding=10)
            caixa.pack(fill=X, pady=(0, 10), padx=(0, 10))
            ttk.Label(caixa, wraplength=520, justify=LEFT, bootstyle="secondary",
                      text="A aparência — imagem, cores, fontes e tamanhos — vem deste arquivo. "
                           "Para mudar a aparência, ajuste o arquivo no Word e importe de novo.").pack(anchor=W)
            ttk.Label(caixa, font=("Helvetica", 10, "bold"),
                      text=f"Usando: {info.get('nome') or 'modelo padrão'}"
                           + (f"  (atualizado em {info['atualizado_em'][:16].replace('T', ' ')})"
                              if info.get('atualizado_em') else "")).pack(anchor=W, pady=(6, 6))
            botoes = ttk.Frame(caixa)
            botoes.pack(anchor=W)
            ttk.Button(botoes, text="Importar arquivo oficial…", bootstyle="info", command=importar_modelo).pack(side=LEFT, padx=(0, 6))
            ttk.Button(botoes, text="Abrir modelo no Word", bootstyle="info-outline", command=abrir_modelo).pack(side=LEFT, padx=(0, 6))
            ttk.Button(botoes, text="Usar modelo padrão", bootstyle="secondary-outline", command=modelo_padrao).pack(side=LEFT)

            # --- textos do topo
            estado['cab_vars'] = []
            if desc.get('cabecalho'):
                caixa = ttk.LabelFrame(area, text="2. Títulos do topo", padding=10)
                caixa.pack(fill=X, pady=(0, 10), padx=(0, 10))
                ttk.Label(caixa, bootstyle="secondary", wraplength=520, justify=LEFT,
                          text="Pode usar {congregacao} para o nome da congregação das Configurações.").pack(anchor=W)
                salvos = m.get('cabecalho') or []
                for i, texto_modelo in enumerate(desc['cabecalho']):
                    valor = salvos[i] if i < len(salvos) and salvos[i] else texto_modelo
                    var = tk.StringVar(value=valor)
                    ttk.Entry(caixa, textvariable=var).pack(fill=X, pady=2)
                    estado['cab_vars'].append(var)

            # --- blocos
            estado['blocos_ui'] = []
            for b_i, t in enumerate(m.get('tabelas', [])):
                caixa = ttk.LabelFrame(area, text=f"{b_i + 3}. Tabela de cada mês — {t.get('nome') or 'Bloco'}", padding=10)
                caixa.pack(fill=X, pady=(0, 10), padx=(0, 10))
                caixa.grid_columnconfigure(1, weight=1)
                ui = {'nome': t.get('nome', ''), 'modelo': t.get('modelo', 0),
                      'linha_dados': t.get('linha_dados', 2)}

                ttk.Label(caixa, text="Usar como exemplo:").grid(row=0, column=0, sticky=W, pady=3)
                var_tab = tk.StringVar(value=opcoes_tabelas[ui['modelo']] if ui['modelo'] < len(opcoes_tabelas) else '')
                cb_tab = ttk.Combobox(caixa, textvariable=var_tab, values=opcoes_tabelas, state="readonly")
                cb_tab.grid(row=0, column=1, columnspan=2, sticky=EW, pady=3)

                def trocar_tabela(_e=None, b_i=b_i, var_tab=var_tab):
                    atual = coletar()
                    atual['tabelas'][b_i]['modelo'] = opcoes_tabelas.index(var_tab.get())
                    montar(atual)
                    previa.agendar()

                cb_tab.bind("<<ComboboxSelected>>", trocar_tabela)

                ttk.Label(caixa, text="Título do mês:").grid(row=1, column=0, sticky=W, pady=3)
                ui['titulo'] = tk.StringVar(value=t.get('titulo', ''))
                e_tit = ttk.Entry(caixa, textvariable=ui['titulo'])
                e_tit.grid(row=1, column=1, sticky=EW, pady=3)
                var_ins = tk.StringVar(value="Inserir…")
                cb_ins = ttk.Combobox(caixa, textvariable=var_ins, state="readonly", width=24,
                                      values=[f"{{{k}}} — {v}" for k, v in padrao.VARIAVEIS_TITULO.items()])
                cb_ins.grid(row=1, column=2, padx=(6, 0))

                def inserir(_e=None, e_tit=e_tit, var_ins=var_ins):
                    e_tit.insert(tk.INSERT, var_ins.get().split(" — ")[0])
                    var_ins.set("Inserir…")
                    previa.agendar()

                cb_ins.bind("<<ComboboxSelected>>", inserir)
                ttk.Label(caixa, bootstyle="secondary",
                          text="Em branco = mantém o título escrito no modelo.").grid(row=2, column=1, sticky=W)

                ttk.Label(caixa, text="O que vai em cada coluna:", font=("Helvetica", 10, "bold")).grid(
                    row=3, column=0, columnspan=3, sticky=W, pady=(8, 2))
                info_tab = tabelas_modelo[ui['modelo']] if ui['modelo'] < len(tabelas_modelo) else {'colunas': [], 'n_colunas': 0}
                campos = list(t.get('campos', []))
                ui['campos'] = []
                for c_i in range(info_tab['n_colunas']):
                    rotulo_col = info_tab['colunas'][c_i] if c_i < len(info_tab['colunas']) else f"Coluna {c_i + 1}"
                    ttk.Label(caixa, text=f"  {rotulo_col or f'Coluna {c_i + 1}'}").grid(row=4 + c_i, column=0, sticky=W)
                    campo = campos[c_i] if c_i < len(campos) else ''
                    var = tk.StringVar(value=padrao.CAMPOS.get(campo, SEM_CAMPO))
                    ttk.Combobox(caixa, textvariable=var, values=ROTULOS_CAMPOS, state="readonly").grid(
                        row=4 + c_i, column=1, sticky=EW, pady=2)
                    ui['campos'].append(var)

                linha = 4 + info_tab['n_colunas']
                ui['omitir'] = tk.BooleanVar(value=bool(t.get('omitir_se_vazio')))
                ttk.Checkbutton(caixa, text="Não mostrar esta tabela no mês em que estiver vazia",
                                variable=ui['omitir']).grid(row=linha, column=0, columnspan=3, sticky=W, pady=(6, 0))
                if len(m.get('tabelas', [])) > 1:
                    ttk.Button(caixa, text="Remover esta tabela", bootstyle="danger-link",
                               command=lambda b_i=b_i: remover_bloco(b_i)).grid(row=linha + 1, column=0, sticky=W)
                estado['blocos_ui'].append(ui)

            ttk.Button(area, text="+ Adicionar outra tabela por mês", bootstyle="success-link",
                       command=adicionar_bloco).pack(anchor=W)

        def trocar_documento(_e=None):
            estado['chave'] = documentos[doc_var.get()]
            montar(minutas[estado['chave']])
            previa.agendar()

        def adicionar_bloco():
            m = coletar()
            n = len(estado['descricao'].get('tabelas', [{}])[0].get('colunas', [])) or 1
            m['tabelas'].append({'nome': f"Tabela {len(m['tabelas']) + 1}", 'modelo': 0, 'titulo': '',
                                 'campos': ['data'] + [''] * (n - 1), 'omitir_se_vazio': True, 'linha_dados': 2})
            montar(m)
            previa.agendar()

        def remover_bloco(indice):
            m = coletar()
            del m['tabelas'][indice]
            montar(m)
            previa.agendar()

        def importar_modelo():
            from tkinter import filedialog
            caminho = filedialog.askopenfilename(parent=janela, title="Arquivo Word oficial",
                                                 filetypes=[("Documento Word", "*.docx")])
            if not caminho:
                return
            with open(caminho, "rb") as f:
                r = minuta_service.trocar_modelo(estado['chave'], f.read(), os.path.basename(caminho))
            if not r.get('success'):
                Messagebox.show_error(r.get('message', 'Erro'), "Arquivo modelo", parent=janela)
                return
            montar(coletar())
            previa.agendar()
            Messagebox.ok("Arquivo importado. Confira na pré-visualização qual tabela serve de exemplo "
                          "para cada parte e salve.", "Arquivo modelo", parent=janela)

        def abrir_modelo():
            modelo = minuta_service.obter_modelo(estado['chave'])
            if modelo:
                abrir_arquivo(minuta_service.gravar_temporario(f"modelo_{estado['chave']}.docx", modelo))

        def modelo_padrao():
            if not confirmou(Messagebox.yesno("Voltar a usar o arquivo modelo padrão?", "Modelo", parent=janela)):
                return
            minuta_service.restaurar_modelo_padrao(estado['chave'])
            montar(coletar())
            previa.agendar()

        def salvar():
            m = coletar()
            r = minuta_service.salvar_minuta(m)
            if not r.get('success'):
                Messagebox.show_error(r.get('message', 'Erro ao salvar'), "Não foi possível salvar", parent=janela)
                return
            m['versao'] = r.get('versao', m.get('versao'))
            minutas[m['chave']] = m
            estado['minuta'] = copy.deepcopy(m)
            Messagebox.ok("Modelo salvo. As próximas reuniões já saem assim.", "Salvo", parent=janela)

        def restaurar():
            if not confirmou(Messagebox.yesno("Voltar este documento para o padrão (arquivo modelo e colunas)?",
                                              "Restaurar padrão", parent=janela)):
                return
            minuta_service.restaurar_padrao(estado['chave'])
            minutas[estado['chave']] = minuta_service.obter_minuta(estado['chave'])
            montar(minutas[estado['chave']])
            previa.agendar()

        cb_doc.bind("<<ComboboxSelected>>", trocar_documento)
        ttk.Button(rodape, text="Salvar", bootstyle="success", width=14, command=salvar).pack(side=LEFT, padx=(0, 8))
        ttk.Button(rodape, text="Restaurar padrão", bootstyle="warning-outline", width=16, command=restaurar).pack(side=LEFT)
        ttk.Button(rodape, text="Fechar", bootstyle="secondary", width=12, command=janela.destroy).pack(side=RIGHT)

        trocar_documento()
        _centralizar(janela, 1450, 860)
