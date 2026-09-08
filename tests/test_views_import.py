"""Smoke test: as telas importam offline e enxergam o modal de edição.

Os mixins usam `from views._shared import *`; um símbolo esquecido lá só
apareceria como NameError na mão do usuário, com a janela já aberta.
"""


def test_shared_exporta_modal_de_edicao():
    from views import _shared
    assert callable(_shared.abrir_modal_editar_participacao)


def test_mixins_de_historico_importam():
    from views.publicadores_view import PublicadoresMixin
    from views.historico_view import HistoricoMixin
    assert hasattr(PublicadoresMixin, "historico_publicadores")
    assert hasattr(HistoricoMixin, "historico")


def test_componentes_expoem_o_modal():
    from views.components import abrir_modal_editar_participacao
    assert callable(abrir_modal_editar_participacao)


def test_confirmou_aceita_rotulo_traduzido():
    """REGRESSÃO: `Messagebox.yesno` devolve o rótulo traduzido do botão ("Sim"
    em pt-BR). Comparar com "Yes" cancelava a ação em silêncio."""
    from views.components import confirmou
    assert confirmou("Yes") is True
    assert confirmou("Sim") is True
    assert confirmou(" sim ") is True
    assert confirmou("No") is False
    assert confirmou("Não") is False
    assert confirmou(None) is False
