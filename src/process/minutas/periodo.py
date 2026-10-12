"""Datas do período (bimestre) da reunião de final de semana."""
import calendar
import datetime

SABADO = 5  # datetime.weekday(): segunda=0 ... sábado=5

MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

URL_MEETINGS = "https://wol.jw.org/{idioma}/wol/meetings/r5/lp-t/{ano}/{semana}"


def meses_do_periodo(ano, mes, qtd_meses=2):
    """[(ano, mes), ...] a partir de (ano, mes), virando o ano se preciso."""
    resultado = []
    for i in range(qtd_meses):
        indice = (mes - 1) + i
        resultado.append((ano + indice // 12, indice % 12 + 1))
    return resultado


def dias_da_reuniao(ano, mes, dia_semana=SABADO):
    """Todas as datas do mês que caem no dia da reunião (padrão: sábado)."""
    _, ultimo = calendar.monthrange(ano, mes)
    return [
        datetime.date(ano, mes, d)
        for d in range(1, ultimo + 1)
        if datetime.date(ano, mes, d).weekday() == dia_semana
    ]


def url_semana_wol(data, idioma="pt"):
    """URL da semana no wol.jw.org. O site usa a semana ISO (seg–dom) no caminho:
    `.../lp-t/2026/45` = 2–8 de novembro de 2026. Usa o ano ISO, não o civil
    (sábado 2/1/2027 ainda é a semana 53 de 2026)."""
    ano_iso, semana_iso, _ = data.isocalendar()
    return URL_MEETINGS.format(idioma=idioma, ano=ano_iso, semana=semana_iso)


def rotulo_data(data):
    """'7 de novembro de 2026' — também é a chave `data` do histórico do publicador."""
    return f"{data.day} de {MESES_PT[data.month].lower()} de {data.year}"


def nome_periodo(meses):
    """'Novembro–Dezembro 2026' ou 'Dezembro 2026–Janeiro 2027'."""
    if not meses:
        return ""
    (a1, m1), (a2, m2) = meses[0], meses[-1]
    if len(meses) == 1:
        return f"{MESES_PT[m1]} {a1}"
    if a1 == a2:
        return f"{MESES_PT[m1]}–{MESES_PT[m2]} {a1}"
    return f"{MESES_PT[m1]} {a1}–{MESES_PT[m2]} {a2}"


def semana_vazia(data):
    """Estrutura de uma semana no modo Minutas (compatível com o modo legado:
    `semana`, `titulo_estudo`, `presidente`, `leitor_sentinela`, `orador`,
    `tema_discurso` têm o mesmo significado)."""
    rotulo = rotulo_data(data)
    return {
        'data': data.isoformat(),
        'semana': rotulo,
        'data_historico': rotulo,
        'titulo_estudo': '',
        'tema_discurso': '',
        'orador': '',
        'presidente': '',
        'leitor_sentinela': '',
        'orador_saindo': '',
        'tema_saindo': '',
    }


def montar_periodo(ano, mes, qtd_meses=2, dia_semana=SABADO):
    """Esqueleto do período: lista de meses, cada um com as suas semanas vazias."""
    return [
        {
            'ano': a,
            'mes': m,
            'congregacao_recebendo': '',
            'congregacao_saindo': '',
            'semanas': [semana_vazia(d) for d in dias_da_reuniao(a, m, dia_semana)],
        }
        for a, m in meses_do_periodo(ano, mes, qtd_meses)
    ]
