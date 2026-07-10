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
from ttkbootstrap.constants import BOTH, YES, X, CENTER, TOP

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
