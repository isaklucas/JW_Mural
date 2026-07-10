"""
Componentes de UI reutilizáveis.

Primeiro passo do SDD 03: extrair a construção de widgets do god object
`ModernApp` (layout.py) para módulos próprios. Aqui vive o card do menu
principal + o botão "ACESSAR". Sem lógica de negócio, sem acesso a banco —
só apresentação, então importável sem MongoDB.

Nota: o código antigo usava `tk.Button` com `bg=` manual por cor. Sob um tema
ttkbootstrap (o app real) o próprio ttkbootstrap re-tematiza todo `tk.Button`
para a cor `primary`, então aquelas cores por-estilo (info/success/danger…)
NUNCA apareciam — todos os botões ficavam azuis. Trocado por `ttk.Button` com
`bootstyle=`, que aplica a cor certa de fato e ganha hover nativo do tema.
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES, X, CENTER, BOTTOM

# Padding do botão ACESSAR: (horizontal, vertical). Vertical maior = botão mais
# alto e com mais respiro que a versão anterior.
_BTN_PADDING = (24, 22)


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

    access_button = ttk.Button(
        button_frame,
        text="ACESSAR  ➜",
        bootstyle=style,          # cor por-estilo + hover nativo do tema
        cursor="hand2",
        command=command,
        padding=_BTN_PADDING,     # botão mais alto
    )
    access_button.pack(anchor=CENTER, fill=X, padx=20)

    return card
