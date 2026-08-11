"""Unitários: normalização de nome de publicador (sem banco, sem UI)."""
from util.comandosUteis import ComandosUteis


def test_titlecase_colapsa_espacos():
    assert ComandosUteis.TitleCase("  josé   da   SILVA ") == "José Da Silva"


def test_titlecase_none_vira_string_vazia():
    assert ComandosUteis.TitleCase(None) == ""


def test_normalizar_nome_mantem_acento():
    assert ComandosUteis.normalizar_nome("joão pereira") == "João Pereira"


def test_chave_nome_iguala_variacoes():
    variacoes = ["José  da Silva", "jose da silva ", "JOSE DA SILVA", " José da  Silva"]
    chaves = {ComandosUteis.chave_nome(v) for v in variacoes}
    assert chaves == {"jose da silva"}


def test_chave_nome_diferencia_publicadores_distintos():
    assert ComandosUteis.chave_nome("Ana Lima") != ComandosUteis.chave_nome("Ana Lima Souza")
