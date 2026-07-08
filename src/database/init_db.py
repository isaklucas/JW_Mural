from pymongo import MongoClient
import os
import logging
from pathlib import Path

# Carregar .env quando chamado pelo instalador ou diretamente
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

logger = logging.getLogger(__name__)

def init_mongodb():
    """
    Inicializa a estrutura do MongoDB, criando índices necessários
    """
    try:
        # Conectar ao MongoDB (MONGODB_DB_NAME alinhado com db_connection.py)
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        db_name = os.getenv('MONGODB_DB_NAME', os.getenv('MONGODB_DB', 'jw_mural'))
        db = client[db_name]
        
        # Coleção de publicadores
        collection_publicadores = db['publicadores']
        collection_publicadores.create_index([("nome", 1)], unique=True)
        
        # Coleção de reuniões
        collection_reunioes = db['reunioes']
        
        # Índice único para ano e semana
        collection_reunioes.create_index([("ano", 1), ("semana", 1)], unique=True)
        
        # Índices para busca de participantes
        collection_reunioes.create_index([("presidente", 1)])
        collection_reunioes.create_index([("oracao_inicial", 1)])
        collection_reunioes.create_index([("oracao_final", 1)])
        
        # Índices para partes individuais
        collection_reunioes.create_index([("tesouro", 1)])
        collection_reunioes.create_index([("joias_espirituais", 1)])
        collection_reunioes.create_index([("leitura_biblia", 1)])
        collection_reunioes.create_index([("estudo_congregacao", 1)])
        
        # Índices para Escola
        collection_reunioes.create_index([("escola.primeira_parte", 1)])
        collection_reunioes.create_index([("escola.segunda_parte", 1)])
        collection_reunioes.create_index([("escola.terceira_parte", 1)])
        collection_reunioes.create_index([("escola.quarta_parte", 1)])
        
        # Índices para Nossa Vida Cristã
        collection_reunioes.create_index([("nossa_vida_crista.primeira_parte", 1)])
        collection_reunioes.create_index([("nossa_vida_crista.segunda_parte", 1)])
        
        # Índices para ordenação e busca
        collection_reunioes.create_index([("data_reuniao", 1)])
        collection_reunioes.create_index([("ultima_atualizacao", 1)])
        
        # Coleção de reuniões de final de semana
        collection_final_semana = db['reunioes_final_semana']
        collection_final_semana.create_index([("ano", 1), ("mes", 1)], unique=True)
        collection_final_semana.create_index([("data_criacao", 1)])
        
        logger.info("Índices do MongoDB criados com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao inicializar MongoDB: {str(e)}")
        return False

if __name__ == "__main__":
    init_mongodb() 