"""Integração: CRUD básico de publicadores via db_ops real (mongomock)."""


def _nomes(db_ops):
    return sorted(p["nome"] for p in db_ops.getAllPub())


def test_post_cria_publicador_com_historico_vazio(db_ops):
    db_ops.post("joao silva", batizado=True, sexo="Masculino")
    pubs = db_ops.getAllPub()
    assert len(pubs) == 1
    p = pubs[0]
    assert p["nome"] == "Joao Silva"       # TitleCase aplicado
    assert p["sexo"] == "Masculino"
    assert p["historico"] == []


def test_delete_remove_publicador(db_ops):
    db_ops.post("ana lima", batizado=True)
    db_ops.post("bruno rocha", batizado=True)
    db_ops.delete("ana lima")
    assert _nomes(db_ops) == ["Bruno Rocha"]


def test_delete_inexistente_nao_quebra(db_ops):
    db_ops.post("ana lima", batizado=True)
    db_ops.delete("nao existe")            # não deve levantar
    assert _nomes(db_ops) == ["Ana Lima"]


def test_buscar_historico_publicador_vazio(db_ops):
    db_ops.post("ana lima", batizado=True)
    assert db_ops.buscar_historico_publicador("Ana Lima") == []
