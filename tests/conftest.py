"""
Configuração de testes.

Ponto crítico: `src/database/__init__.py` cria `DatabaseOperations()` no import,
que por sua vez chama `db_connection.get_connection()` e `list_collection_names()`
— ou seja, importar `database` (e portanto `process.webscrapper` / `process.s140`)
exige um MongoDB vivo. Para rodar os testes offline, injetamos um módulo
`database` FALSO em `sys.modules` ANTES de qualquer teste importar os módulos de
produção. Assim nenhum teste toca o banco real.
"""
import sys
import types


class FakeDbOps:
    """Dublê de `database.db_ops`. Configurável por teste.

    O algoritmo de designação apenas consome as listas que estes métodos
    retornam (a regra de papel/permissão fica dentro do db_ops real, então é
    testada em integração, não aqui).
    """

    def __init__(self, pool=None, ajudantes=None, sexos=None):
        # pool: lista de candidatos devolvida para QUALQUER parte do meio de semana
        self.pool = pool if pool is not None else []
        self.ajudantes = ajudantes if ajudantes is not None else []
        # sexos: mapa nome -> "Masculino"/"Feminino"; ausente => "Masculino"
        self.sexos = sexos or {}
        self.reunioes_salvas = []  # registra chamadas de salvar_reuniao

    # --- métodos usados por selecionar_publicadores_automaticamente ---
    def listar_candidatos_ordenados_por_menos_partecipacoes_meio(self, parte):
        return list(self.pool)

    def listar_ajudantes_estudo_ordenados_por_menos_partecipacoes(self):
        return list(self.ajudantes)

    def obter_sexo_publicador(self, nome):
        return self.sexos.get(nome, "Masculino")

    def salvar_reuniao(self, dados):
        self.reunioes_salvas.append(dados)
        return {"success": True, "message": "ok"}


def _instalar_database_falso():
    """Insere um módulo `database` sintético em sys.modules (idempotente)."""
    if isinstance(sys.modules.get("database"), types.ModuleType) and getattr(
        sys.modules["database"], "_fake", False
    ):
        return sys.modules["database"]

    mod = types.ModuleType("database")
    mod._fake = True
    mod.db_ops = FakeDbOps()
    # webscrapper faz: from database import post, getAllPub, delete
    mod.post = lambda *a, **k: None
    mod.getAllPub = lambda *a, **k: []
    mod.delete = lambda *a, **k: None

    # Qualquer outro símbolo importado por módulos de produção (ex.: update_parte
    # em util.janelas) vira um no-op — os testes não exercitam essas funções.
    def _module_getattr(name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: None

    mod.__getattr__ = _module_getattr
    sys.modules["database"] = mod
    return mod


# Executa no import do conftest — antes de qualquer coleta/import de teste.
_instalar_database_falso()


import pytest  # noqa: E402


@pytest.fixture
def fake_db():
    """Retorna o FakeDbOps ativo (mesmo objeto que `process.s140.db_ops`)."""
    return sys.modules["database"].db_ops
