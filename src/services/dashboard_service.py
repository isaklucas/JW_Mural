"""Serviço de estatísticas dos dashboards.

Usa o singleton `db_ops` em vez de instanciar `DatabaseOperations()` a cada
chamada (evita recriar índices repetidamente).
"""
from database import db_ops


class DashboardService:
    def contar_participacoes_por_parte(self, parte=None):
        return db_ops.contar_participacoes_por_parte(parte=parte)

    def contar_participacoes_unicas_por_reuniao(self):
        return db_ops.contar_participacoes_unicas_por_reuniao()

    def contar_designacoes_por_publicador(self):
        return db_ops.contar_designacoes_salao_por_publicador()


dashboard_service = DashboardService()
