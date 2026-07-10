"""
Camada de serviço (SDD 03 — R3/R4).

Único ponto do código de UI que fala com `database`/`db_ops`. As telas (views)
chamam estes serviços em vez de acessar o banco direto, isolando a persistência.
"""
from services.publicador_service import publicador_service, PublicadorService
from services.reuniao_service import reuniao_service, ReuniaoService
from services.designacao_service import designacao_service, DesignacaoService
from services.dashboard_service import dashboard_service, DashboardService

__all__ = [
    "publicador_service", "PublicadorService",
    "reuniao_service", "ReuniaoService",
    "designacao_service", "DesignacaoService",
    "dashboard_service", "DashboardService",
]
