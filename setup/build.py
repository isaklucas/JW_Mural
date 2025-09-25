import PyInstaller.__main__
import os
import shutil

# Remover diretório dist se existir
if os.path.exists("dist"):
    shutil.rmtree("dist")

# Garantir que os diretórios necessários existam
diretorios = ['documentosCriados', 'Templates', 'util', 'process', 'database', 'assets']
for dir in diretorios:
    if not os.path.exists(dir):
        os.makedirs(dir)
        print(f"Diretório criado: {dir}")

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
    print("Arquivo .env criado")

# Garantir que o arquivo .env e Template.docx existam
if not os.path.exists("Template.docx"):
    print("AVISO: Template.docx não encontrado. Crie este arquivo antes de continuar.")

# Compilar o executável
PyInstaller.__main__.run([
    'layout.py',
    '--name=JW_Mural',
    '--onedir',  # Criar um diretório em vez de um único arquivo
    '--add-data=assets;assets',
    '--add-data=database;database',
    '--add-data=process;process',
    '--add-data=util;util',
    '--add-data=Templates;Templates',
    '--add-data=documentosCriados;documentosCriados',
    '--add-data=.env;.',
    '--add-data=Template.docx;.',
    '--hidden-import=ttkbootstrap',
    '--hidden-import=pymongo',
    '--hidden-import=docx',
    '--hidden-import=PIL',
    '--hidden-import=requests',
    '--hidden-import=bs4',
    '--hidden-import=os',
    '--hidden-import=sys',
    '--hidden-import=json',
    '--hidden-import=datetime',
    '--hidden-import=re',
    '--hidden-import=dotenv'
])

# Copiar arquivo de inicialização
shutil.copy("setup/startup.bat", "dist/JW_Mural/startup.bat")
print("\nExecutável criado com sucesso na pasta dist/JW_Mural!")
print("Use o arquivo startup.bat para iniciar o programa.") 