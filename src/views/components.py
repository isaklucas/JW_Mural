"""
Componentes de UI reutilizáveis.

Primeiro passo do SDD 03: extrair a construção de widgets do god object
`ModernApp` (layout.py) para módulos próprios. Aqui vive o card do menu
principal + o botão "ACESSAR". Sem lógica de negócio, sem acesso a banco —
só apresentação, então importável sem MongoDB.

Botão ACESSAR — dois problemas do ttkbootstrap resolvidos juntos:
  1. `ttk.Button` às vezes NÃO renderiza texto no Windows (por isso o autor
     original usava `tk.Button`).
  2. Sob um tema, o ttkbootstrap re-tematiza todo `tk.Button` para a cor
     `primary` — mas só o valor passado NO CONSTRUTOR; um `.configure(bg=...)`
     DEPOIS de criado prevalece.
Solução: criar `tk.Button` (texto aparece) e aplicar cor/hover via `.configure`
após a criação.
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES, X, CENTER, BOTTOM

# Fundo (bg) e texto (fg) por bootstyle.
_CORES = {
    "primary": ("#0d6efd", "white"),
    "info": ("#0dcaf0", "black"),
    "success": ("#198754", "white"),
    "warning": ("#ffc107", "black"),
    "secondary": ("#6c757d", "white"),
    "danger": ("#dc3545", "white"),
}


def _escurecer(hex_cor, fator=0.14):
    """Versão mais escura de uma cor #rrggbb (para hover)."""
    hex_cor = hex_cor.lstrip("#")
    r, g, b = (int(hex_cor[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (round(v * (1 - fator)) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def criar_card(parent, title, description, style, command, row, col, columnspan=1):
    """Monta um card do menu principal com título, descrição e botão ACESSAR.

    `parent` é o frame container (antes: self.cards_frame). Não guarda estado —
    devolve o card criado caso o chamador queira referência.
    `style` é um bootstyle ("primary", "info", "success", "warning",
    "secondary", "danger") aplicado ao botão.
    """
    card = ttk.Frame(parent, bootstyle="light", padding=20)
    card.grid(row=row, column=col, columnspan=columnspan,
              padx=10, pady=10, sticky="nsew")

    # Grid expande igualmente
    for c in range(col, col + columnspan):
        parent.grid_columnconfigure(c, weight=1)
    parent.grid_rowconfigure(row, weight=1)

    content_frame = ttk.Frame(card, bootstyle="light")
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
    desc_label.pack(anchor=CENTER, pady=(0, 20), fill=X)

    button_frame = ttk.Frame(content_frame, bootstyle="light")
    button_frame.pack(side=BOTTOM, fill=X, pady=(10, 0))

    bg, fg = _CORES.get(style, ("#0d6efd", "white"))
    bg_hover = _escurecer(bg)

    access_button = tk.Button(
        button_frame,
        text="ACESSAR",
        font=("Segoe UI", 13, "bold"),
        cursor="hand2",
        command=command,
        relief="flat",
        bd=0,
        highlightthickness=0,
        height=2,      # 2 linhas de texto de altura — não fica fino
        pady=10,
    )
    # Cor DEPOIS de criar: sob tema ttkbootstrap o bg do construtor é ignorado.
    access_button.configure(
        bg=bg, fg=fg,
        activebackground=bg_hover, activeforeground=fg,
        disabledforeground=fg,
    )
    access_button.pack(anchor=CENTER, fill=X, padx=20, ipady=6)

    # Hover: escurece ao passar o mouse, volta ao sair.
    access_button.bind("<Enter>", lambda e: access_button.configure(bg=bg_hover))
    access_button.bind("<Leave>", lambda e: access_button.configure(bg=bg))

    return card
