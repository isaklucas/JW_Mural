"""Serviço de reuniões (meio de semana + final de semana)."""
from database import db_ops


class ReuniaoService:
    # --- meio de semana ---
    def listar(self, *args, **kwargs):
        return db_ops.listar_reunioes(*args, **kwargs)

    def buscar(self, *args, **kwargs):
        return db_ops.buscar_reuniao(*args, **kwargs)

    def salvar(self, *args, **kwargs):
        return db_ops.salvar_reuniao(*args, **kwargs)

    # --- final de semana ---
    def salvar_final_semana(self, *args, **kwargs):
        return db_ops.salvar_reuniao_final_semana(*args, **kwargs)

    def listar_final_semana(self, *args, **kwargs):
        return db_ops.listar_reunioes_final_semana(*args, **kwargs)

    def buscar_final_semana(self, *args, **kwargs):
        return db_ops.buscar_reuniao_final_semana(*args, **kwargs)

    def excluir_final_semana(self, *args, **kwargs):
        return db_ops.excluir_reuniao_final_semana(*args, **kwargs)


reuniao_service = ReuniaoService()
