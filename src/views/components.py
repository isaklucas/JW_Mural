"""
Componentes de UI reutilizáveis.

Primeiro passo do SDD 03: extrair a construção de widgets do god object
`ModernApp` (layout.py) para módulos próprios. Aqui vive o card do menu
principal. Sem lógica de negócio, sem acesso a banco — só apresentação, então
importável sem MongoDB.

O card INTEIRO é clicável (não há botão "ACESSAR"): clicar em qualquer ponto
navega para a área correspondente. Uma faixa colorida no topo dá a identidade de
cor de cada card (o que o botão fazia antes).
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES, X, W, LEFT, CENTER, TOP
from ttkbootstrap.dialogs import Messagebox

# Cor da faixa por bootstyle.
_CORES = {
    "primary": "#0d6efd",
    "info": "#0dcaf0",
    "success": "#198754",
    "warning": "#ffc107",
    "secondary": "#6c757d",
    "danger": "#dc3545",
}


def _escurecer(hex_cor, fator=0.14):
    """Versão mais escura de uma cor #rrggbb (para hover)."""
    hex_cor = hex_cor.lstrip("#")
    r, g, b = (int(hex_cor[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (round(v * (1 - fator)) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def criar_card(parent, title, description, style, command, row, col, columnspan=1):
    """Monta um card do menu principal — clicável por inteiro.

    `parent` é o frame container (antes: self.cards_frame). `style` é um bootstyle
    ("primary", "info", "success", "warning", "secondary", "danger") usado na
    faixa de cor. `command` dispara ao clicar em qualquer ponto do card.
    """
    cor = _CORES.get(style, "#0d6efd")
    cor_hover = _escurecer(cor)

    card = ttk.Frame(parent, bootstyle="light", padding=0)
    card.grid(row=row, column=col, columnspan=columnspan,
              padx=10, pady=10, sticky="nsew")

    # Grid expande igualmente
    for c in range(col, col + columnspan):
        parent.grid_columnconfigure(c, weight=1)
    parent.grid_rowconfigure(row, weight=1)

    # Faixa de cor no topo (identidade da categoria). tk.Frame p/ controlar bg.
    faixa = tk.Frame(card, height=6, bg=cor)
    faixa.pack(side=TOP, fill=X)

    content_frame = ttk.Frame(card, bootstyle="light", padding=20)
    content_frame.pack(fill=BOTH, expand=YES)

    title_label = ttk.Label(
        content_frame,
        text=title,
        font=("Helvetica", 18, "bold"),
        bootstyle="primary",
        justify="center",
    )
    title_label.pack(anchor=CENTER, pady=(0, 10), fill=X)

    desc_label = ttk.Label(
        content_frame,
        text=description,
        wraplength=300,
        bootstyle="secondary",
        justify="center",
    )
    desc_label.pack(anchor=CENTER, pady=(0, 6), fill=X)

    dica = ttk.Label(
        content_frame,
        text="Clique para abrir  →",
        font=("Segoe UI", 9),
        bootstyle="secondary",
        justify="center",
    )
    dica.pack(anchor=CENTER, pady=(10, 0), fill=X)

    # --- tornar TODO o card clicável ---
    alvos = [card, faixa, content_frame, title_label, desc_label, dica]

    def _abrir(_evt=None):
        command()

    def _enter(_evt=None):
        faixa.configure(bg=cor_hover, height=10)

    def _leave(_evt=None):
        faixa.configure(bg=cor, height=6)

    for w in alvos:
        w.configure(cursor="hand2")
        w.bind("<Button-1>", _abrir)
        w.bind("<Enter>", _enter)
        w.bind("<Leave>", _leave)

    return card



# Rótulos afirmativos que `Messagebox.yesno` pode devolver.
_RESPOSTAS_SIM = {"yes", "sim", "ok"}


def confirmou(resposta):
    """True se o usuário respondeu SIM num `Messagebox.yesno`.

    ARMADILHA: `yesno` devolve o RÓTULO do botão, e o ttkbootstrap traduz esse
    rótulo pelo locale do sistema — em pt-BR volta "Sim", não "Yes". Comparar com
    "Yes" cru faz a ação ser silenciosamente cancelada (o usuário clica em Sim e
    nada acontece). Use sempre este helper.
    """
    if resposta is None:
        return False
    return str(resposta).strip().lower() in _RESPOSTAS_SIM

def abrir_modal_editar_participacao(parent, parte, data, participantes, publicadores,
                                    ao_substituir, ao_remover, ao_terminar=None):
    """Modal para corrigir UMA participação já gravada: trocar quem fez ou apagar.

    É o "transferir histórico" de uma entrada só, usado tanto pelo Histórico de
    Publicadores quanto pelo Histórico de Reuniões. Não fala com o banco: recebe
    os callbacks `ao_substituir(nome_atual, nome_novo)` e `ao_remover(nome_atual)`,
    que devolvem o dict de resultado do serviço ({"success", "message"}).

    Args:
        participantes: nomes atualmente gravados nessa parte (a parte pode ter dois).
        publicadores: lista para escolher o substituto (aceita nome digitado).
        ao_terminar: chamado após uma alteração bem-sucedida (recarregar as telas).
    """
    participantes = [p for p in participantes if p and p != "não possui"]
    if not participantes:
        Messagebox.show_warning("Não há participante para alterar nesta parte.",
                                "Editar participação", parent=parent)
        return

    modal = ttk.Toplevel(parent)
    modal.title("Editar Participação")

    container = ttk.Frame(modal, padding=20)
    container.pack(fill=BOTH, expand=YES)

    ttk.Label(container, text="Editar Participação", font=("Helvetica", 18, "bold"),
              bootstyle="primary").pack(anchor=W, pady=(0, 5))
    ttk.Label(container, text=f"{parte} — {data}", font=("Helvetica", 10),
              bootstyle="secondary", wraplength=460).pack(anchor=W, pady=(0, 15))

    campos = ttk.Frame(container)
    campos.pack(fill=X)
    campos.grid_columnconfigure(1, weight=1)

    ttk.Label(campos, text="Participante atual:", font=("Helvetica", 11)).grid(
        row=0, column=0, sticky="w", padx=(0, 10), pady=8)
    atual_var = ttk.StringVar(value=participantes[0])
    ttk.Combobox(campos, textvariable=atual_var, values=participantes,
                 state="readonly" if len(participantes) > 1 else "disabled",
                 bootstyle="primary").grid(row=0, column=1, sticky="ew", pady=8)

    ttk.Label(campos, text="Novo participante:", font=("Helvetica", 11)).grid(
        row=1, column=0, sticky="w", padx=(0, 10), pady=8)
    novo_var = ttk.StringVar()
    ttk.Combobox(campos, textvariable=novo_var, values=publicadores,
                 bootstyle="primary").grid(row=1, column=1, sticky="ew", pady=8)

    ttk.Label(
        container,
        text=("Substituir passa a participação para o novo publicador (histórico e "
              "reunião salva). Remover apaga a participação dos dois lugares."),
        font=("Helvetica", 9), bootstyle="secondary", wraplength=460
    ).pack(anchor=W, pady=(10, 5))

    def _finalizar(resultado):
        """Mostra o resultado do serviço e fecha o modal quando deu certo."""
        if resultado.get("success"):
            # O modal morre antes do Messagebox: um parent destruído trava o diálogo.
            modal.destroy()
            Messagebox.show_info(resultado.get("message", "Alteração concluída"),
                                 "Editar participação", parent=parent)
            if ao_terminar:
                ao_terminar()
        else:
            Messagebox.show_error(resultado.get("message", "Não foi possível alterar"),
                                  "Editar participação", parent=modal)

    def substituir():
        atual = atual_var.get().strip()
        novo = novo_var.get().strip()
        if not novo:
            Messagebox.show_warning("Escolha o novo participante.",
                                    "Editar participação", parent=modal)
            return
        if novo == atual:
            Messagebox.show_warning("O novo participante é o mesmo de agora.",
                                    "Editar participação", parent=modal)
            return
        confirmar = Messagebox.yesno(
            f"Passar '{parte}' de '{data}' de '{atual}' para '{novo}'?\n\n"
            "O histórico dos dois e a reunião salva serão atualizados.",
            "Confirmar alteração", parent=modal
        )
        if not confirmou(confirmar):
            return
        _finalizar(ao_substituir(atual, novo))

    def remover():
        atual = atual_var.get().strip()
        confirmar = Messagebox.yesno(
            f"Remover '{parte}' de '{data}' de '{atual}'?\n\n"
            "A participação sai do histórico e da reunião salva.",
            "Confirmar remoção", parent=modal
        )
        if not confirmou(confirmar):
            return
        _finalizar(ao_remover(atual))

    botoes = ttk.Frame(container)
    botoes.pack(fill=X, pady=(10, 0))
    ttk.Button(botoes, text="Substituir", command=substituir,
               bootstyle="success", padding=(20, 10)).pack(side=LEFT, padx=5)
    ttk.Button(botoes, text="Remover", command=remover,
               bootstyle="danger", padding=(20, 10)).pack(side=LEFT, padx=5)
    ttk.Button(botoes, text="Cancelar", command=modal.destroy,
               bootstyle="secondary", padding=(20, 10)).pack(side=LEFT, padx=5)

    modal.update_idletasks()
    largura, altura = 540, 360
    x = int((modal.winfo_screenwidth() / 2) - (largura / 2))
    y = int((modal.winfo_screenheight() / 2) - (altura / 2))
    modal.geometry(f"{largura}x{altura}+{x}+{y}")
    modal.transient(parent)
    modal.grab_set()
    return modal
