import boto3
from boto3.dynamodb.conditions import Key
import datetime
import util.comandosUteis as util

# Configurar a conexão com o DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') 

# Referenciar a tabela
table = dynamodb.Table('publicadores')  # Substitua pelo nome da sua tabela

def post(nome, batizado):
    now = datetime.datetime.now().isoformat()
    nome = util.ComandosUteis.TitleCase(nome)
    item = {
        "nome": nome.strip(),
        "batizado": batizado,
        "data_inclusao": now,
        "ultima_parte": "",
        "historico": []
    }
    print(f"Adicionando novo publicador {nome} ao DynamoDB")
    table.put_item(Item=item)

def getAllPub():
    response = table.scan()
    return response['Items']

def delete(nome):
    nome = util.ComandosUteis.TitleCase(nome)
    print(f"Removendo publicador {nome} do DynamoDB")
    table.delete_item(Key={"nome": nome.strip()})

def update_parte(nome, parte , semana):
    nome = util.ComandosUteis.TitleCase(nome)
    print(f"Atualizando publicador {nome} no DynamoDB")
    now = datetime.datetime.now().isoformat()
    table.update_item(
        Key={"nome": nome.strip()},
        UpdateExpression="set ultima_parte = :p, historico = list_append(if_not_exists(historico, :empty_list), :h)",
        ExpressionAttributeValues={
            ":p": semana,
            ":h": [{"parte": parte, "data": semana}],
            ":empty_list": []
        }
    )