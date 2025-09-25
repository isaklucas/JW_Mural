import sys
import os
from cx_Freeze import setup, Executable

# Dependências do seu código
build_exe_options = {
    "packages": [
        "os",
        "requests",
        "bs4",
        "docx",
        "tkinter",
        "pymongo",
        "datetime",
        "webbrowser",
        "boto3",
        "ttkbootstrap",
        "PIL",
        "python-dotenv"
    ],
    "includes": [
        "tkinter",
        "tkinter.ttk",
        "ttkbootstrap",
        "PIL",
        "boto3",
        "pymongo",
        "python-dotenv"
    ],
    "include_files": [
        ("layout.py", "layout.py"),
        ("Template.docx", "Template.docx"),
        ("assets", "assets"),
        ("Templates", "Templates"),
        ("util", "util"),
        ("process", "process"),
        ("database", "database"),
        (".env", ".env")
    ],
    "excludes": [
        "test",
        "unittest",
        "pydoc",
        "doctest",
        "distutils"
    ],
    "zip_include_packages": "*",
    "zip_exclude_packages": "",
    "build_exe": os.path.join("build", "JW_Mural")
}

# Configurações do executável
target = Executable(
    script="layout.py",
    base="Win32GUI" if sys.platform == "win32" else None,
    target_name="JW_Mural.exe",
    icon=None,
    shortcut_name="JW_Mural",
    shortcut_dir="DesktopFolder"
)

# Configurações do setup
setup(
    name="JW_Mural",
    version="1.0",
    description="Sistema de Gerenciamento de Anúncios JW",
    options={"build_exe": build_exe_options},
    executables=[target]
)
