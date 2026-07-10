"""Serviço de publicadores — encapsula as operações de `db_ops` de publicador."""
from database import db_ops


class PublicadorService:
    def listar(self):
        return db_ops.getAllPub()

    def adicionar(self, *args, **kwargs):
        return db_ops.post(*args, **kwargs)

    def excluir(self, *args, **kwargs):
        return db_ops.delete(*args, **kwargs)

    def atualizar(self, *args, **kwargs):
        return db_ops.update_publicador(*args, **kwargs)

    def buscar_historico(self, *args, **kwargs):
        return db_ops.buscar_historico_publicador(*args, **kwargs)

    def resetar_todo_historico(self, *args, **kwargs):
        return db_ops.resetar_todo_historico(*args, **kwargs)

    def restaurar_historico(self, nome, historico, ultima_parte):
        """Sobrescreve histórico/última parte de um publicador (usado ao renomear).

        Encapsula o acesso direto à collection que antes vivia na view.
        """
        col = db_ops.db if hasattr(db_ops.db, "find") else db_ops.db.database["publicadores"]
        col.update_one(
            {"nome": nome},
            {"$set": {"historico": historico, "ultima_parte": ultima_parte}},
        )


publicador_service = PublicadorService()
