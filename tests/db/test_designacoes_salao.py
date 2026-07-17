"""Integração: designações do salão (salvar / editar / excluir) e o histórico.

O foco é a REGRESSÃO corrigida: ao reeditar e salvar de novo uma designação já
gravada, a pessoa trocada tem de SAIR do histórico e não pode duplicar entradas.
"""
import pytest


def _hist(db_ops, nome):
    """Histórico de um publicador como lista de (parte, data)."""
    return [(h.get("parte"), h.get("data")) for h in db_ops.buscar_historico_publicador(nome)]


def _dados(semanas, ano=2026, mes=3):
    return {"ano": ano, "mes": mes, "dia_semana": "Terça", "dia_fds": "Domingo",
            "semanas": semanas}


def _semana(data, audio="", video="", microfone="", indicadores="", tipo="meio"):
    return {"data": data, "tipo": tipo, "audio": audio, "video": video,
            "microfone": microfone, "indicadores": indicadores}


def test_salvar_gera_historico_por_papel(db_ops, seed):
    seed(["Alfa", "Bravo", "Charlie", "Delta"])
    res = db_ops.salvar_designacoes_salao(_dados([
        _semana("Semana 1", audio="Alfa", video="Bravo",
                microfone="Charlie / Delta", indicadores="Alfa"),
    ]))
    assert res["success"] is True
    assert _hist(db_ops, "Alfa") == [("Salão - Áudio", "Semana 1"), ("Salão - Indicador", "Semana 1")]
    assert _hist(db_ops, "Bravo") == [("Salão - Vídeo", "Semana 1")]
    assert _hist(db_ops, "Charlie") == [("Salão - Microfone", "Semana 1")]
    assert _hist(db_ops, "Delta") == [("Salão - Microfone", "Semana 1")]


def test_reeditar_troca_pessoa_remove_do_historico(db_ops, seed):
    """REGRESSÃO: trocar o áudio de Alfa->Echo e resalvar remove Alfa e adiciona Echo,
    sem duplicar as entradas dos que não mudaram."""
    seed(["Alfa", "Bravo", "Charlie", "Delta", "Echo"])
    dados = _dados([
        _semana("Semana 1", audio="Alfa", video="Bravo",
                microfone="Charlie / Delta", indicadores="Alfa"),
    ])
    db_ops.salvar_designacoes_salao(dados)

    # Edita: áudio Alfa -> Echo, indicador Alfa -> Bravo. Resalva.
    dados["semanas"][0]["audio"] = "Echo"
    dados["semanas"][0]["indicadores"] = "Bravo"
    db_ops.salvar_designacoes_salao(dados)

    # Alfa saiu totalmente do histórico daquela semana.
    assert _hist(db_ops, "Alfa") == []
    # Echo entrou como áudio.
    assert _hist(db_ops, "Echo") == [("Salão - Áudio", "Semana 1")]
    # Bravo agora é vídeo E indicador — sem duplicar o vídeo.
    assert sorted(_hist(db_ops, "Bravo")) == [("Salão - Indicador", "Semana 1"),
                                              ("Salão - Vídeo", "Semana 1")]
    # Charlie/Delta não mudaram e não podem ter duplicado.
    assert _hist(db_ops, "Charlie") == [("Salão - Microfone", "Semana 1")]
    assert _hist(db_ops, "Delta") == [("Salão - Microfone", "Semana 1")]


def test_resalvar_identico_nao_duplica(db_ops, seed):
    seed(["Alfa", "Bravo"])
    dados = _dados([_semana("Semana 1", audio="Alfa", video="Bravo")])
    db_ops.salvar_designacoes_salao(dados)
    db_ops.salvar_designacoes_salao(dados)  # de novo, idêntico
    assert _hist(db_ops, "Alfa") == [("Salão - Áudio", "Semana 1")]
    assert _hist(db_ops, "Bravo") == [("Salão - Vídeo", "Semana 1")]


def test_datas_diferentes_nao_se_afetam(db_ops, seed):
    """Reeditar a Semana 1 não pode mexer no histórico da Semana 2."""
    seed(["Alfa", "Bravo"])
    dados = _dados([
        _semana("Semana 1", audio="Alfa"),
        _semana("Semana 2", audio="Bravo"),
    ])
    db_ops.salvar_designacoes_salao(dados)
    # Troca só a Semana 1.
    dados["semanas"][0]["audio"] = "Bravo"
    db_ops.salvar_designacoes_salao(dados)
    assert _hist(db_ops, "Alfa") == []
    assert sorted(_hist(db_ops, "Bravo")) == [("Salão - Áudio", "Semana 1"),
                                              ("Salão - Áudio", "Semana 2")]


def test_excluir_remove_doc_e_historico(db_ops, seed):
    seed(["Alfa", "Bravo"])
    dados = _dados([_semana("Semana 1", audio="Alfa", video="Bravo")])
    db_ops.salvar_designacoes_salao(dados)
    res = db_ops.excluir_designacoes_salao(2026, 3)
    assert res["success"] is True
    assert db_ops.buscar_designacoes_salao(2026, 3) is None
    assert _hist(db_ops, "Alfa") == []
    assert _hist(db_ops, "Bravo") == []


def test_buscar_e_listar(db_ops, seed):
    seed(["Alfa"])
    db_ops.salvar_designacoes_salao(_dados([_semana("Semana 1", audio="Alfa")], mes=3))
    db_ops.salvar_designacoes_salao(_dados([_semana("Semana 1", audio="Alfa")], mes=5))
    doc = db_ops.buscar_designacoes_salao(2026, 3)
    assert doc["mes"] == 3 and doc["semanas"][0]["audio"] == "Alfa"
    meses = [d["mes"] for d in db_ops.listar_designacoes_salao()]
    assert meses == [3, 5]  # ordenado por ano/mês


def test_contar_designacoes_por_publicador(db_ops, seed):
    seed(["Alfa", "Bravo"])
    db_ops.salvar_designacoes_salao(_dados([
        _semana("Semana 1", audio="Alfa", microfone="Alfa / Bravo"),
        _semana("Semana 2", audio="Alfa"),
    ]))
    cont = db_ops.contar_designacoes_salao_por_publicador()
    assert cont["Alfa"] == {"audio": 2, "video": 0, "microfone": 1,
                            "indicadores": 0, "total": 3}
    assert cont["Bravo"]["microfone"] == 1
