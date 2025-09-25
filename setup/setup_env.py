import os
import shutil
from pathlib import Path

def setup_environment():
    """Configura o ambiente para o executável"""
    print("Configurando ambiente para JW Mural...")
    
    # Diretórios necessários
    diretórios = ['documentosCriados', 'Templates', 'util', 'process', 'database', 'assets']
    
    # Criar diretórios se não existirem
    for dir in diretórios:
        if not os.path.exists(dir):
            os.makedirs(dir)
            print(f"Diretório criado: {dir}")
        else:
            print(f"Diretório já existe: {dir}")
    
    # Verificar se arquivo .env existe
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Arquivo de configuração\n")
            f.write("MONGODB_URI=mongodb://localhost:27017\n")
            f.write("DB_NAME=jw_mural\n")
            f.write("APP_NAME=JW Mural\n")
            f.write("APP_VERSION=1.0\n")
        print("Arquivo .env criado")
    else:
        print("Arquivo .env já existe")
    
    # Verificar se Template.docx existe
    if not os.path.exists("Template.docx"):
        print("AVISO: Template.docx não encontrado. Importância: Necessário para a geração de documentos.")
    else:
        print("Template.docx encontrado")
    
    print("Configuração de ambiente concluída!")

if __name__ == "__main__":
    setup_environment() 