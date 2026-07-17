"""Harness de testes de INTEGRAÇÃO da camada de dados (services -> db_ops -> Mongo).

O `tests/conftest.py` da raiz injeta um módulo `database` FALSO em `sys.modules`
para os testes de `process.*` rodarem offline. Aqui é o oposto: queremos exercitar
o `DatabaseOperations` REAL, mas sem um MongoDB de verdade. Para isso trocamos o
`pymongo.MongoClient` por `mongomock.MongoClient` (Mongo em memória) e importamos
o pacote `database` de verdade — fresco a cada teste, garantindo isolamento total
entre os testes (cada um começa com o banco vazio).

Ao final de cada teste o módulo falso é restaurado, para que a ordem de execução
não interfira nos testes de `process.*`.
"""
import sys

import mongomock
import pymongo
import pytest


def _remover_modulos_database():
    removidos = {
        nome: mod
        for nome, mod in sys.modules.items()
        if nome == "database" or nome.startswith("database.")
    }
    for nome in removidos:
        del sys.modules[nome]
    return removidos


@pytest.fixture
def db_ops(monkeypatch):
    """`DatabaseOperations` real ligado a um MongoDB em memória (mongomock).

    Cada teste recebe um banco limpo: removemos os módulos `database.*` do cache,
    trocamos o driver por mongomock e reimportamos — o que recria a conexão global
    (`db_connection`) contra um `mongomock.MongoClient` novo (store independente).
    """
    # Guarda o `database` falso da raiz para restaurar no teardown.
    fake_saved = _remover_modulos_database()

    monkeypatch.setattr(pymongo, "MongoClient", mongomock.MongoClient)
    monkeypatch.setenv("DB_TYPE", "mongodb")

    import database.db_operations as dbmod  # import fresco sob o patch

    ops = dbmod.DatabaseOperations()
    try:
        yield ops
    finally:
        _remover_modulos_database()
        sys.modules.update(fake_saved)  # devolve o módulo falso para os outros testes


def _seed_publicadores(db_ops, nomes, sexo="Masculino"):
    """Cria publicadores vazios (histórico []) para os testes usarem."""
    for nome in nomes:
        db_ops.post(nome, batizado=True, sexo=sexo)


@pytest.fixture
def seed(db_ops):
    """Retorna um helper que cria publicadores no banco do teste corrente."""
    def _criar(nomes, sexo="Masculino"):
        _seed_publicadores(db_ops, nomes, sexo=sexo)
    return _criar
