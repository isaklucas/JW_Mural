import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import time
import logging
from .system_checks import SystemChecks
from .db_utils import db_utils
from .backup import backup_database

logger = logging.getLogger(__name__)

class StartupManager:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.root = None
        self.progress_var = None
        self.status_label = None
        self.error_occurred = False
        self.error_message = ""
        # Criar o tema uma única vez
        self.style = ttk.Style(theme="litera")

    def create_loading_window(self):
        """Cria a janela de loading"""
        try:
            # Criar janela modal
            self.root = ttk.Toplevel(self.parent)
            self.root.title("Iniciando Sistema")
            
            # Configurar como modal
            self.root.transient(self.parent)
            self.root.grab_set()
            
            # Remover decorações da janela
            self.root.overrideredirect(True)
            
            # Configurar geometria
            window_width = 400
            window_height = 150
            
            # Frame principal com fundo branco e borda
            main_frame = ttk.Frame(self.root, bootstyle="light")
            main_frame.pack(fill=BOTH, expand=True, padx=2, pady=2)
            
            # Container interno
            content_frame = ttk.Frame(main_frame)
            content_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
            
            # Label de status
            self.status_label = ttk.Label(
                content_frame,
                text="Iniciando verificações do sistema...",
                font=('Helvetica', 10),
                bootstyle="primary"
            )
            self.status_label.pack(pady=(0, 15))
            
            # Frame da barra de progresso
            progress_frame = ttk.Frame(content_frame)
            progress_frame.pack(fill=X)
            
            # Barra de progresso
            self.progress_var = ttk.DoubleVar(value=0)
            progress_bar = ttk.Progressbar(
                progress_frame,
                variable=self.progress_var,
                maximum=100,
                mode='determinate',
                bootstyle="primary-striped",
                length=300
            )
            progress_bar.pack(fill=X)
            
            # Forçar atualização para garantir que as dimensões estejam corretas
            self.root.update_idletasks()
            
            # Obter dimensões da tela
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calcular posição para centralizar na tela
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Configurar geometria e posição
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Garantir que a janela está visível e na frente
            self.root.lift()
            self.root.focus_force()
            
            # Atualizar a janela
            self.root.update()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar janela de loading: {str(e)}")
            return False

    def update_status(self, message: str, progress: float):
        """Atualiza o status na interface"""
        if not self.root:
            return
            
        try:
            if self.status_label:
                self.status_label.configure(text=message)
            if self.progress_var:
                self.progress_var.set(progress)
            self.root.update()
            self.root.lift()  # Mantém a janela na frente
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {str(e)}")

    def show_error(self, message: str):
        """Mostra mensagem de erro"""
        if not self.root:
            return
            
        try:
            self.error_occurred = True
            self.error_message = message
            if self.status_label:
                self.status_label.configure(text=f"Erro: {message}", bootstyle="danger")
            self.root.update()
            self.root.lift()  # Mantém a janela na frente
            time.sleep(2)
        except Exception as e:
            logger.error(f"Erro ao mostrar erro: {str(e)}")

    def close_window(self):
        """Fecha a janela de loading com segurança"""
        try:
            if self.root:
                self.root.grab_release()
                self.root.destroy()
        except Exception as e:
            logger.error(f"Erro ao fechar janela: {str(e)}")
        finally:
            self.root = None
            self.status_label = None
            self.progress_var = None

    def run_checks(self) -> bool:
        """Executa todas as verificações necessárias"""
        try:
            # Verificar sistema
            self.update_status("Verificando requisitos do sistema...", 20)
            system_ok, system_status = SystemChecks.run_all_checks()
            if not system_ok:
                error_msg = "Falha na verificação do sistema"
                if system_status.get('missing_directories'):
                    error_msg += f"\nDiretórios faltando: {', '.join(system_status['missing_directories'])}"
                if system_status.get('missing_files'):
                    error_msg += f"\nArquivos faltando: {', '.join(system_status['missing_files'])}"
                self.show_error(error_msg)
                return False

            # Verificar conexão com banco
            self.update_status("Verificando conexão com banco de dados...", 40)
            if not db_utils.verify_mongodb_connection():
                self.show_error("Não foi possível conectar ao banco de dados")
                return False

            # Backup diário
            self.update_status("Realizando backup do banco de dados...", 55)
            backup_database()

            # Verificar estrutura do banco
            self.update_status("Verificando estrutura do banco de dados...", 70)
            if not db_utils.setup_mongodb_structure():
                self.show_error("Erro ao configurar estrutura do banco de dados")
                return False

            # Verificação final
            self.update_status("Finalizando verificações...", 85)
            db_status = db_utils.get_database_status()
            if not db_status['connected'] or not db_status['structured']:
                self.show_error("Erro na configuração final do banco de dados")
                return False

            # Sucesso
            self.update_status("Sistema iniciado com sucesso!", 100)
            time.sleep(1)
            return True

        except Exception as e:
            logger.error(f"Erro durante a inicialização: {str(e)}")
            self.show_error(f"Erro inesperado: {str(e)}")
            return False

    def initialize_system(self) -> bool:
        """Inicializa o sistema com interface visual"""
        try:
            if not self.create_loading_window():
                return False
            return self.run_checks()
        except Exception as e:
            logger.error(f"Erro na inicialização do sistema: {str(e)}")
            return False
        finally:
            self.close_window()

def initialize_application(parent_window) -> bool:
    """Função principal para inicializar a aplicação"""
    startup = StartupManager(parent_window)
    return startup.initialize_system() 