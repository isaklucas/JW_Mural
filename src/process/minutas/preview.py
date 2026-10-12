"""Layout simplificado de um .docx para pré-visualização na tela (sem Word).

`montar_layout(docx_bytes)` devolve uma "lista de desenho" neutra que a tela
(`views/preview_docx.py`) pinta num Canvas. Não é um renderizador de Word
completo — cobre o que as minutas usam: parágrafos com runs formatados, imagens
(inline e flutuantes), linhas decorativas, tabelas com células mescladas e cores
vindas do estilo de tabela (inclusive cores do tema com tint/shade).

Medidas em pontos (pt). Cores em hex "RRGGBB".

    {"pagina": {"largura", "altura", "margem_esq", "margem_dir", "margem_sup"},
     "blocos": [
        {"tipo": "p", "alinhamento": "left|center|right", "antes", "depois", "recuo": (esq, dir, 1a linha),
         "runs": [{"texto", "tamanho", "negrito", "italico", "cor", "fonte"}],
         "imagens": [{"dados": bytes, "largura", "altura", "x", "y", "flutuante"}],
         "formas": [{"largura", "altura", "cor"}]},
        {"tipo": "tabela", "larguras": [pt...], "cor_borda": hex,
         "linhas": [{"altura_min": pt, "celulas": [{"span", "fundo", "paragrafos": [{"alinhamento", "runs"}]}]}]}
     ]}
"""
import io
import logging

from docx import Document
from docx.oxml.ns import qn
from lxml import etree

logger = logging.getLogger(__name__)

NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
EMU_POR_PT = 12700

_TEMA_W_PARA_A = {
    'text1': 'dk1', 'dark1': 'dk1', 'background1': 'lt1', 'light1': 'lt1',
    'text2': 'dk2', 'dark2': 'dk2', 'background2': 'lt2', 'light2': 'lt2',
}


def _bool(el):
    """<w:b/> ligado? (val ausente = verdadeiro)."""
    if el is None:
        return None
    return el.get(qn('w:val'), 'true') not in ('0', 'false', 'off')


def _aplicar_tint_shade(hexa, tint=None, shade=None):
    r, g, b = (int(hexa[i:i + 2], 16) for i in (0, 2, 4))
    if tint is not None:
        f = int(tint, 16) / 255
        r, g, b = (round(c * f + 255 * (1 - f)) for c in (r, g, b))
    if shade is not None:
        f = int(shade, 16) / 255
        r, g, b = (round(c * f) for c in (r, g, b))
    return f"{r:02X}{g:02X}{b:02X}"


class _Contexto:
    """Tema de cores, estilos e padrões do documento."""

    def __init__(self, doc):
        self.doc = doc
        self.tema = self._ler_tema(doc)
        self.padrao = self._ler_padroes(doc)

    @staticmethod
    def _ler_tema(doc):
        cores = {}
        try:
            for rel in doc.part.rels.values():
                if rel.reltype.endswith('/theme'):
                    raiz = etree.fromstring(rel.target_part.blob)
                    esquema = raiz.find(f'.//{{{NS_A}}}clrScheme')
                    for filho in esquema:
                        nome = etree.QName(filho).localname
                        srgb = filho.find(f'{{{NS_A}}}srgbClr')
                        sys_ = filho.find(f'{{{NS_A}}}sysClr')
                        if srgb is not None:
                            cores[nome] = srgb.get('val')
                        elif sys_ is not None:
                            cores[nome] = sys_.get('lastClr', '000000')
                    break
        except Exception as e:
            logger.debug("Tema não lido: %s", e)
        return cores

    @staticmethod
    def _ler_padroes(doc):
        padrao = {'tamanho': 11.0, 'fonte': None}
        try:
            rpr = doc.styles.element.find(qn('w:docDefaults') + '/' + qn('w:rPrDefault') + '/' + qn('w:rPr'))
            if rpr is not None:
                sz = rpr.find(qn('w:sz'))
                if sz is not None:
                    padrao['tamanho'] = int(sz.get(qn('w:val'))) / 2
                fontes = rpr.find(qn('w:rFonts'))
                if fontes is not None:
                    padrao['fonte'] = fontes.get(qn('w:ascii'))
        except Exception:
            pass
        return padrao

    def cor_tema(self, nome, tint=None, shade=None):
        base = self.tema.get(_TEMA_W_PARA_A.get(nome, nome))
        if not base:
            return None
        return _aplicar_tint_shade(base, tint, shade)

    def cor_de_shd(self, shd):
        if shd is None:
            return None
        tema = shd.get(qn('w:themeFill'))
        if tema:
            return self.cor_tema(tema, shd.get(qn('w:themeFillTint')), shd.get(qn('w:themeFillShade')))
        fill = shd.get(qn('w:fill'))
        return fill.upper() if fill and fill.lower() != 'auto' else None

    def cor_de_color(self, color):
        if color is None:
            return None
        tema = color.get(qn('w:themeColor'))
        if tema:
            return self.cor_tema(tema, color.get(qn('w:themeTint')), color.get(qn('w:themeShade')))
        val = color.get(qn('w:val'))
        return val.upper() if val and val.lower() != 'auto' else None


def _props_rpr(ctx, rpr):
    """Propriedades explícitas de um rPr (só as presentes)."""
    props = {}
    if rpr is None:
        return props
    sz = rpr.find(qn('w:sz'))
    if sz is not None:
        props['tamanho'] = int(sz.get(qn('w:val'))) / 2
    for chave, tag in (('negrito', 'w:b'), ('italico', 'w:i')):
        v = _bool(rpr.find(qn(tag)))
        if v is not None:
            props[chave] = v
    cor = ctx.cor_de_color(rpr.find(qn('w:color')))
    if cor:
        props['cor'] = cor
    fontes = rpr.find(qn('w:rFonts'))
    if fontes is not None and fontes.get(qn('w:ascii')):
        props['fonte'] = fontes.get(qn('w:ascii'))
    return props


def _props_estilo_paragrafo(ctx, p):
    """Propriedades herdadas do estilo do parágrafo (cadeia basedOn)."""
    ppr = p.find(qn('w:pPr'))
    estilo_id = None
    if ppr is not None and ppr.find(qn('w:pStyle')) is not None:
        estilo_id = ppr.find(qn('w:pStyle')).get(qn('w:val'))
    cadeia = []
    estilos = ctx.doc.styles.element
    visitados = set()
    while True:
        if estilo_id:
            el = estilos.find(f"{qn('w:style')}[@{qn('w:styleId')}='{estilo_id}']")
        else:
            el = estilos.find(f"{qn('w:style')}[@{qn('w:default')}='1'][@{qn('w:type')}='paragraph']")
        if el is None or id(el) in visitados:
            break
        visitados.add(id(el))
        cadeia.append(el)
        base = el.find(qn('w:basedOn'))
        if base is None:
            break
        estilo_id = base.get(qn('w:val'))
    props = {}
    for el in reversed(cadeia):
        props.update(_props_rpr(ctx, el.find(qn('w:rPr'))))
    return props


def _alinhamento(p):
    ppr = p.find(qn('w:pPr'))
    jc = ppr.find(qn('w:jc')) if ppr is not None else None
    val = jc.get(qn('w:val')) if jc is not None else 'left'
    return {'center': 'center', 'right': 'right', 'end': 'right', 'both': 'left'}.get(val, 'left')


def _espacamento(p):
    ppr = p.find(qn('w:pPr'))
    sp = ppr.find(qn('w:spacing')) if ppr is not None else None
    if sp is None:
        return 0.0, 0.0
    return (int(sp.get(qn('w:before'), 0) or 0) / 20, int(sp.get(qn('w:after'), 0) or 0) / 20)


def _recuo(p):
    """(esquerda, direita, primeira_linha) em pt. Primeira linha negativa = deslocamento."""
    ppr = p.find(qn('w:pPr'))
    ind = ppr.find(qn('w:ind')) if ppr is not None else None
    if ind is None:
        return 0.0, 0.0, 0.0

    def _tw(*nomes):
        for nome in nomes:
            v = ind.get(qn(f'w:{nome}'))
            if v not in (None, ''):
                try:
                    return int(v) / 20
                except ValueError:
                    pass
        return 0.0

    primeira = _tw('firstLine') - _tw('hanging')
    return _tw('left', 'start'), _tw('right', 'end'), primeira


def _eh_run_de_texto(r):
    return r.find(qn('w:t')) is not None


def _runs(ctx, p, herdado):
    base = {'tamanho': ctx.padrao['tamanho'], 'negrito': False, 'italico': False,
            'cor': '000000', 'fonte': ctx.padrao['fonte']}
    base.update(herdado)
    base.update(_props_estilo_paragrafo(ctx, p))
    runs = []
    for r in p.iter(qn('w:r')):
        if not _eh_run_de_texto(r):
            continue
        texto = ''.join(t.text or '' for t in r.iter(qn('w:t')))
        if not texto:
            continue
        props = dict(base)
        props.update(_props_rpr(ctx, r.find(qn('w:rPr'))))
        props['texto'] = texto
        runs.append(props)
    return runs


def _tamanho_marca(ctx, p, herdado):
    """Altura de um parágrafo vazio: tamanho da marca de parágrafo."""
    props = {'tamanho': ctx.padrao['tamanho']}
    props.update(herdado)
    props.update(_props_estilo_paragrafo(ctx, p))
    ppr = p.find(qn('w:pPr'))
    if ppr is not None:
        props.update(_props_rpr(ctx, ppr.find(qn('w:rPr'))))
    return props['tamanho']


def _imagens_e_formas(ctx, p):
    imagens, formas = [], []
    for desenho in p.iter(qn('w:drawing')):
        ext = desenho.find(f'.//{{{NS_WP}}}extent')
        if ext is None:
            continue
        larg, alt = int(ext.get('cx')) / EMU_POR_PT, int(ext.get('cy')) / EMU_POR_PT
        blip = desenho.find(f'.//{{{NS_A}}}blip')
        ancora = desenho.find(f'{{{NS_WP}}}anchor')
        if blip is not None:
            rid = blip.get(f'{{{NS_R}}}embed')
            try:
                dados = ctx.doc.part.related_parts[rid].blob
            except KeyError:
                continue
            img = {'dados': dados, 'largura': larg, 'altura': alt, 'flutuante': ancora is not None,
                   'x': None, 'x_relativo': None, 'y': 0.0,
                   # wrapTopAndBottom: o texto seguinte começa abaixo da imagem
                   'empurra': ancora is not None and ancora.find(f'{{{NS_WP}}}wrapTopAndBottom') is not None}
            if ancora is not None:
                ph = ancora.find(f'{{{NS_WP}}}positionH')
                pv = ancora.find(f'{{{NS_WP}}}positionV')
                off_h = ph.find(f'{{{NS_WP}}}posOffset') if ph is not None else None
                off_v = pv.find(f'{{{NS_WP}}}posOffset') if pv is not None else None
                if off_h is not None:
                    img['x'] = int(off_h.text) / EMU_POR_PT
                    img['x_relativo'] = ph.get('relativeFrom')
                if off_v is not None:
                    img['y'] = int(off_v.text) / EMU_POR_PT
            imagens.append(img)
        else:
            cor = None
            for preenchido in desenho.iter(f'{{{NS_A}}}solidFill'):
                srgb = preenchido.find(f'{{{NS_A}}}srgbClr')
                if srgb is not None:
                    cor = srgb.get('val')
                    break
            formas.append({'largura': larg, 'altura': alt, 'cor': cor or '999999'})
    return imagens, formas


# ------------------------------------------------------------------ tabelas

def _estilo_tabela(ctx, tbl):
    tblpr = tbl.find(qn('w:tblPr'))
    est = tblpr.find(qn('w:tblStyle')) if tblpr is not None else None
    if est is None:
        return None
    return ctx.doc.styles.element.find(f"{qn('w:style')}[@{qn('w:styleId')}='{est.get(qn('w:val'))}']")


def _formatos_condicionais(ctx, estilo):
    """{tipo: {'fundo', 'rpr'}} do estilo de tabela (inclui 'wholeTable')."""
    formatos = {}
    if estilo is None:
        return formatos
    tcpr = estilo.find(qn('w:tcPr'))
    formatos['wholeTable'] = {
        'fundo': ctx.cor_de_shd(tcpr.find(qn('w:shd'))) if tcpr is not None else None,
        'rpr': _props_rpr(ctx, estilo.find(qn('w:rPr'))),
    }
    for cond in estilo.findall(qn('w:tblStylePr')):
        tcpr = cond.find(qn('w:tcPr'))
        formatos[cond.get(qn('w:type'))] = {
            'fundo': ctx.cor_de_shd(tcpr.find(qn('w:shd'))) if tcpr is not None else None,
            'rpr': _props_rpr(ctx, cond.find(qn('w:rPr'))),
        }
    return formatos


def _cor_borda(ctx, tbl, estilo):
    for origem in (tbl.find(qn('w:tblPr')), estilo.find(qn('w:tblPr')) if estilo is not None else None):
        if origem is None:
            continue
        bordas = origem.find(qn('w:tblBorders'))
        if bordas is None:
            continue
        for nome in ('insideH', 'top', 'bottom', 'left'):
            b = bordas.find(qn(f'w:{nome}'))
            if b is not None and b.get(qn('w:val')) not in ('nil', 'none'):
                # Em bordas, w:val é o tipo de linha; a cor fica em w:color/w:themeColor.
                tema = b.get(qn('w:themeColor'))
                cor = ctx.cor_tema(tema, b.get(qn('w:themeTint')), b.get(qn('w:themeShade'))) if tema else None
                if not cor:
                    val = b.get(qn('w:color'))
                    cor = val.upper() if val and val.lower() != 'auto' else None
                if cor:
                    return cor
    return 'BFBFBF'


def _look(tbl):
    tblpr = tbl.find(qn('w:tblPr'))
    look = tblpr.find(qn('w:tblLook')) if tblpr is not None else None
    padrao = {'firstRow': True, 'lastRow': False, 'firstColumn': True, 'lastColumn': False,
              'noHBand': False, 'noVBand': True}
    if look is None:
        return padrao
    val = int(look.get(qn('w:val'), '0') or '0', 16)
    bits = {'firstRow': 0x20, 'lastRow': 0x40, 'firstColumn': 0x80, 'lastColumn': 0x100,
            'noHBand': 0x200, 'noVBand': 0x400}
    resultado = {}
    for chave, bit in bits.items():
        attr = look.get(qn(f'w:{chave}'))
        resultado[chave] = (attr in ('1', 'true')) if attr is not None else bool(val & bit)
    return resultado


def _tabela(ctx, tbl):
    estilo = _estilo_tabela(ctx, tbl)
    formatos = _formatos_condicionais(ctx, estilo)
    look = _look(tbl)
    grid = tbl.find(qn('w:tblGrid'))
    larguras = [int(g.get(qn('w:w'), 0) or 0) / 20 for g in grid] if grid is not None else []
    linhas_xml = tbl.findall(qn('w:tr'))
    n_linhas = len(linhas_xml)
    linhas = []
    for ri, tr in enumerate(linhas_xml):
        trpr = tr.find(qn('w:trPr'))
        altura = trpr.find(qn('w:trHeight')) if trpr is not None else None
        celulas = []
        col = 0
        for tc in tr.findall(qn('w:tc')):
            tcpr = tc.find(qn('w:tcPr'))
            span_el = tcpr.find(qn('w:gridSpan')) if tcpr is not None else None
            span = int(span_el.get(qn('w:val'))) if span_el is not None else 1

            # Ordem de prioridade do Word: tabela < bandas < colunas < linhas.
            tipos = ['wholeTable']
            inicio_banda = 1 if look['firstRow'] else 0
            if not look['noVBand']:
                tipos.append('band1Vert' if col % 2 == 0 else 'band2Vert')
            if not look['noHBand'] and ri >= inicio_banda:
                tipos.append('band1Horz' if (ri - inicio_banda) % 2 == 0 else 'band2Horz')
            if look['firstColumn'] and col == 0:
                tipos.append('firstCol')
            if look['lastColumn'] and col + span == len(larguras):
                tipos.append('lastCol')
            if look['lastRow'] and ri == n_linhas - 1:
                tipos.append('lastRow')
            if look['firstRow'] and ri == 0:
                tipos.append('firstRow')
            fundo, herdado = None, {}
            for t in tipos:
                f = formatos.get(t)
                if f:
                    fundo = f['fundo'] or fundo
                    herdado.update(f['rpr'])
            explicito = ctx.cor_de_shd(tcpr.find(qn('w:shd'))) if tcpr is not None else None
            paragrafos = []
            for p in tc.findall(qn('w:p')):
                antes, depois = _espacamento(p)
                paragrafos.append({'alinhamento': _alinhamento(p), 'runs': _runs(ctx, p, herdado),
                                   'recuo': _recuo(p),
                                   'tamanho_vazio': _tamanho_marca(ctx, p, herdado),
                                   'antes': antes, 'depois': depois})
            celulas.append({'span': span, 'fundo': explicito or fundo, 'paragrafos': paragrafos})
            col += span
        linhas.append({'altura_min': int(altura.get(qn('w:val'), 0)) / 20 if altura is not None else 0,
                       'celulas': celulas})
    return {'tipo': 'tabela', 'larguras': larguras, 'linhas': linhas, 'cor_borda': _cor_borda(ctx, tbl, estilo)}


# ---------------------------------------------------------------------- API

def montar_layout(docx_bytes):
    doc = Document(io.BytesIO(docx_bytes))
    ctx = _Contexto(doc)
    secao = doc.sections[0]
    pagina = {
        'largura': (secao.page_width or 7560310) / EMU_POR_PT,
        'altura': (secao.page_height or 10692130) / EMU_POR_PT,
        'margem_esq': (secao.left_margin or 0) / EMU_POR_PT,
        'margem_dir': (secao.right_margin or 0) / EMU_POR_PT,
        'margem_sup': (secao.top_margin or 0) / EMU_POR_PT,
    }
    blocos = []
    for el in doc.element.body:
        if el.tag == qn('w:p'):
            antes, depois = _espacamento(el)
            imagens, formas = _imagens_e_formas(ctx, el)
            blocos.append({'tipo': 'p', 'alinhamento': _alinhamento(el), 'antes': antes, 'depois': depois,
                           'recuo': _recuo(el),
                           'runs': _runs(ctx, el, {}), 'tamanho_vazio': _tamanho_marca(ctx, el, {}),
                           'imagens': imagens, 'formas': formas})
        elif el.tag == qn('w:tbl'):
            blocos.append(_tabela(ctx, el))
    return {'pagina': pagina, 'blocos': blocos}
