import os
from dotenv import load_dotenv
from pymongo import MongoClient
import boto3
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'mongodb')
        if self.db_type == 'mongodb':
            self._init_mongodb()
        else:
            self._init_dynamodb()

    def _init_mongodb(self):
        try:
            # Conectar ao MongoDB
            self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
            self.db = self.client[os.getenv('MONGODB_DB_NAME', 'jw_mural')]
            self.collection = self.db[os.getenv('MONGODB_COLLECTION', 'publicadores')]
            
            # Garantir que a collection reunioes existe
            if 'reunioes' not in self.db.list_collection_names():
                self.db.create_collection('reunioes')
                logger.info("Collection 'reunioes' criada com sucesso")
            
            logger.info("Conexão com MongoDB estabelecida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {str(e)}")
            raise

    def _init_dynamodb(self):
        try:
            # Conectar ao DynamoDB
            self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            self.table = self.dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'publicadores'))
            logger.info("Conexão com DynamoDB estabelecida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao DynamoDB: {str(e)}")
            raise

    def get_connection(self):
        """Retorna a conexão apropriada baseada no tipo de banco de dados"""
        if self.db_type == 'mongodb':
            return self.collection
        return self.table

# Criar uma instância global da conexão
db_connection = DatabaseConnection() 