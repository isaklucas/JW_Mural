"""Taxonomia das partes gravadas no `historico` de cada publicador.

O `historico` de um publicador é uma lista única de entradas
`{"parte": <str>, "data": <str>}` que mistura DUAS coisas conceitualmente
diferentes. Este módulo é a ÚNICA fonte da verdade sobre essa separação —
qualquer contagem, relatório ou dashboard deve classificar as partes daqui,
nunca com listas literais espalhadas pelo código.

1. PARTICIPAÇÃO NA REUNIÃO (`PARTES_PARTICIPACAO`)
   O publicador participa do programa da reunião: preside, ora, ensina, lê,
   faz uma parte da escola etc. Dividida em:
   - `PARTES_MEIO_SEMANA` — programa da reunião de meio de semana (S140).
   - `PARTES_FINAL_SEMANA` — programa da reunião de fim de semana.
   Cada uma tem o seu próprio dashboard e as contagens NÃO se somam:
   - meio de semana -> "Participações por Publicador" / "Participações por Reunião"
   - fim de semana  -> "Participações Final de Semana"

2. DESIGNAÇÃO DE TRABALHO (`PARTES_SALAO`)
   O publicador trabalha para a reunião acontecer (áudio, vídeo, microfone,
   indicador). NÃO é participação no programa: nunca entra nos dashboards de
   participação — aparece exclusivamente no dashboard "Designações Salão".

Regra de ouro: ao criar uma parte nova, registre-a numa das listas abaixo.
Se ela não estiver em nenhuma, `eh_designacao_trabalho()` a trata como
participação (comportamento conservador para partes antigas do banco).
"""

# --- 1. Participação no programa da reunião -------------------------------

PARTES_ORACAO = (
    "Oração Inicial",
    "Oração Final",
)

PARTES_MEIO_SEMANA = (
    "Presidente",
    "Oração Inicial",
    "Tesouro",
    "Joias Espirituais",
    "Leitura da Bíblia",
    "Escola - Primeira Parte",
    "Escola - Segunda Parte",
    "Escola - Terceira Parte",
    "Escola - Quarta Parte",
    "Nossa Vida Cristã - Primeira Parte",
    "Nossa Vida Cristã - Segunda Parte",
    "Estudo de Congregação",
    "Oração Final",
)

PARTE_FS_LEITURA_SENTINELA = "Leitura Sentinela"
PARTE_FS_PRESIDENTE = "Presidente Final Semana"

PARTES_FINAL_SEMANA = (
    PARTE_FS_LEITURA_SENTINELA,
    PARTE_FS_PRESIDENTE,
)

PARTES_PARTICIPACAO = PARTES_MEIO_SEMANA + PARTES_FINAL_SEMANA

# Onde cada parte de meio de semana mora no documento da collection `reunioes`.
# Usado para manter reunião e histórico em sincronia quando uma participação é
# removida ou passada para outro publicador.
CAMPO_REUNIAO_POR_PARTE = {
    "Presidente": ("presidente",),
    "Oração Inicial": ("oracao_inicial",),
    "Tesouro": ("tesouro",),
    "Joias Espirituais": ("joias_espirituais",),
    "Leitura da Bíblia": ("leitura_biblia",),
    "Escola - Primeira Parte": ("escola", "primeira_parte"),
    "Escola - Segunda Parte": ("escola", "segunda_parte"),
    "Escola - Terceira Parte": ("escola", "terceira_parte"),
    "Escola - Quarta Parte": ("escola", "quarta_parte"),
    "Nossa Vida Cristã - Primeira Parte": ("nossa_vida_crista", "primeira_parte"),
    "Nossa Vida Cristã - Segunda Parte": ("nossa_vida_crista", "segunda_parte"),
    "Estudo de Congregação": ("estudo_congregacao",),
    "Oração Final": ("oracao_final",),
}

# Valor gravado num campo de participante quando ninguém está designado.
SEM_PARTICIPANTE = "não possui"

# --- 2. Designação de trabalho (salão) ------------------------------------

PARTE_SALAO_AUDIO = "Salão - Áudio"
PARTE_SALAO_VIDEO = "Salão - Vídeo"
PARTE_SALAO_MICROFONE = "Salão - Microfone"
PARTE_SALAO_INDICADOR = "Salão - Indicador"

PARTES_SALAO = (
    PARTE_SALAO_AUDIO,
    PARTE_SALAO_VIDEO,
    PARTE_SALAO_MICROFONE,
    PARTE_SALAO_INDICADOR,
)

# Prefixo usado pelas partes de salão. Serve de rede de segurança para partes
# de trabalho futuras que ainda não tenham sido adicionadas a `PARTES_SALAO`.
PREFIXO_SALAO = "Salão - "


def eh_designacao_trabalho(parte):
    """True se `parte` é designação de trabalho (salão), não participação."""
    if not parte:
        return False
    return parte in PARTES_SALAO or str(parte).startswith(PREFIXO_SALAO)


def eh_participacao_reuniao(parte):
    """True se `parte` é participação no programa da reunião."""
    return bool(parte) and not eh_designacao_trabalho(parte)


def somente_participacoes(historico):
    """Filtra o histórico deixando só participações no programa da reunião."""
    return [h for h in (historico or []) if eh_participacao_reuniao(h.get('parte'))]


def somente_designacoes_trabalho(historico):
    """Filtra o histórico deixando só designações de trabalho (salão)."""
    return [h for h in (historico or []) if eh_designacao_trabalho(h.get('parte'))]


def eh_participacao_final_semana(parte):
    """True se `parte` é participação no programa da reunião de fim de semana."""
    return parte in PARTES_FINAL_SEMANA


def eh_participacao_meio_semana(parte):
    """True se `parte` é participação no programa da reunião de meio de semana.

    Conservador de propósito: qualquer participação que não seja de fim de
    semana conta como meio de semana, para partes antigas do banco (ou novas
    ainda não registradas aqui) não sumirem do dashboard.
    """
    return eh_participacao_reuniao(parte) and not eh_participacao_final_semana(parte)


def somente_meio_semana(historico):
    """Filtra o histórico deixando só participações do programa de meio de semana."""
    return [h for h in (historico or []) if eh_participacao_meio_semana(h.get('parte'))]


def somente_final_semana(historico):
    """Filtra o histórico deixando só participações do programa de fim de semana."""
    return [h for h in (historico or []) if eh_participacao_final_semana(h.get('parte'))]
