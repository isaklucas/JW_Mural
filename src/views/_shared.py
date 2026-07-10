"""
Imports compartilhados pelas telas extraídas de layout.py (SDD 03).

Os métodos de tela foram movidos VERBATIM do god object `ModernApp` para mixins
(um módulo por tela). Para que os nomes que eles usam continuem resolvendo, este
módulo centraliza os imports de topo que o `layout.py` original fornecia; cada
mixin faz `from views._shared import *`.

Imports pesados e locais (docx, matplotlib, filedialog, calendar, copy, backup,
DesignacoesSalao) permanecem dentro de cada método — viajam junto com o código.
"""
import os
import time
import datetime
import threading
import webbrowser
import logging

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # noqa: F401,F403 (X, BOTH, LEFT, END, ...)
from ttkbootstrap.dialogs import Messagebox

import process.s140 as s140
import process.final_semana as final_semana
from PIL import Image, ImageTk

# Camada de serviço (SDD 03 R3/R4): as telas NÃO importam `database` — falam com
# estes serviços. Reexportados via `from views._shared import *`.
from services import (
    publicador_service,
    reuniao_service,
    designacao_service,
    dashboard_service,
)
import util.janelas as janelas
import util.updater as updater

# Alguns métodos usam `logger` sem qualificador.
logger = logging.getLogger("layout")
