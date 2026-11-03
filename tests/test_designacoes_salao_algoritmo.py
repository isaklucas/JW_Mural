"""
Testes da geração automática de designações do salão
(process.designacoes_salao.DesignacoesSalao.gerar_designacoes).

Lógica pura: as listas de candidatos e o histórico são injetados via monkeypatch.
"""
from collections import Counter

import pytest

from process import designacoes_salao as mod
from process.designacoes_salao import DesignacoesSalao

AV = [f"AV {i}" for i in range(6)]
MIC = AV[:3] + [f"Mic {i}" for i in range(8)]
IND = [f"Ind {i}" for i in range(15)]


@pytest.fixture
def candidatos(monkeypatch):
    listas = {"audio_video": AV, "microfone": MIC, "indicador": IND}
    monkeypatch.setattr(mod, "listar_candidatos_salao_ordenados", lambda p: list(listas[p]))
    monkeypatch.setattr(mod, "listar_designacoes_salao", lambda: [])
    return listas


def _gerar(**kw):
    datas = DesignacoesSalao.gerar_datas_meses(2, 5, [(2026, 11), (2026, 12)])
    return DesignacoesSalao.gerar_designacoes(datas, seed=kw.pop("seed", 7), **kw)


def _nomes_semana(s):
    nomes = [s["audio"], s["video"]]
    for f in ("microfone", "indicadores"):
        nomes += [n.strip() for n in s[f].split("/") if n.strip()]
    return nomes


def test_ninguem_com_duas_funcoes_no_mesmo_dia(candidatos):
    for s in _gerar():
        nomes = _nomes_semana(s)
        assert len(nomes) == len(set(nomes)), s


def test_ninguem_em_reunioes_seguidas(candidatos):
    r = _gerar()
    for anterior, atual in zip(r, r[1:]):
        repetidos = set(_nomes_semana(anterior)) & set(_nomes_semana(atual))
        assert not repetidos, (atual["data"], repetidos)


def test_audio_video_nao_repetem_sempre_a_mesma_dupla(candidatos):
    r = _gerar()
    duplas = Counter(frozenset([s["audio"], s["video"]]) for s in r)
    assert max(duplas.values()) <= 3, duplas
    assert len(duplas) >= 8, duplas


def test_carga_equilibrada_em_audio_video(candidatos):
    r = _gerar()
    carga = Counter()
    for s in r:
        carga[s["audio"]] += 1
        carga[s["video"]] += 1
    assert set(carga) == set(AV)
    assert max(carga.values()) - min(carga.values()) <= 2, carga


def test_respeita_impedimentos(candidatos):
    datas = DesignacoesSalao.gerar_datas_meses(2, 5, [(2026, 11)])
    bloqueado = {d["data"] for d in datas}
    r = DesignacoesSalao.gerar_designacoes(datas, {"AV 0": bloqueado}, seed=1)
    assert all("AV 0" not in _nomes_semana(s) for s in r)


def test_historico_evita_quem_serviu_na_ultima_reuniao(candidatos, monkeypatch):
    historico = [{"ano": 2026, "mes": 10, "semanas": [{
        "data": "31/10/2026", "audio": "AV 0", "video": "AV 1",
        "microfone": "Mic 0 / Mic 1", "indicadores": "Ind 0 / Ind 1",
    }]}]
    monkeypatch.setattr(mod, "listar_designacoes_salao", lambda: historico)
    primeira = _gerar()[0]
    assert not {"AV 0", "AV 1", "Mic 0", "Mic 1", "Ind 0", "Ind 1"} & set(_nomes_semana(primeira))
