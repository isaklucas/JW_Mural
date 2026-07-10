import sys
import os
import logging
from pathlib import Path

# Logging ANTES de qualquer import para capturar erros de inicialização
def _setup_logging():
    if getattr(sys, 'frozen', False):
        _log_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'JW Mural')
    else:
        _log_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(_log_dir, exist_ok=True)
    _log_file = os.path.join(_log_dir, 'jw_mural.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(_log_file, encoding='utf-8'),
            logging.StreamHandler(),
        ]
    )
    return _log_file

_log_file = _setup_logging()
logging.getLogger(__name__).info(f"Iniciando JW Mural — log em {_log_file}")

sys.path.insert(0, str(Path(__file__).resolve().parent))
if '--init-db' in sys.argv:
    from database.init_db import init_mongodb
    _ok = init_mongodb()
    sys.exit(0 if _ok else 1)

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.dialogs import Messagebox
    import tkinter as tk
    import webbrowser
    import time
    import process.s140 as s140
    import process.final_semana as final_semana
    from PIL import Image, ImageTk
    from database import post, getAllPub, delete, listar_reunioes_final_semana, buscar_reuniao_final_semana, excluir_reuniao_final_semana, db_ops
    from database.db_operations import DatabaseOperations
    import util.janelas as janelas
    import util.updater as updater
    from views.components import criar_card
    from views.publicadores_view import PublicadoresMixin
    from views.historico_view import HistoricoMixin
    from views.reunioes_view import ReunioesMixin
    from views.designacoes_view import DesignacoesMixin
    from views.dashboards_view import DashboardsMixin
    from views.config_view import ConfigMixin
    from util.startup_manager import initialize_application
    import datetime
    import threading

    # Workaround: LabelFrame com padding= falha no Tcl/Tk do app frozen
    # Strip padding silenciosamente para evitar _tkinter.TclError: unknown option "-padding"
    if getattr(sys, 'frozen', False):
        _OrigLF = ttk.LabelFrame
        class _SafeLabelFrame(_OrigLF):
            def __init__(self, master=None, **kw):
                kw.pop('padding', None)
                super().__init__(master, **kw)
        ttk.LabelFrame = _SafeLabelFrame

except Exception as _import_err:
    logging.getLogger(__name__).critical(f"Falha ao importar módulos: {_import_err}", exc_info=True)
    import tkinter as _tk
    from tkinter import messagebox as _mb
    _r = _tk.Tk()
    _r.withdraw()
    _mb.showerror(
        "Erro Fatal",
        f"Não foi possível iniciar o aplicativo.\n\n{_import_err}\n\nVerifique se o MongoDB está em execução e o arquivo .env está correto.\n\nLog: %APPDATA%\\JW Mural\\jw_mural.log"
    )
    sys.exit(1)

logger = logging.getLogger(__name__)

class ModernApp(PublicadoresMixin, HistoricoMixin, ReunioesMixin, DesignacoesMixin, DashboardsMixin, ConfigMixin):
    def __init__(self, root):
        self.root = root
        # Configuração da janela principal com tema moderno
        self.root.iconbitmap("assets/icon.ico") if os.path.exists("assets/icon.ico") else None
        
        # Configuração do container principal
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # Título principal
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="JW Mural",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Sistema de Gerenciamento de Reuniões",
            font=("Helvetica", 12),
            bootstyle="secondary"
        )
        subtitle_label.pack()
        
        # Container para os cards
        self.cards_frame = ttk.Frame(self.main_frame, bootstyle="light")
        self.cards_frame.pack(fill=BOTH, expand=YES)
        
        # Criação dos cards
        # Linha 0: Criar reuniões
        self.create_card(
            "Criar Reunião de Meio de Semana",
            "Gere documentos para reuniões de meio de semana",
            "primary",
            self.criar_quadro_de_anuncio,
            0, 0
        )
        self.create_card(
            "Criar Reunião Final de Semana",
            "Gere documentos para reuniões de final de semana",
            "primary",
            self.criar_reuniao_final_semana,
            0, 1
        )
        
        # Linha 1: Publicadores
        self.create_card(
            "Publicadores",
            "Gerencie a lista de publicadores",
            "info",
            self.publicadores,
            1, 0
        )
        self.create_card(
            "Histórico de Publicadores",
            "Visualize o histórico de partes dos publicadores",
            "success",
            self.historico_publicadores,
            1, 1
        )
        
        # Linha 2: Históricos de reuniões
        self.create_card(
            "Histórico Reunião Meio de Semana",
            "Visualize o histórico de reuniões de meio de semana",
            "warning",
            self.historico,
            2, 0
        )
        self.create_card(
            "Histórico Reunião Final de Semana",
            "Visualize o histórico de reuniões de final de semana",
            "secondary",
            self.historico_final_semana,
            2, 1
        )
        
        # Linha 3: Designações Salão + Dashboards
        self.create_card(
            "Designações Salão",
            "Gerencie áudio, vídeo, microfone e indicadores",
            "info",
            self.designacoes_salao,
            3, 0
        )
        self.create_card(
            "Dashboards",
            "Visualize estatísticas e gráficos",
            "danger",
            self.dashboards,
            3, 1
        )
        
        # Rodapé
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill=X, pady=(20, 0))
        
        version_label = ttk.Label(
            footer_frame,
            text="Versão 1.0",
            bootstyle="secondary"
        )
        version_label.pack(side=RIGHT)

        gear_btn = ttk.Button(
            self.main_frame,
            text="⚙",
            bootstyle="secondary-outline",
            width=3,
            command=self.abrir_configuracoes
        )
        gear_btn.place(relx=1.0, rely=0.0, anchor="ne")

    def create_card(self, title, description, style, command, row, col, columnspan=1):
        """Cria um card estilizado com título, descrição e botão.

        Delega para views.components.criar_card (extraído do god object — SDD 03).
        """
        return criar_card(self.cards_frame, title, description, style, command,
                          row, col, columnspan)

def _verificar_atualizacao_async(root):
    """Verifica atualização em background e, se houver, oferece instalar."""
    def _worker():
        info = updater.verificar_atualizacao()
        if info:
            root.after(0, lambda: _oferecer_atualizacao(root, info))

    threading.Thread(target=_worker, daemon=True).start()


def _oferecer_atualizacao(root, info):
    """Pergunta ao usuário e conduz download + instalação."""
    resposta = Messagebox.yesno(
        f"Uma nova versão ({info['versao']}) está disponível.\n\n"
        "Deseja baixar e instalar agora? O aplicativo será fechado durante a "
        "atualização.",
        "Atualização disponível",
        parent=root,
    )
    if resposta != "Yes":
        return

    # Janela simples de progresso.
    win = ttk.Toplevel(root)
    win.title("Baixando atualização")
    win.geometry("360x120")
    win.transient(root)
    win.resizable(False, False)
    ttk.Label(win, text="Baixando o instalador, aguarde...").pack(pady=(20, 10))
    barra = ttk.Progressbar(win, mode="determinate", maximum=100, length=320)
    barra.pack(pady=5)

    def _on_progress(baixado, total):
        pct = int(baixado * 100 / total) if total else 0
        root.after(0, lambda: barra.configure(value=pct))

    def _baixar():
        try:
            caminho = updater.baixar_instalador(info["url"], on_progress=_on_progress)
        except Exception as e:
            logging.getLogger(__name__).error(f"Falha ao baixar atualização: {e}")
            root.after(0, win.destroy)
            root.after(0, lambda: Messagebox.show_error(
                "Não foi possível baixar a atualização. Tente novamente mais tarde.",
                "Erro na atualização", parent=root))
            return
        # Lança o instalador e encerra o app (libera arquivos para substituição).
        updater.lancar_instalador_e_sair(caminho)

    threading.Thread(target=_baixar, daemon=True).start()


if __name__ == "__main__":
    try:
        # Criar janela principal com tema
        root = ttk.Window(themename="litera")
        root.title("JW Mural")

        # Capturar exceções de callbacks tkinter no log (console=False swallows them)
        _main_logger = logging.getLogger(__name__)
        def _tk_exception(exc, val, tb):
            _main_logger.error("Exceção em callback tkinter", exc_info=(exc, val, tb))
        root.report_callback_exception = _tk_exception
        
        # Corrigir texto dos botões no Windows (evitar "só traço colorido" por fonte inválida)
        try:
            style = root.style
            font_btn = ("Segoe UI", 10)
            style.configure("TButton", font=font_btn)
            for name in ("primary", "secondary", "success", "info", "warning", "danger"):
                for suffix in ("", "-outline", "-link", "-round", "-round-toggle"):
                    try:
                        style.configure(f"{name}{suffix}.TButton", font=font_btn)
                    except tk.TclError:
                        pass
        except Exception:
            pass
        
        # Configurar geometria da janela principal
        window_width = 1024
        window_height = 768
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Criar aplicação
        app = ModernApp(root)
        
        # Forçar atualização da janela principal
        root.update_idletasks()
        root.deiconify()
        root.update()
        
        # Função para iniciar as verificações após a janela principal estar visível
        def start_checks():
            if not initialize_application(root):
                Messagebox.show_error(
                    "Não foi possível inicializar o sistema. Verifique os logs para mais detalhes.",
                    "Erro de Inicialização"
                )
                root.quit()
                sys.exit(1)
            # Verificar atualizações (apenas no app compilado) sem travar a UI.
            if getattr(sys, 'frozen', False):
                root.after(500, lambda: _verificar_atualizacao_async(root))
        
        # Agendar a inicialização para acontecer após a janela principal estar pronta
        root.after(100, start_checks)
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Erro ao iniciar a aplicação: {str(e)}")
        Messagebox.show_error(
            f"Ocorreu um erro ao iniciar a aplicação:\n{str(e)}",
            "Erro Fatal"
        )
        sys.exit(1)
