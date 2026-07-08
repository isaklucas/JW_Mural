import os
import sys
import logging
import platform
from typing import Dict, List, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def _get_base_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # system_checks.py → util/ → src/ → raiz
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_DIR = _get_base_dir()

class SystemChecks:
    @staticmethod
    def check_directories() -> List[str]:
        """Verifica se todos os diretórios necessários existem"""
        required_dirs = [
            'assets',
            'documentosCriados',
            'Templates',
        ]

        missing_dirs = []
        for dir_name in required_dirs:
            full_path = os.path.join(BASE_DIR, dir_name)
            if not os.path.exists(full_path):
                missing_dirs.append(dir_name)
                logger.warning(f"Diretório não encontrado: {full_path}")

        return missing_dirs

    @staticmethod
    def check_required_files() -> List[str]:
        """Verifica se todos os arquivos necessários existem"""
        required_files = [
            'Templates/Template_PT.docx',
            'Templates/template_final_semana_sentinela.docx',
            'Templates/template_final_semana_oradores.docx',
            '.env'
        ]

        missing_files = []
        for file_name in required_files:
            full_path = os.path.join(BASE_DIR, file_name)
            if not os.path.exists(full_path):
                missing_files.append(file_name)
                logger.warning(f"Arquivo não encontrado: {full_path}")
        
        return missing_files

    @staticmethod
    def check_environment() -> Dict[str, bool]:
        """Verifica variáveis de ambiente necessárias"""
        required_env_vars = [
            'DB_TYPE',
            'MONGODB_URI',
            'MONGODB_DB_NAME',
            'MONGODB_COLLECTION'
        ]
        
        env_status = {}
        for var in required_env_vars:
            env_status[var] = var in os.environ
            if not env_status[var]:
                logger.warning(f"Variável de ambiente não encontrada: {var}")
        
        return env_status

    @staticmethod
    def check_system_requirements() -> Dict[str, bool]:
        """Verifica requisitos do sistema"""
        requirements = {
            'os': platform.system(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0]
        }
        
        logger.info(f"Sistema Operacional: {requirements['os']}")
        logger.info(f"Versão Python: {requirements['python_version']}")
        logger.info(f"Arquitetura: {requirements['architecture']}")
        
        return requirements

    @staticmethod
    def run_all_checks() -> Tuple[bool, Dict[str, List]]:
        """Executa todas as verificações do sistema"""
        logger.info("Iniciando verificações do sistema...")
        
        results = {
            'missing_directories': SystemChecks.check_directories(),
            'missing_files': SystemChecks.check_required_files(),
            'environment': SystemChecks.check_environment(),
            'system': SystemChecks.check_system_requirements()
        }
        
        # Verifica se há algum problema crítico
        has_critical_issues = (
            len(results['missing_directories']) > 0 or
            len(results['missing_files']) > 0 or
            not all(results['environment'].values())
        )
        
        if has_critical_issues:
            logger.error("Foram encontrados problemas críticos no sistema")
        else:
            logger.info("Todas as verificações do sistema foram concluídas com sucesso")
        
        return not has_critical_issues, results 