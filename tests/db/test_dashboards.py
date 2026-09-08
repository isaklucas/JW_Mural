"""Integração: as três categorias de parte têm dashboards disjuntos.

Meio de semana (programa do S140), fim de semana (Leitura Sentinela e
Presidente Final Semana) e trabalho de salão (Áudio/Vídeo/Microfone/Indicador)
são contados separadamente e nunca se somam.

REGRESSÃO corrigida: o dashboard "Participações por Publicador" somava salão —
e depois também fim de semana — junto com as partes do meio de semana.
A classificação vive em `database/partes.py`.
"""
import pytest


def _dados_salao(semanas, ano=2026, mes=3):
    return {"ano": ano, "mes": mes, "dia_semana": "Terça", "dia_fds": "Domingo",
            "semanas": semanas}


def _semana(data, audio="", video="", microfone="", indicadores="", tipo="meio"):
    return {"data": data, "tipo": tipo, "audio": audio, "video": video,
            "microfone": microfone, "indicadores": indicadores}


@pytest.fixture
def cenario(db_ops, seed):
    """Alfa: 2 partes de meio de semana + 1 de fim de semana + 3 de salão.
    Bravo: só salão. Charlie: só fim de semana."""
    seed(["Alfa", "Bravo", "Charlie"])
    db_ops.update_parte("Alfa", "Tesouro", "Semana 1")
    db_ops.update_parte("Alfa", "Oração Final", "Semana 1")
    db_ops.update_parte("Alfa", "Leitura Sentinela", "Semana 1")
    db_ops.update_parte("Charlie", "Presidente Final Semana", "Semana 1")
    db_ops.salvar_designacoes_salao(_dados_salao([
        _semana("Semana 1 de Março de 2026", audio="Alfa", video="Bravo",
                microfone="Alfa", indicadores="Alfa"),
    ]))
    return db_ops


def test_meio_de_semana_ignora_salao_e_final_de_semana(cenario):
    contagem = cenario.contar_participacoes_por_parte()
    assert contagem.get("Alfa") == 2          # só Tesouro + Oração Final
    assert "Bravo" not in contagem            # só fez trabalho de salão
    assert "Charlie" not in contagem          # só fez fim de semana


def test_filtro_sem_oracoes_continua_so_no_meio_de_semana(cenario):
    sem_oracoes = cenario.contar_participacoes_por_parte(parte="__EXCLUIR_ORACOES__")
    assert sem_oracoes.get("Alfa") == 1       # só Tesouro
    assert "Bravo" not in sem_oracoes
    assert "Charlie" not in sem_oracoes


def test_pedir_parte_de_outro_dashboard_retorna_vazio(cenario):
    assert cenario.contar_participacoes_por_parte(parte="Salão - Áudio") == {}
    assert cenario.contar_participacoes_por_parte(parte="Leitura Sentinela") == {}
    assert cenario.contar_participacoes_por_parte(parte="Presidente Final Semana") == {}


def test_final_de_semana_conta_so_sentinela_e_presidente(cenario):
    fds = cenario.contar_participacoes_final_semana_por_publicador()
    assert fds["Alfa"] == {"leitura_sentinela": 1, "presidente": 0, "total": 1}
    assert fds["Charlie"] == {"leitura_sentinela": 0, "presidente": 1, "total": 1}
    assert "Bravo" not in fds                 # só fez trabalho de salão


def test_designacoes_salao_contam_so_o_trabalho(cenario):
    salao = cenario.contar_designacoes_salao_por_publicador()
    assert salao["Alfa"] == {"audio": 1, "video": 0, "microfone": 1,
                             "indicadores": 1, "total": 3}
    assert salao["Bravo"]["total"] == 1


def test_participacoes_unicas_por_reuniao_nao_contam_salao(db_ops, seed):
    seed(["Alfa", "Bravo"])
    db_ops.salvar_reuniao({
        "ano": 2026, "semana": "Semana 1", "data_reuniao": "2 de Março de 2026",
        "presidente": "Alfa", "oracao_inicial": "não possui",
        "tesouro": "não possui", "joias_espirituais": "não possui",
        "leitura_biblia": "não possui",
        "escola": {"primeira_parte": "não possui", "segunda_parte": "não possui",
                   "terceira_parte": "não possui", "quarta_parte": "não possui"},
        "nossa_vida_crista": {"primeira_parte": "não possui", "segunda_parte": "não possui"},
        "estudo_congregacao": "não possui", "oracao_final": "não possui",
    })
    db_ops.salvar_designacoes_salao(_dados_salao([
        _semana("Semana 1 de Março de 2026", audio="Bravo"),
    ]))

    total, por_publicador = db_ops.contar_participacoes_unicas_por_reuniao()
    assert total == 1
    assert por_publicador.get("Alfa") == 1
    assert "Bravo" not in por_publicador
