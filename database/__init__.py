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
salvar_reuniao_final_semana = db_ops.salvar_reuniao_final_semana
listar_reunioes_final_semana = db_ops.listar_reunioes_final_semana
buscar_reuniao_final_semana = db_ops.buscar_reuniao_final_semana

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
    'salvar_reuniao_final_semana',
    'listar_reunioes_final_semana',
    'buscar_reuniao_final_semana',
    'db_ops'
] 