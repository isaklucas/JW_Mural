"""
Testes da designação automática (s140.selecionar_publicadores_automaticamente).

Exercita a LÓGICA PURA de distribuição: rotação em ciclo, não-repetição na
mesma semana e ramos condicionais das partes. A regra de papel/permissão vive
dentro do db_ops real (query no banco) e é integração — não é coberta aqui.
"""
import pytest

from process.s140 import s140

# 25 nomes masculinos distintos: pool > ~16 slots/semana, evita "não possui"
POOL = [f"Irmao {i:02d}" for i in range(25)]
AJUDANTES = [f"Ajudante {i:02d}" for i in range(6)]


def _semanas(qtd, estudo="Explique suas crenças", escola4="Faça discípulos",
             nvc2="Estudo bíblico"):
    return [
        {
            "semana": f"Semana {i + 1}",
            "estudoDiscurso": estudo,
            "escola4": escola4,
            "nvcP2": nvc2,
        }
        for i in range(qtd)
    ]


def _nomes_planos(participantes, excluir=("OracaoFinal",)):
    """Achata os valores de Participantes em nomes individuais (separa 'A / B')."""
    nomes = []
    for chave, valor in participantes.items():
        if chave in excluir or valor == "não possui":
            continue
        nomes += [n.strip() for n in valor.split("/") if n.strip()]
    return nomes


@pytest.fixture
def configurar(monkeypatch, fake_db):
    """Configura o FakeDbOps e garante que s140 use ele."""
    def _cfg(pool=POOL, ajudantes=AJUDANTES, sexos=None):
        fake_db.pool = list(pool)
        fake_db.ajudantes = list(ajudantes)
        fake_db.sexos = sexos or {}
        fake_db.reunioes_salvas = []
        monkeypatch.setattr("process.s140.db_ops", fake_db)
        return fake_db
    return _cfg


def test_nao_repete_publicador_na_mesma_semana(configurar):
    configurar()
    semanas = _semanas(1)
    s140.selecionar_publicadores_automaticamente(semanas, salvar_imediatamente=False)

    nomes = _nomes_planos(semanas[0]["Participantes"])
    assert nomes, "deveria designar alguém"
    assert len(nomes) == len(set(nomes)), f"repetição na semana: {nomes}"


def test_oracao_final_igual_presidente(configurar):
    configurar()
    semanas = _semanas(1)
    s140.selecionar_publicadores_automaticamente(semanas, salvar_imediatamente=False)

    p = semanas[0]["Participantes"]
    assert p["OracaoFinal"] == p["Presidente"]


def test_rotaciona_presidente_entre_semanas(configurar):
    configurar()
    semanas = _semanas(3)
    s140.selecionar_publicadores_automaticamente(semanas, salvar_imediatamente=False)

    presidentes = [s["Participantes"]["Presidente"] for s in semanas]
    assert len(set(presidentes)) == 3, f"presidente não rotacionou: {presidentes}"


def test_pool_vazio_retorna_nao_possui(configurar):
    configurar(pool=[], ajudantes=[])
    semanas = _semanas(1)
    s140.selecionar_publicadores_automaticamente(semanas, salvar_imediatamente=False)

    valores = set(semanas[0]["Participantes"].values())
    assert valores == {"não possui"}


def test_partes_ausentes_marcam_nao_possui(configurar):
    configurar()
    semanas = _semanas(1, estudo="não possui", escola4="não possui",
                       nvc2="não possue esta Parte")
    s140.selecionar_publicadores_automaticamente(semanas, salvar_imediatamente=False)

    p = semanas[0]["Participantes"]
    assert p["EstudoDiscurso"] == "não possui"
    assert p["Escola4"] == "não possui"
    assert p["Nvc2"] == "não possui"


def test_salvar_imediatamente_false_nao_toca_db(configurar):
    fake = configurar()
    semanas = _semanas(2)
    s140.selecionar_publicadores_automaticamente(semanas, salvar_imediatamente=False)

    assert fake.reunioes_salvas == []


def test_salvar_imediatamente_true_persiste(configurar):
    fake = configurar()
    semanas = _semanas(2)
    s140.selecionar_publicadores_automaticamente(semanas, salvar_imediatamente=True)

    assert len(fake.reunioes_salvas) == 2
    assert fake.reunioes_salvas[0]["presidente"] == semanas[0]["Participantes"]["Presidente"]
