import os
import shutil
import sys
from pathlib import Path

def corrigir_erros():
    """Corrige os erros de execução do JW Mural"""
    print("Corrigindo erros do JW Mural...")
    
    # Diretórios necessários
    diretorios = ['documentosCriados', 'Templates', 'util', 'process', 'database', 'assets']
    
    # Criar diretórios se não existirem
    for dir in diretorios:
        if not os.path.exists(dir):
            os.makedirs(dir)
            print(f"Diretório criado: {dir}")
        else:
            print(f"Diretório já existe: {dir}")
    
    # Verificar se arquivo .env existe
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Arquivo de configuração do JW Mural\n")
            f.write("MONGODB_URI=mongodb://localhost:27017\n")
            f.write("DB_NAME=jw_mural\n")
            f.write("COLLECTION_NAME=reunioes\n")
            f.write("DB_TYPE=mongodb\n")
            f.write("MONGODB_DB_NAME=jw_mural\n")
            f.write("MONGODB_COLLECTION=reunioes\n")
        print("Arquivo .env criado com configurações básicas")
    else:
        print("Arquivo .env já existe")
    
    # Verificar se Template.docx existe
    if not os.path.exists("Template.docx"):
        print("AVISO: Template.docx não encontrado. Este arquivo é necessário para a geração de documentos.")
        print("Por favor, inclua um arquivo Template.docx na pasta raiz do programa.")
    else:
        print("Template.docx encontrado")
    
    # Modificando o arquivo setup/build.py para incluir --onedir
    build_path = os.path.join("setup", "build.py")
    if os.path.exists(build_path):
        with open(build_path, "r") as f:
            content = f.read()
        
        # Substituindo '--onefile' por '--onedir' para resolver problemas de extração temporária
        if "--onefile" in content:
            content = content.replace("'--onefile',", "'--onedir',")
            
            with open(build_path, "w") as f:
                f.write(content)
            print("Arquivo build.py modificado para usar --onedir em vez de --onefile")
    
    print("Correções concluídas! Execute 'python setup/build.py' para gerar o executável.")

if __name__ == "__main__":
    corrigir_erros() 