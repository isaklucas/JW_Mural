import os
import sys
import logging
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
import boto3
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente — path explícito para frozen app
if getattr(sys, 'frozen', False):
    _env_path = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(_env_path)

class DatabaseUtils:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'mongodb')

    def verify_mongodb_connection(self) -> bool:
        """Verifica se é possível conectar ao MongoDB"""
        try:
            client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'), serverSelectionTimeoutMS=5000)
            client.server_info()
            logger.info("Conexão com MongoDB estabelecida com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {str(e)}")
            return False

    def verify_dynamodb_connection(self) -> bool:
        """Verifica se é possível conectar ao DynamoDB"""
        try:
            dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            table = dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'publicadores'))
            table.table_status
            logger.info("Conexão com DynamoDB estabelecida com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao DynamoDB: {str(e)}")
            return False

    def setup_mongodb_structure(self) -> bool:
        """Configura a estrutura necessária no MongoDB"""
        try:
            client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
            db_name = os.getenv('MONGODB_DB_NAME', 'jw_mural')
            db = client[db_name]

            # Definição da estrutura do banco
            collections_structure = {
                'publicadores': {
                    'indexes': [
                        {
                            'fields': [('nome', ASCENDING)],
                            'unique': True,
                            'name': 'nome_unique'
                        }
                    ],
                    'validator': {
                        '$jsonSchema': {
                            'bsonType': 'object',
                            'required': ['nome', 'batizado', 'data_inclusao'],
                            'properties': {
                                'nome': {
                                    'bsonType': 'string',
                                    'description': 'Nome do publicador - obrigatório e único'
                                },
                                'batizado': {
                                    'bsonType': 'bool',
                                    'description': 'Status de batismo - obrigatório'
                                },
                                'data_inclusao': {
                                    'bsonType': 'string',
                                    'description': 'Data de inclusão - obrigatório'
                                },
                                'ultima_parte': {
                                    'bsonType': 'string',
                                    'description': 'Última parte realizada'
                                },
                                'historico': {
                                    'bsonType': 'array',
                                    'description': 'Histórico de partes',
                                    'items': {
                                        'bsonType': 'object',
                                        'required': ['parte', 'data'],
                                        'properties': {
                                            'parte': {
                                                'bsonType': 'string',
                                                'description': 'Nome da parte'
                                            },
                                            'data': {
                                                'bsonType': 'string',
                                                'description': 'Data da parte'
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            # Criar/atualizar collections e índices
            for collection_name, structure in collections_structure.items():
                # Criar collection se não existir
                if collection_name not in db.list_collection_names():
                    logger.info(f"Criando collection: {collection_name}")
                    db.create_collection(
                        collection_name,
                        validator=structure.get('validator')
                    )
                else:
                    # Atualizar validator se a collection já existe (não-fatal)
                    try:
                        db.command({
                            'collMod': collection_name,
                            'validator': structure.get('validator')
                        })
                    except Exception as e:
                        logger.warning(f"collMod ignorado para '{collection_name}': {e}")

                collection = db[collection_name]

                # Criar/atualizar índices
                for index in structure['indexes']:
                    collection.create_index(
                        index['fields'],
                        unique=index.get('unique', False),
                        name=index.get('name')
                    )

            logger.info("Estrutura do MongoDB configurada com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao configurar estrutura do MongoDB: {str(e)}")
            return False

    def verify_and_setup_database(self) -> bool:
        """Verifica e configura o banco de dados conforme necessário"""
        try:
            if self.db_type == 'mongodb':
                if not self.verify_mongodb_connection():
                    return False
                return self.setup_mongodb_structure()
            else:
                return self.verify_dynamodb_connection()
        except Exception as e:
            logger.error(f"Erro ao verificar e configurar banco de dados: {str(e)}")
            return False

    def get_database_status(self) -> Dict[str, bool]:
        """Retorna o status atual do banco de dados"""
        status = {
            'type': self.db_type,
            'connected': False,
            'structured': False
        }

        try:
            if self.db_type == 'mongodb':
                status['connected'] = self.verify_mongodb_connection()
                if status['connected']:
                    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
                    db = client[os.getenv('MONGODB_DB_NAME', 'jw_mural')]
                    status['structured'] = 'publicadores' in db.list_collection_names()
            else:
                status['connected'] = self.verify_dynamodb_connection()
                status['structured'] = status['connected']  # Para DynamoDB, se está conectado, está estruturado

            logger.info(f"Status do banco de dados: {status}")
            return status

        except Exception as e:
            logger.error(f"Erro ao verificar status do banco de dados: {str(e)}")
            return status

# Criar uma instância global dos utilitários do banco de dados
db_utils = DatabaseUtils() 