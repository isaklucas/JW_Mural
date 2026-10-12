"""Renderizador de minutas: minuta (dict) + MODELO (.docx oficial, bytes) + dados -> .docx (bytes).

O modelo é o próprio documento oficial (com imagem, título, cores, fontes). Nada
de layout é recriado: o renderizador

1. mantém intacto tudo que vem ANTES da primeira tabela (cabeçalho: imagem,
   título, linhas decorativas) — opcionalmente trocando só o texto do título;
2. usa as tabelas do modelo como "carimbo": para cada mês, copia a tabela
   escolhida, troca o texto do título do mês e repete a primeira linha de dados
   uma vez por reunião.

A troca de texto preserva a formatação por trecho: "Setembro – Saindo - Congregação
Jacaré" com "Setembro" preto 14pt e o resto azul 12pt vira "Novembro – Saindo -
Congregação X" com as mesmas cores/tamanhos nas mesmas posições.

Função pura: não lê nem grava arquivo, não fala com banco.

`dados` esperado:

    {"congregacao": "...", "dirigente": "...",
     "meses": [{"ano": 2026, "mes": 11, "congregacao_recebendo": "...", "congregacao_saindo": "...",
                "semanas": [{"data": "2026-11-07", "presidente": ..., ...}, ...]}, ...]}
"""
import copy
import datetime
import difflib
import io
import logging
import re

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

from process.minutas.periodo import MESES_PT, nome_periodo

logger = logging.getLogger(__name__)

_VARIAVEL = re.compile(r"\{(\w+)\}")
# Título que terminou em "… - Congregação " porque a variável estava vazia.
_CONGREGACAO_PENDURADA = re.compile(r"[\s\-–—:]*Congrega[çc][ãa]o[\s\-–—:]*$")
# Elementos de run que não são texto (imagem, forma): esses runs nunca são tocados.
_NAO_TEXTO = (qn('w:drawing'), qn('w:pict'), qn('w:object'),
              '{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent')
# Marcas de revisão que não podem ir para o rPr de um run novo.
_RPR_PROIBIDOS = (qn('w:ins'), qn('w:del'), qn('w:moveFrom'), qn('w:moveTo'), qn('w:rPrChange'))


# ----------------------------------------------------------------- texto/XML

def _eh_run_de_texto(r):
    return r.find(qn('w:t')) is not None and not any(r.find('.//' + t) is not None for t in _NAO_TEXTO)


def _runs_de_texto(p):
    """Runs com texto do parágrafo, em ordem (inclusive dentro de hyperlinks)."""
    return [r for r in p.iter(qn('w:r')) if _eh_run_de_texto(r)]


def _texto_run(r):
    return ''.join(t.text or '' for t in r.iter(qn('w:t')))


def texto_paragrafo(p):
    return ''.join(_texto_run(r) for r in _runs_de_texto(p))


def texto_celula(tc):
    return '\n'.join(t for t in (texto_paragrafo(p) for p in tc.iter(qn('w:p'))) if t)


def _novo_run(rpr, texto):
    r = OxmlElement('w:r')
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = OxmlElement('w:t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = texto
    r.append(t)
    return r


def _rpr_da_marca(p):
    """rPr da marca de parágrafo (formatação de um parágrafo vazio)."""
    ppr = p.find(qn('w:pPr'))
    marca = ppr.find(qn('w:rPr')) if ppr is not None else None
    if marca is None:
        return None
    rpr = OxmlElement('w:rPr')
    for filho in marca:
        if filho.tag not in _RPR_PROIBIDOS:
            rpr.append(copy.deepcopy(filho))
    return rpr


def _mapear_formatacao(original, dono, novo):
    """Para cada caractere de `novo`, o índice do run de origem cuja formatação usar."""
    if not original:
        return [None] * len(novo)
    mapa = [0] * len(novo)
    sm = difflib.SequenceMatcher(None, original, novo, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(j2 - j1):
                mapa[j1 + k] = dono[i1 + k]
        elif tag == 'replace':
            n = i2 - i1
            for k in range(j2 - j1):
                mapa[j1 + k] = dono[i1 + min(k * n // (j2 - j1), n - 1)]
        elif tag == 'insert':
            origem = dono[min(max(i1 - 1, 0), len(dono) - 1)]
            for k in range(j2 - j1):
                mapa[j1 + k] = origem
    return mapa


def definir_texto_paragrafo(p, novo):
    """Troca o texto do parágrafo preservando a formatação por trecho.
    Runs de imagem/forma ficam intactos; hyperlinks esvaziados são removidos."""
    runs = _runs_de_texto(p)
    textos = [_texto_run(r) for r in runs]
    original = ''.join(textos)
    if novo == original:
        return
    rprs = [r.find(qn('w:rPr')) for r in runs]

    if not runs:
        if novo:
            p.append(_novo_run(_rpr_da_marca(p), novo))
        return

    # Runs com formatação idêntica contam como um só (o Word fragmenta à toa: "0","3","/08").
    assinaturas = [etree.tostring(r) if r is not None else b'' for r in rprs]
    canonico = [assinaturas.index(a) for a in assinaturas]
    dono = [canonico[i] for i, t in enumerate(textos) for _ in t]
    mapa = _mapear_formatacao(original, dono, novo)
    grupos = []  # [(indice_run, texto)]
    for ch, i in zip(novo, mapa):
        if grupos and grupos[-1][0] == i:
            grupos[-1] = (i, grupos[-1][1] + ch)
        else:
            grupos.append((i, ch))

    # Ponto de inserção: o filho direto do parágrafo que contém o primeiro run.
    ancora = runs[0]
    while ancora.getparent() is not p:
        ancora = ancora.getparent()
    for i, texto in grupos:
        rpr = rprs[i] if i is not None else rprs[0]
        ancora.addprevious(_novo_run(rpr, texto))
    for r in runs:
        pai = r.getparent()
        pai.remove(r)
        if pai is not p and pai.tag == qn('w:hyperlink') and not list(pai.iter(qn('w:r'))):
            pai.getparent().remove(pai)
    # Hyperlinks que sobraram em volta do texto novo não fazem sentido (link do dado antigo).
    for h in list(p.findall(qn('w:hyperlink'))):
        for filho in list(h):
            h.addprevious(filho)
        p.remove(h)


def definir_texto_celula(tc, novo):
    """Texto da célula no 1º parágrafo com texto; outros parágrafos com texto saem
    (parágrafos vazios de espaçamento ficam)."""
    paragrafos = tc.findall(qn('w:p'))
    if not paragrafos:
        p = OxmlElement('w:p')
        tc.append(p)
        paragrafos = [p]
    com_texto = [p for p in paragrafos if _runs_de_texto(p)]
    alvo = com_texto[0] if com_texto else paragrafos[0]
    for p in com_texto[1:]:
        tc.remove(p)
    definir_texto_paragrafo(alvo, novo)


def _celulas(tr):
    return tr.findall(qn('w:tc'))


# ------------------------------------------------------------------- valores

def substituir_variaveis(texto, contexto):
    """Troca `{nome}` pelo valor do contexto; variável desconhecida vira vazio.
    Se o título terminar pendurado em "Congregação" (variável vazia), apara."""
    vazia = [False]

    def _troca(m):
        valor = contexto.get(m.group(1), '')
        valor = '' if valor is None else str(valor)
        if not valor.strip():
            vazia[0] = True
        return valor

    resultado = _VARIAVEL.sub(_troca, texto or '')
    if vazia[0]:
        resultado = _CONGREGACAO_PENDURADA.sub('', resultado).rstrip(' -–—:')
    return resultado.strip()


def _formatar_data(iso):
    try:
        return datetime.date.fromisoformat(iso).strftime('%d/%m/%Y')
    except (TypeError, ValueError):
        return iso or ''


def valor_campo(campo, semana, dados):
    """Texto da célula para `campo` (ver padrao.CAMPOS). Campo vazio = coluna em branco."""
    if not campo:
        return ''
    if campo == 'data':
        return _formatar_data(semana.get('data'))
    if campo == 'dirigente':
        return (dados.get('dirigente') or '').strip()
    if campo == 'dirigente_leitor':
        partes = [(dados.get('dirigente') or '').strip(), (semana.get('leitor_sentinela') or '').strip()]
        return ' / '.join(p for p in partes if p)
    valor = semana.get(campo, '')
    return '' if valor is None else str(valor).strip()


def tabela_vazia(spec, semanas, dados):
    """True se nenhuma coluna de conteúdo (tudo menos a data) tem valor."""
    campos = [c for c in spec.get('campos', []) if c and c != 'data']
    return not any(valor_campo(c, s, dados) for s in semanas for c in campos)


# -------------------------------------------------------------------- modelo

def _partes_do_modelo(doc):
    body = doc.element.body
    filhos = [el for el in body if el.tag != qn('w:sectPr')]
    tabelas = [el for el in filhos if el.tag == qn('w:tbl')]
    return body, filhos, tabelas


def descrever_modelo(modelo_bytes):
    """O que o editor precisa saber do modelo: textos do cabeçalho e, por tabela,
    o título, os rótulos das colunas e quantas colunas tem a linha de dados."""
    doc = Document(io.BytesIO(modelo_bytes))
    _, filhos, tabelas = _partes_do_modelo(doc)
    if not tabelas:
        return {'cabecalho': [], 'tabelas': []}
    primeiro = filhos.index(tabelas[0])
    cabecalho = [texto_paragrafo(p) for p in filhos[:primeiro]
                 if p.tag == qn('w:p') and texto_paragrafo(p).strip()]
    descricao = []
    for i, tbl in enumerate(tabelas):
        linhas = tbl.findall(qn('w:tr'))
        titulo = ' '.join(texto_celula(linhas[0]).split()) if linhas else ''
        rotulos = [' '.join(texto_celula(tc).split()) for tc in _celulas(linhas[1])] if len(linhas) > 1 else []
        n = len(_celulas(linhas[2])) if len(linhas) > 2 else len(rotulos)
        descricao.append({'indice': i, 'titulo': titulo, 'colunas': rotulos[:n] + [''] * (n - len(rotulos)),
                          'n_colunas': n, 'linhas': len(linhas)})
    return {'cabecalho': cabecalho, 'tabelas': descricao}


def validar_modelo(modelo_bytes):
    """Erro legível se o .docx não serve de modelo; None se serve."""
    try:
        desc = descrever_modelo(modelo_bytes)
    except Exception as e:  # python-docx levanta vários tipos para arquivo inválido
        return f"Arquivo não é um documento Word (.docx) válido: {e}"
    if not desc['tabelas']:
        return "O documento não tem nenhuma tabela para servir de modelo."
    if not any(t['linhas'] >= 3 for t in desc['tabelas']):
        return "As tabelas precisam ter título, cabeçalho e ao menos uma linha de exemplo."
    return None


def _linha_modelo(linhas, indice):
    """Cópia da linha de dados `indice`. Coluna vazia nela herda a célula da primeira
    linha seguinte (do mesmo bloco) que tenha texto — assim a formatação de exemplo
    vem de uma célula preenchida."""
    base = copy.deepcopy(linhas[indice])
    celulas = _celulas(base)
    for c, tc in enumerate(celulas):
        if texto_celula(tc):
            continue
        for tr in linhas[indice + 1:]:
            outras = _celulas(tr)
            if len(outras) != len(celulas) or not any(texto_celula(x) for x in outras):
                break
            if texto_celula(outras[c]):
                substituta = copy.deepcopy(outras[c])
                tcpr_base = tc.find(qn('w:tcPr'))
                tcpr_nova = substituta.find(qn('w:tcPr'))
                if tcpr_base is not None:  # largura/mesclagem da coluna original
                    if tcpr_nova is not None:
                        substituta.remove(tcpr_nova)
                    substituta.insert(0, copy.deepcopy(tcpr_base))
                tc.addprevious(substituta)
                base.remove(tc)
                break
    return base


def _tabela_preenchida(prototipo, spec, semanas, contexto, dados):
    tbl = copy.deepcopy(prototipo)
    linhas = tbl.findall(qn('w:tr'))
    li = int(spec.get('linha_dados', 2))
    if len(linhas) <= li:
        raise ValueError(f"Tabela {spec.get('modelo')} do modelo não tem linha de dados {li}.")
    modelo_dados = _linha_modelo(linhas, li)
    for tr in linhas[li:]:
        tbl.remove(tr)

    titulo = spec.get('titulo')
    if titulo and linhas:
        celulas_titulo = _celulas(linhas[0])
        if celulas_titulo:
            definir_texto_celula(celulas_titulo[0], substituir_variaveis(titulo, contexto))

    campos = spec.get('campos', [])
    for semana in semanas:
        tr = copy.deepcopy(modelo_dados)
        for i, tc in enumerate(_celulas(tr)):
            campo = campos[i] if i < len(campos) else ''
            definir_texto_celula(tc, valor_campo(campo, semana, dados))
        tbl.append(tr)
    return tbl


# ----------------------------------------------------------------------- API

def renderizar(minuta, modelo_bytes, dados):
    """Monta o documento a partir do modelo e devolve os bytes do .docx."""
    if not modelo_bytes:
        raise ValueError("Minuta sem arquivo modelo.")
    doc = Document(io.BytesIO(modelo_bytes))
    body, filhos, tabelas = _partes_do_modelo(doc)
    if not tabelas:
        raise ValueError("O arquivo modelo não tem tabelas.")

    primeiro, ultimo = filhos.index(tabelas[0]), filhos.index(tabelas[-1])
    cabecalho, rodape = filhos[:primeiro], filhos[ultimo + 1:]
    prototipos = {}
    for i, tbl in enumerate(tabelas):
        pos = filhos.index(tbl)
        anterior = filhos[pos - 1] if pos > 0 else None
        separador = None
        if anterior is not None and anterior.tag == qn('w:p') and not _runs_de_texto(anterior) \
                and anterior.find('.//' + qn('w:drawing')) is None:
            separador = copy.deepcopy(anterior)
        prototipos[i] = (copy.deepcopy(tbl), separador)
    for el in filhos[primeiro:]:
        body.remove(el)

    meses = dados.get('meses') or []
    contexto_geral = {
        'congregacao': dados.get('congregacao', ''),
        'periodo': nome_periodo([(m['ano'], m['mes']) for m in meses]),
    }

    # Cabeçalho: troca só o texto dos parágrafos (imagem e linhas ficam).
    paragrafos_cab = [p for p in cabecalho if p.tag == qn('w:p') and texto_paragrafo(p).strip()]
    for p, novo in zip(paragrafos_cab, minuta.get('cabecalho') or []):
        if novo and novo.strip():
            definir_texto_paragrafo(p, substituir_variaveis(novo, contexto_geral))

    sect_pr = body.find(qn('w:sectPr'))

    def adicionar(el):
        if sect_pr is not None:
            sect_pr.addprevious(el)
        else:
            body.append(el)

    primeira = True
    for mes in meses:
        semanas = mes.get('semanas') or []
        if not semanas:
            continue
        contexto = {
            **contexto_geral,
            'mes': MESES_PT.get(mes.get('mes'), str(mes.get('mes', ''))),
            'ano': mes.get('ano', ''),
            'congregacao_recebendo': mes.get('congregacao_recebendo', ''),
            'congregacao_saindo': mes.get('congregacao_saindo', ''),
        }
        for spec in minuta.get('tabelas', []):
            indice = spec.get('modelo')
            if indice not in prototipos:
                logger.warning("Minuta '%s': tabela %s não existe no modelo; bloco ignorado.",
                               minuta.get('chave'), indice)
                continue
            if spec.get('omitir_se_vazio') and tabela_vazia(spec, semanas, dados):
                continue
            prototipo, separador = prototipos[indice]
            if not primeira:
                adicionar(copy.deepcopy(separador) if separador is not None else OxmlElement('w:p'))
            adicionar(_tabela_preenchida(prototipo, spec, semanas, contexto, dados))
            primeira = False

    for el in rodape:
        adicionar(el)
    if not rodape:
        adicionar(OxmlElement('w:p'))  # Word exige parágrafo depois da última tabela

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def dados_de_exemplo(congregacao="Minha Congregação"):
    """Dados fictícios para a pré-visualização no editor de minutas."""
    from process.minutas.periodo import montar_periodo

    hoje = datetime.date.today()
    meses = montar_periodo(hoje.year, hoje.month, 2)
    for m in meses:
        m['congregacao_recebendo'] = congregacao
        m['congregacao_saindo'] = 'Vizinha'
        for i, s in enumerate(m['semanas'], start=1):
            s.update({
                'titulo_estudo': f'Título do estudo da semana {i}',
                'tema_discurso': f'Tema do discurso público {i}',
                'orador': f'Orador {i}',
                'presidente': f'Presidente {i}',
                'leitor_sentinela': f'Leitor {i}',
                'orador_saindo': f'Orador saindo {i}' if i % 2 else '',
                'tema_saindo': f'Tema saindo {i}' if i % 2 else '',
            })
    return {'congregacao': congregacao, 'dirigente': 'Dirigente', 'meses': meses}
