"""Versão da aplicação — fonte única de verdade lida de VERSION.txt.

O mesmo VERSION.txt é lido pelo Inno Setup (JW_Mural.iss) via ISPP, então
bumpar a versão do app = editar apenas VERSION.txt na raiz do projeto.
"""
import os
import sys


def _localizar_version_txt():
    """Retorna o caminho de VERSION.txt tanto em dev quanto no app compilado.

    - Frozen (PyInstaller OneDir): VERSION.txt fica ao lado do JW_Mural.exe.
    - Dev: na raiz do projeto (um nível acima de src/).
    """
    if getattr(sys, "frozen", False):
        candidatos = [
            os.path.join(os.path.dirname(sys.executable), "VERSION.txt"),
            os.path.join(getattr(sys, "_MEIPASS", ""), "VERSION.txt"),
        ]
    else:
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidatos = [os.path.join(raiz, "VERSION.txt")]
    for c in candidatos:
        if os.path.isfile(c):
            return c
    return None


def _ler_versao():
    caminho = _localizar_version_txt()
    if caminho:
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                v = f.read().strip()
                if v:
                    return v
        except Exception:
            pass
    return "0.0"


__version__ = _ler_versao()
