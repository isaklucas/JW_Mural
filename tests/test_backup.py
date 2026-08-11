"""Unitários do backup (offline).

`backup_database` importa `database.db_connection` DENTRO da função, então basta
injetar um módulo falso em `sys.modules` apontando para um Mongo em memória
(mongomock) — nenhum banco real é tocado. `_project_root` vai para um tmp_path.
"""
import json
import sys
import types
from datetime import date, timedelta

import mongomock
import pytest

from util import backup as backup_mod


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    monkeypatch.setattr(backup_mod, "_project_root", lambda: tmp_path)
    return tmp_path


def _instalar_db(monkeypatch, db_type="mongodb", docs=None):
    """Injeta `database.db_connection` falso com um mongomock populado."""
    client = mongomock.MongoClient()
    db = client["jw_mural"]
    for nome, documentos in (docs or {"publicadores": [{"nome": "Ana Lima"}]}).items():
        if documentos:
            db[nome].insert_many(documentos)

    fake = types.ModuleType("database.db_connection")
    fake.db_connection = types.SimpleNamespace(db_type=db_type, db=db)
    monkeypatch.setitem(sys.modules, "database.db_connection", fake)
    return db


def _pasta(raiz, sufixo="", dia=None):
    return raiz / "backups" / f"{dia or date.today()}{sufixo}"


def test_backup_exporta_collections_para_json(raiz, monkeypatch):
    _instalar_db(monkeypatch, docs={"publicadores": [{"nome": "Ana Lima"}, {"nome": "Bruno Rocha"}]})

    assert backup_mod.backup_database() is True

    arquivo = _pasta(raiz) / "publicadores.json"
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert sorted(d["nome"] for d in dados) == ["Ana Lima", "Bruno Rocha"]


def test_backup_do_dia_nao_regrava_sem_forcar(raiz, monkeypatch):
    _instalar_db(monkeypatch)
    backup_mod.backup_database()

    arquivo = _pasta(raiz) / "publicadores.json"
    arquivo.write_text("[]", encoding="utf-8")
    backup_mod.backup_database()  # pasta do dia já existe → no-op

    assert arquivo.read_text(encoding="utf-8") == "[]"


def test_backup_de_saida_usa_pasta_propria_e_regrava(raiz, monkeypatch):
    _instalar_db(monkeypatch)
    backup_mod.backup_database()  # arranque

    assert backup_mod.backup_database(sufixo="-saida", forcar=True) is True
    arquivo_saida = _pasta(raiz, "-saida") / "publicadores.json"
    assert arquivo_saida.exists()
    # a pasta do arranque continua intocada
    assert (_pasta(raiz) / "publicadores.json").exists()

    arquivo_saida.write_text("[]", encoding="utf-8")
    backup_mod.backup_database(sufixo="-saida", forcar=True)
    assert json.loads(arquivo_saida.read_text(encoding="utf-8"))  # regravado


def test_limpar_backups_antigos_remove_so_o_que_venceu(raiz):
    antigo = date.today() - timedelta(days=40)
    recente = date.today() - timedelta(days=5)
    backups = raiz / "backups"
    for nome in (f"{antigo}", f"{antigo}-saida", f"{recente}", f"{date.today()}", "manual"):
        (backups / nome).mkdir(parents=True)

    removidas = backup_mod.limpar_backups_antigos(30)

    assert removidas == 2
    restantes = sorted(p.name for p in backups.iterdir())
    assert restantes == sorted([f"{recente}", f"{date.today()}", "manual"])


def test_backup_purga_antigos(raiz, monkeypatch):
    _instalar_db(monkeypatch)
    antigo = raiz / "backups" / f"{date.today() - timedelta(days=40)}"
    antigo.mkdir(parents=True)

    backup_mod.backup_database()

    assert not antigo.exists()


def test_backup_ignorado_fora_do_mongodb(raiz, monkeypatch):
    _instalar_db(monkeypatch, db_type="dynamodb")

    assert backup_mod.backup_database() is True
    assert not (raiz / "backups").exists()
