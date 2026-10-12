"""PreviewDocx — pré-visualização de um .docx dentro do app (sem Word).

Pinta num Canvas o layout de `process.minutas.preview.montar_layout`: página
branca em escala, imagens, linhas, títulos e tabelas com as cores do estilo.
É uma aproximação fiel o bastante para conferir o documento enquanto se digita;
o arquivo final é o .docx gerado.
"""
import io
import logging
import tkinter as tk
import tkinter.font as tkfont

import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # noqa: F401,F403

from process.minutas.preview import montar_layout

logger = logging.getLogger(__name__)

PAD = 14          # margem do canvas em volta da página (px)


def _cor(hexa, padrao="000000"):
    """'#RRGGBB' válido para o Tk (cor estranha do docx cai no padrão)."""
    hexa = (hexa or "").strip().lstrip("#")
    if len(hexa) == 6 and all(ch in "0123456789abcdefABCDEF" for ch in hexa):
        return "#" + hexa
    return "#" + padrao
CEL_PAD = 3       # respiro interno da célula (pt)


class PreviewDocx(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, background="#8a8f98", highlightthickness=0)
        barra = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barra.set)
        barra.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self._layout = None
        self._erro = None
        self._fontes = {}
        self._imagens = []  # referências vivas das PhotoImage
        self._redesenho = None
        self.canvas.bind("<Configure>", lambda e: self._agendar_redesenho())
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._roda))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    # ------------------------------------------------------------------ API
    def mostrar(self, docx_bytes):
        try:
            self._layout, self._erro = montar_layout(docx_bytes), None
        except Exception as e:
            logger.exception("Falha ao montar a pré-visualização")
            self._layout, self._erro = None, f"Não foi possível pré-visualizar: {e}"
        self._desenhar()

    def mostrar_erro(self, mensagem):
        self._layout, self._erro = None, mensagem
        self._desenhar()

    # -------------------------------------------------------------- interno
    def _roda(self, evento):
        self.canvas.yview_scroll(int(-evento.delta / 120), "units")

    def _agendar_redesenho(self):
        if self._redesenho:
            self.after_cancel(self._redesenho)
        self._redesenho = self.after(120, self._desenhar)

    def _fonte(self, familia, tamanho_px, negrito, italico):
        chave = (familia, tamanho_px, negrito, italico)
        if chave not in self._fontes:
            self._fontes[chave] = tkfont.Font(
                family=familia or "Calibri", size=-max(6, tamanho_px),
                weight="bold" if negrito else "normal", slant="italic" if italico else "roman")
        return self._fontes[chave]

    def _desenhar(self):
        self._redesenho = None
        c = self.canvas
        c.delete("all")
        self._imagens.clear()
        largura_canvas = max(c.winfo_width(), 200)
        if self._erro or not self._layout:
            c.create_text(largura_canvas // 2, 40, text=self._erro or "Sem pré-visualização.",
                          fill="white", width=largura_canvas - 40, font=("Helvetica", 11))
            c.configure(scrollregion=(0, 0, largura_canvas, 100))
            return

        pagina = self._layout['pagina']
        escala = (largura_canvas - 2 * PAD) / pagina['largura']
        self._e = escala
        x_pagina, y_pagina = PAD, PAD
        x0 = x_pagina + pagina['margem_esq'] * escala
        largura_util = (pagina['largura'] - pagina['margem_esq'] - pagina['margem_dir']) * escala
        fundo = c.create_rectangle(0, 0, 0, 0, fill="white", outline="#555")
        y = y_pagina + pagina['margem_sup'] * escala

        for bloco in self._layout['blocos']:
            if bloco['tipo'] == 'p':
                y = self._paragrafo(bloco, x0, y, largura_util, x_pagina, y_pagina)
            else:
                y = self._tabela(bloco, x0, y)

        altura_pagina = pagina['altura'] * escala
        paginas = max(1, int((y - y_pagina) // altura_pagina) + 1)
        c.coords(fundo, x_pagina, y_pagina, x_pagina + pagina['largura'] * escala,
                 y_pagina + paginas * altura_pagina)
        for i in range(1, paginas):  # quebra de página aproximada
            yy = y_pagina + i * altura_pagina
            c.create_line(x_pagina, yy, x_pagina + pagina['largura'] * escala, yy, fill="#999", dash=(4, 3))
        c.tag_lower(fundo)
        c.configure(scrollregion=(0, 0, int(largura_canvas), int(y_pagina + paginas * altura_pagina + PAD)))

    def _texto_runs(self, runs, x, y, largura, alinhamento):
        """Desenha os runs numa linha (ou com quebra, se não couber). Devolve a altura."""
        c, e = self.canvas, self._e
        if not runs:
            return 0
        fontes = [self._fonte(r.get('fonte'), round(r['tamanho'] * e), r['negrito'], r['italico'])
                  for r in runs]
        larguras = [f.measure(r['texto']) for f, r in zip(fontes, runs)]
        altura = max(f.metrics('linespace') for f in fontes)
        if sum(larguras) <= largura:
            if alinhamento == 'center':
                xi = x + (largura - sum(larguras)) / 2
            elif alinhamento == 'right':
                xi = x + largura - sum(larguras)
            else:
                xi = x
            for r, f, w in zip(runs, fontes, larguras):
                c.create_text(xi, y, text=r['texto'], anchor="nw", font=f, fill=_cor(r['cor']))
                xi += w
            return altura
        # Não cabe numa linha: um bloco só com quebra automática (formato do 1º run).
        texto = ''.join(r['texto'] for r in runs)
        ancora, justificar, xi = {"center": ("n", "center", x + largura / 2),
                                  "right": ("ne", "right", x + largura)}.get(alinhamento, ("nw", "left", x))
        item = c.create_text(xi, y, text=texto, anchor=ancora, justify=justificar, width=max(1, int(largura)),
                             font=fontes[0], fill=_cor(runs[0]['cor']))
        x1, y1, x2, y2 = c.bbox(item)
        return y2 - y1

    def _area_recuada(self, p, x, largura):
        """(x, largura) do texto depois dos recuos do parágrafo. O recuo da 1ª linha
        entra inteiro (os títulos das minutas são, na prática, uma linha por vez)."""
        esq, dir_, primeira = (v * self._e for v in p.get('recuo', (0, 0, 0)))
        inicio = max(0, esq + primeira)
        return x + inicio, max(20, largura - inicio - dir_)

    def _paragrafo(self, b, x0, y, largura, x_pagina, y_pagina):
        c, e = self.canvas, self._e
        y += b['antes'] * e
        topo = y
        empurrar = 0
        for forma in b['formas']:
            h = max(1, forma['altura'] * e)
            c.create_rectangle(x0, y, x0 + min(largura, forma['largura'] * e), y + h,
                               fill=_cor(forma['cor'], "999999"), outline="")
            y += h + 1
        for img in b['imagens']:
            foto = self._foto(img['dados'], img['largura'] * e, img['altura'] * e)
            if foto is None:
                continue
            if img['flutuante']:
                if img['x'] is not None and img['x_relativo'] == 'page':
                    xi = x_pagina + img['x'] * e
                else:
                    xi = x0 + (img['x'] or 0) * e
                c.create_image(xi, topo + img['y'] * e, image=foto, anchor="nw")
                if img.get('empurra'):
                    empurrar = max(empurrar, topo + (img['y'] + img['altura']) * e)
            else:
                c.create_image(x0, y, image=foto, anchor="nw")
                y += img['altura'] * e
        if b['runs']:
            xt, lt = self._area_recuada(b, x0, largura)
            y += self._texto_runs(b['runs'], xt, y, lt, b['alinhamento'])
        elif not b['formas']:
            y += b['tamanho_vazio'] * e * 1.15
        return max(y + b['depois'] * e, empurrar)

    def _foto(self, dados, w, h):
        try:
            from PIL import Image, ImageTk
            img = Image.open(io.BytesIO(dados))
            img = img.resize((max(1, int(w)), max(1, int(h))))
            foto = ImageTk.PhotoImage(img)
            self._imagens.append(foto)
            return foto
        except Exception as ex:
            logger.debug("Imagem não exibida: %s", ex)
            return None

    def _tabela(self, t, x0, y):
        c, e = self.canvas, self._e
        larguras = [w * e for w in t['larguras']] or [100]
        borda = _cor(t['cor_borda'], "BFBFBF")
        for linha in t['linhas']:
            itens, col, xs = [], 0, []
            altura = linha['altura_min'] * e
            for cel in linha['celulas']:
                xa = x0 + sum(larguras[:col])
                xb = x0 + sum(larguras[:col + cel['span']])
                xs.append((xa, xb, cel))
                yy = y + CEL_PAD * e
                for p in cel['paragrafos']:
                    yy += p['antes'] * e
                    if p['runs']:
                        xt, lt = self._area_recuada(p, xa + CEL_PAD * e, xb - xa - 2 * CEL_PAD * e)
                        yy += self._texto_runs(p['runs'], xt, yy, lt, p['alinhamento'])
                    else:
                        yy += p['tamanho_vazio'] * e * 1.1
                    yy += p['depois'] * e
                altura = max(altura, yy - y + CEL_PAD * e)
                col += cel['span']
            for xa, xb, cel in xs:
                ret = c.create_rectangle(xa, y, xb, y + altura, outline=borda,
                                         fill=_cor(cel['fundo'], "FFFFFF"))
                c.tag_lower(ret)
            y += altura
        return y
