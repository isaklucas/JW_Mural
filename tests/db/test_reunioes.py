"""Integração: salvar reunião de meio de semana atualiza o histórico dos participantes."""
import pytest


def _dados_reuniao(ano=2026, semana="Semana 1", **partes):
    # Todas as partes começam "não possui" (o gerador de histórico ignora esse
    # valor). Cada teste sobrescreve só as partes que quer exercitar — assim não
    # semeamos publicadores desnecessários nem disparamos o diálogo de inclusão.
    base = {
        "ano": ano,
        "semana": semana,
        "data_reuniao": "5-11 de janeiro",
        "presidente": "não possui",
        "oracao_inicial": "não possui",
        "tesouro": "não possui",
        "joias_espirituais": "não possui",
        "leitura_biblia": "não possui",
        "escola": {
            "primeira_parte": "não possui",
            "segunda_parte": "não possui",
            "terceira_parte": "não possui",
            "quarta_parte": "não possui",
        },
        "nossa_vida_crista": {
            "primeira_parte": "não possui",
            "segunda_parte": "não possui",
        },
        "estudo_congregacao": "não possui",
        "oracao_final": "não possui",
    }
    base.update(partes)
    return base


def _partes(db_ops, nome):
    return sorted(h["parte"] for h in db_ops.buscar_historico_publicador(nome))


def test_salvar_reuniao_persiste_e_retorna_insert(db_ops):
    db_ops.post("Presidente X", batizado=True)
    res = db_ops.salvar_reuniao(_dados_reuniao(presidente="Presidente X"))
    assert res["success"] is True
    assert res["operacao"] == "insert"
    assert db_ops.buscar_reuniao(2026, "SEMANA 1") is not None  # semana normalizada p/ maiúsculo


def test_salvar_reuniao_atualiza_historico_participantes(db_ops):
    db_ops.post("Presidente X", batizado=True)
    db_ops.post("Leitor L", batizado=True)
    db_ops.salvar_reuniao(_dados_reuniao(presidente="Presidente X", leitura_biblia="Leitor L"))
    assert _partes(db_ops, "Presidente X") == ["Presidente"]
    assert _partes(db_ops, "Leitor L") == ["Leitura da Bíblia"]


def test_resalvar_reuniao_e_update_sem_duplicar_historico(db_ops):
    db_ops.post("Presidente X", batizado=True)
    db_ops.salvar_reuniao(_dados_reuniao(presidente="Presidente X"))
    res = db_ops.salvar_reuniao(_dados_reuniao(presidente="Presidente X"))  # mesma semana de novo
    assert res["operacao"] == "update"
    # _atualizar_historico_individual dedupa (parte, data) → sem duplicata.
    assert _partes(db_ops, "Presidente X") == ["Presidente"]


def test_participante_com_barra_conta_para_os_dois(db_ops):
    db_ops.post("Ana", batizado=True)
    db_ops.post("Bia", batizado=True)
    db_ops.salvar_reuniao(_dados_reuniao(leitura_biblia="Ana / Bia"))
    assert _partes(db_ops, "Ana") == ["Leitura da Bíblia"]
    assert _partes(db_ops, "Bia") == ["Leitura da Bíblia"]
