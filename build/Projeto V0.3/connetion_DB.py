import pymongo
import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["JW_Mural"]

publicadoresDB = db["Publicadores"]



def post(nome, batizado):
    
    now = datetime.datetime.now()
     
    json = { "Nome": nome, "Batizado": batizado, "Data_inclusao": now, "Ultima_Parte": "" }
     
    publicadoresDB.insert_one(json)
    

def getAllPub():
    
    return  publicadoresDB.find()