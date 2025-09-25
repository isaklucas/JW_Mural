from .db_operations import DatabaseOperations

# Criar uma instância global das operações
db_ops = DatabaseOperations()

# Exportar os métodos como funções
post = db_ops.post
getAllPub = db_ops.getAllPub
delete = db_ops.delete
update_parte = db_ops.update_parte
limpar_historico_todos = db_ops.limpar_historico_todos
salvar_reuniao = db_ops.salvar_reuniao
buscar_reuniao = db_ops.buscar_reuniao
buscar_historico_publicador = db_ops.buscar_historico_publicador
listar_reunioes = db_ops.listar_reunioes

__all__ = [
    'post',
    'getAllPub',
    'delete',
    'update_parte',
    'limpar_historico_todos',
    'salvar_reuniao',
    'buscar_reuniao',
    'buscar_historico_publicador',
    'listar_reunioes',
    'db_ops'
] 