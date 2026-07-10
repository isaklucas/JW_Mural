"""Serviço de designações do salão (áudio, vídeo, microfone, indicadores)."""
from database import db_ops


class DesignacaoService:
    def listar_candidatos(self, *args, **kwargs):
        return db_ops.listar_candidatos_salao_ordenados(*args, **kwargs)

    def salvar(self, *args, **kwargs):
        return db_ops.salvar_designacoes_salao(*args, **kwargs)

    def listar(self, *args, **kwargs):
        return db_ops.listar_designacoes_salao(*args, **kwargs)

    def buscar(self, *args, **kwargs):
        return db_ops.buscar_designacoes_salao(*args, **kwargs)

    def excluir(self, *args, **kwargs):
        return db_ops.excluir_designacoes_salao(*args, **kwargs)


designacao_service = DesignacaoService()
