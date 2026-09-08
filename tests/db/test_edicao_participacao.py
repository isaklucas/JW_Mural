"""Integração: editar UMA participação já gravada (remover / passar para outro).

É o `transferir_historico` reduzido a uma entrada só, usado pelas telas de
Histórico de Publicadores e Histórico de Reuniões (meio de semana). A regra que
os testes protegem: histórico e documento da reunião andam JUNTOS — senão
resalvar a semana ressuscita o nome antigo.
"""
import pytest


def _reuniao(presidente="Alfa", leitura="Bravo", escola1="Charlie / Delta",
             semana="1-7 DE MARÇO", ano=2026):
    return {
        "ano": ano, "semana": semana, "data_reuniao": "2026-03-02T00:00:00",
        "presidente": presidente, "oracao_inicial": "não possui",
        "tesouro": "não possui", "joias_espirituais": "não possui",
        "leitura_biblia": leitura,
        "escola": {"primeira_parte": escola1, "segunda_parte": "não possui",
                   "terceira_parte": "não possui", "quarta_parte": "não possui"},
        "nossa_vida_crista": {"primeira_parte": "não possui", "segunda_parte": "não possui"},
        "estudo_congregacao": "não possui", "oracao_final": "não possui",
    }


DATA = "Semana 1-7 DE MARÇO de 2026"


def _hist(db_ops, nome):
    return [(h.get("parte"), h.get("data")) for h in db_ops.buscar_historico_publicador(nome)]


@pytest.fixture
def reuniao_salva(db_ops, seed):
    seed(["Alfa", "Bravo", "Charlie", "Delta", "Echo"])
    assert db_ops.salvar_reuniao(_reuniao())["success"] is True
    return db_ops


def test_remover_participacao_limpa_historico_e_reuniao(reuniao_salva):
    res = reuniao_salva.remover_participacao("Alfa", "Presidente", DATA)
    assert res["success"] is True
    assert res["reuniao_atualizada"] is True
    assert _hist(reuniao_salva, "Alfa") == []
    assert reuniao_salva.buscar_reuniao(2026, "1-7 DE MARÇO")["presidente"] == "não possui"


def test_remover_so_um_de_dois_participantes_da_parte(reuniao_salva):
    res = reuniao_salva.remover_participacao("Charlie", "Escola - Primeira Parte", DATA)
    assert res["success"] is True
    reuniao = reuniao_salva.buscar_reuniao(2026, "1-7 DE MARÇO")
    assert reuniao["escola"]["primeira_parte"] == "Delta"   # Delta continua
    assert _hist(reuniao_salva, "Charlie") == []
    assert _hist(reuniao_salva, "Delta") == [("Escola - Primeira Parte", DATA)]


def test_reatribuir_move_a_entrada_e_troca_o_nome_na_reuniao(reuniao_salva):
    res = reuniao_salva.reatribuir_participacao("Bravo", "Echo", "Leitura da Bíblia", DATA)
    assert res["success"] is True
    assert res["reuniao_atualizada"] is True
    assert _hist(reuniao_salva, "Bravo") == []
    assert _hist(reuniao_salva, "Echo") == [("Leitura da Bíblia", DATA)]
    assert reuniao_salva.buscar_reuniao(2026, "1-7 DE MARÇO")["leitura_biblia"] == "Echo"


def test_reatribuicao_sobrevive_a_resalvar_a_reuniao(reuniao_salva):
    """REGRESSÃO: sem atualizar a reunião, regravar a semana desfaria a troca."""
    reuniao_salva.reatribuir_participacao("Bravo", "Echo", "Leitura da Bíblia", DATA)
    reuniao = reuniao_salva.buscar_reuniao(2026, "1-7 DE MARÇO")
    reuniao_salva.salvar_reuniao(_reuniao(leitura=reuniao["leitura_biblia"]))
    assert _hist(reuniao_salva, "Echo") == [("Leitura da Bíblia", DATA)]
    assert _hist(reuniao_salva, "Bravo") == []


def test_resalvar_reuniao_com_outro_participante_nao_deixa_historico_orfao(reuniao_salva):
    """REGRESSÃO: trocar o presidente e resalvar tirava o nome da reunião mas
    deixava a participação pendurada no histórico do antigo."""
    assert reuniao_salva.salvar_reuniao(_reuniao(presidente="Echo"))["success"] is True
    assert _hist(reuniao_salva, "Alfa") == []
    assert _hist(reuniao_salva, "Echo") == [("Presidente", DATA)]


def test_resalvar_reuniao_nao_duplica_quem_continua(reuniao_salva):
    reuniao_salva.salvar_reuniao(_reuniao())
    assert _hist(reuniao_salva, "Alfa") == [("Presidente", DATA)]


def test_resalvar_reuniao_preserva_salao_e_final_de_semana(reuniao_salva):
    """A purga da semana só pode apagar participação de meio de semana."""
    reuniao_salva.update_parte("Alfa", "Leitura Sentinela", "Semana 1-7 DE MARÇO")
    reuniao_salva.salvar_designacoes_salao({
        "ano": 2026, "mes": 3, "dia_semana": "Terça", "dia_fds": "Domingo",
        "semanas": [{"data": DATA, "tipo": "meio", "audio": "Alfa",
                     "video": "", "microfone": "", "indicadores": ""}],
    })
    reuniao_salva.salvar_reuniao(_reuniao())
    partes = {p for p, _ in _hist(reuniao_salva, "Alfa")}
    assert partes == {"Presidente", "Leitura Sentinela", "Salão - Áudio"}


def test_remover_participacao_inexistente_falha_sem_alterar_nada(reuniao_salva):
    res = reuniao_salva.remover_participacao("Echo", "Presidente", DATA)
    assert res["success"] is False
    assert reuniao_salva.buscar_reuniao(2026, "1-7 DE MARÇO")["presidente"] == "Alfa"


def test_reatribuir_para_nome_novo_cria_o_publicador(reuniao_salva):
    res = reuniao_salva.reatribuir_participacao("Alfa", "Foxtrot", "Presidente", DATA)
    assert res["success"] is True
    assert _hist(reuniao_salva, "Foxtrot") == [("Presidente", DATA)]
    assert reuniao_salva.buscar_reuniao(2026, "1-7 DE MARÇO")["presidente"] == "Foxtrot"
