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
        """Trabalho de salão (áudio, vídeo, microfone, indicador)."""
        return db_ops.contar_designacoes_salao_por_publicador()

    def contar_participacoes_final_semana(self):
        """Programa da reunião de fim de semana (Leitura Sentinela, Presidente)."""
        return db_ops.contar_participacoes_final_semana_por_publicador()


dashboard_service = DashboardService()
