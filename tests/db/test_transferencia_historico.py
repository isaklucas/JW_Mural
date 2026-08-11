"""Integração: transferir histórico de um publicador para outro.

Cenário real: participações foram gravadas no publicador errado. Mover só o array
`historico` não basta — resalvar a semana reconstrói o histórico a partir de
`reunioes`/`designacoes_salao`, então o nome precisa mudar lá também.
"""


def _dados_reuniao(ano=2026, semana="Semana 1", **partes):
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


def test_transferir_move_historico_e_zera_origem(db_ops):
    db_ops.post("Ana Lima", batizado=True)
    db_ops.post("Bruno Rocha", batizado=True)
    db_ops.update_parte("Ana Lima", "Presidente", "Semana 1")
    db_ops.update_parte("Ana Lima", "Oração Final", "Semana 2")

    res = db_ops.transferir_historico("Ana Lima", "Bruno Rocha")

    assert res["success"] is True
    assert res["entradas_transferidas"] == 2
    assert _partes(db_ops, "Ana Lima") == []
    assert _partes(db_ops, "Bruno Rocha") == ["Oração Final", "Presidente"]

    ana = next(p for p in db_ops.getAllPub() if p["nome"] == "Ana Lima")
    bruno = next(p for p in db_ops.getAllPub() if p["nome"] == "Bruno Rocha")
    assert ana["ultima_parte"] == ""
    assert bruno["ultima_parte"] != ""


def test_transferir_nao_duplica_entradas_iguais(db_ops):
    db_ops.post("Ana Lima", batizado=True)
    db_ops.post("Bruno Rocha", batizado=True)
    db_ops.update_parte("Ana Lima", "Presidente", "Semana 1")
    db_ops.update_parte("Bruno Rocha", "Presidente", "Semana 1")  # mesma parte+data

    res = db_ops.transferir_historico("Ana Lima", "Bruno Rocha")

    assert res["entradas_transferidas"] == 0
    assert _partes(db_ops, "Bruno Rocha") == ["Presidente"]


def test_transferir_resolve_nome_sem_acento(db_ops):
    db_ops.post("José da Silva", batizado=True)
    db_ops.post("Bruno Rocha", batizado=True)
    db_ops.update_parte("José da Silva", "Presidente", "Semana 1")

    res = db_ops.transferir_historico("jose  da silva", "BRUNO ROCHA")

    assert res["success"] is True
    assert _partes(db_ops, "Bruno Rocha") == ["Presidente"]


def test_transferir_troca_nome_na_reuniao_salva(db_ops):
    db_ops.post("Ana Lima", batizado=True)
    db_ops.post("Bruno Rocha", batizado=True)
    db_ops.salvar_reuniao(_dados_reuniao(presidente="Ana Lima"))

    res = db_ops.transferir_historico("Ana Lima", "Bruno Rocha")

    assert res["documentos_atualizados"] == 1
    reuniao = db_ops.buscar_reuniao(2026, "SEMANA 1")
    assert reuniao["presidente"] == "Bruno Rocha"


def test_transferir_troca_nome_em_campo_com_barra(db_ops):
    db_ops.post("Ana Lima", batizado=True)
    db_ops.post("Bruno Rocha", batizado=True)
    db_ops.post("Carla Dias", batizado=True)
    db_ops.salvar_reuniao(_dados_reuniao(leitura_biblia="Ana Lima / Carla Dias"))

    db_ops.transferir_historico("Ana Lima", "Bruno Rocha")

    reuniao = db_ops.buscar_reuniao(2026, "SEMANA 1")
    assert reuniao["leitura_biblia"] == "Bruno Rocha / Carla Dias"


def test_transferir_troca_nome_nas_designacoes_salao(db_ops):
    db_ops.post("Ana Lima", batizado=True)
    db_ops.post("Bruno Rocha", batizado=True)
    db_ops.salvar_designacoes_salao({
        "ano": 2026,
        "mes": 1,
        "semanas": [{"data": "5 de janeiro de 2026", "audio": "Ana Lima", "indicadores": "Ana Lima"}],
    })

    db_ops.transferir_historico("Ana Lima", "Bruno Rocha")

    doc = db_ops.buscar_designacoes_salao(2026, 1)
    assert doc["semanas"][0]["audio"] == "Bruno Rocha"
    assert doc["semanas"][0]["indicadores"] == "Bruno Rocha"
    assert _partes(db_ops, "Bruno Rocha") == sorted(["Salão - Áudio", "Salão - Indicador"])


def test_resalvar_reuniao_depois_da_transferencia_mantem_no_destino(db_ops):
    """Regressão: sem trocar o nome na reunião, resalvar devolvia o histórico à origem."""
    db_ops.post("Ana Lima", batizado=True)
    db_ops.post("Bruno Rocha", batizado=True)
    db_ops.salvar_reuniao(_dados_reuniao(presidente="Ana Lima"))
    db_ops.transferir_historico("Ana Lima", "Bruno Rocha")

    # Resalvar a semana: a tela relê a reunião do banco (já com o nome trocado)
    # e regrava com os mesmos dados que foram usados na primeira gravação.
    salva = db_ops.buscar_reuniao(2026, "SEMANA 1")
    assert salva["presidente"] == "Bruno Rocha"
    db_ops.salvar_reuniao(_dados_reuniao(presidente=salva["presidente"]))

    assert _partes(db_ops, "Ana Lima") == []
    assert _partes(db_ops, "Bruno Rocha") == ["Presidente"]


def test_transferir_sem_atualizar_reunioes(db_ops):
    db_ops.post("Ana Lima", batizado=True)
    db_ops.post("Bruno Rocha", batizado=True)
    db_ops.salvar_reuniao(_dados_reuniao(presidente="Ana Lima"))

    res = db_ops.transferir_historico("Ana Lima", "Bruno Rocha", atualizar_reunioes=False)

    assert res["documentos_atualizados"] == 0
    assert db_ops.buscar_reuniao(2026, "SEMANA 1")["presidente"] == "Ana Lima"


def test_transferir_falha_com_publicador_inexistente(db_ops):
    db_ops.post("Ana Lima", batizado=True)

    assert db_ops.transferir_historico("Ana Lima", "Ninguem")["success"] is False
    assert db_ops.transferir_historico("Ninguem", "Ana Lima")["success"] is False
    assert db_ops.transferir_historico("Ana Lima", "ana  lima")["success"] is False
