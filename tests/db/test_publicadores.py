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


def test_post_colapsa_espacos_no_nome(db_ops):
    db_ops.post("  josé   da   SILVA ", batizado=True)
    assert _nomes(db_ops) == ["José Da Silva"]


def test_post_nao_duplica_por_acento_ou_espaco(db_ops):
    db_ops.post("José da Silva", batizado=True)
    db_ops.post("jose  da silva", batizado=True)
    db_ops.post("JOSÉ DA SILVA ", batizado=True)
    assert _nomes(db_ops) == ["José Da Silva"]


def test_busca_resolve_nome_sem_acento(db_ops):
    db_ops.post("José da Silva", batizado=True)
    db_ops.update_parte("jose da silva", "Presidente", "Semana 1")
    historico = db_ops.buscar_historico_publicador("JOSE  DA SILVA")
    assert [h["parte"] for h in historico] == ["Presidente"]


def test_delete_resolve_nome_sem_acento(db_ops):
    db_ops.post("José da Silva", batizado=True)
    db_ops.delete("jose da silva")
    assert _nomes(db_ops) == []


def test_update_parte_cria_publicador_desconhecido_sem_dialogo(db_ops, monkeypatch):
    # Antes isso abria `janelas.verificarInclusaoPublicador` (uma Toplevel a partir
    # de thread de background). Agora cria direto — se algo ainda importar util.janelas
    # daqui, o import falso abaixo estoura o teste.
    import sys
    import types

    proibido = types.ModuleType("util.janelas")

    def _boom(nome):
        raise AssertionError("nenhuma janela deveria ser aberta ao criar publicador")

    proibido.__getattr__ = _boom
    monkeypatch.setitem(sys.modules, "util.janelas", proibido)

    db_ops.update_parte("Novo Irmao", "Presidente", "Semana 1")

    assert _nomes(db_ops) == ["Novo Irmao"]
    pub = db_ops.getAllPub()[0]
    assert pub["batizado"] is True
    assert [h["parte"] for h in pub["historico"]] == ["Presidente"]
