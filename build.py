import PyInstaller.__main__
import os
import shutil

# Remover diretório dist se existir
if os.path.exists("dist"):
    shutil.rmtree("dist")

# Compilar o executável
PyInstaller.__main__.run([
    'layout.py',
    '--name=JW_Mural',
    '--onefile',
    '--windowed',
    '--icon=assets/icon.ico',
    '--add-data=assets;assets',
    '--add-data=database;database',
    '--add-data=process;process',
    '--add-data=util;util',
    '--add-data=Templates;Templates',
    '--add-data=documentosCriados;documentosCriados',
    '--hidden-import=ttkbootstrap',
    '--hidden-import=pymongo',
    '--hidden-import=docx',
    '--hidden-import=PIL',
    '--hidden-import=requests',
    '--hidden-import=bs4'
]) 