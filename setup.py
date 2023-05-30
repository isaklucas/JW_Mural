import sys
from cx_Freeze import setup, Executable

# Dependências do seu código
build_exe_options = {"packages": ["os" , "requests" , "bs4" , "docx", "tkinter", "pymongo", "datetime", "webbrowser"], "excludes": [],
     "include_files": ["layout.py", "JW_Mural.py", "connetion_DB.py"] 
     }

# Configurações do setup
setup(
    name = "JW_Mural",
    version = "0.1",
    description = "Descrição do seu código",
    options = {"build_exe": build_exe_options},
    executables = [Executable("layout.py", base=None, shortcut_name= "qd_anuncio")]
)
