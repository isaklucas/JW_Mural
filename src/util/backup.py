import json
import logging
import shutil
import sys
from pathlib import Path
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


def backup_database(sufixo: str = "", forcar: bool = False) -> bool:
    """Exporta todas as collections MongoDB para JSON em backups/<YYYY-MM-DD><sufixo>/.

    Args:
        sufixo: sufixo da pasta do dia. Vazio = backup do arranque; "-saida" = backup
                gravado no encerramento do app (assim o snapshot do arranque, de antes
                das edições do dia, não é sobrescrito).
        forcar: regrava mesmo se a pasta do dia já existir (usado no encerramento,
                que deve refletir sempre o estado mais recente).
    """
    try:
        from database.db_connection import db_connection

        if db_connection.db_type != 'mongodb':
            logger.info("Backup ignorado: banco não é MongoDB")
            return True

        backup_dir = _project_root() / "backups" / f"{date.today()}{sufixo}"

        if backup_dir.exists() and not forcar:
            logger.info(f"Backup de hoje já existe: {backup_dir}")
            return True

        backup_dir.mkdir(parents=True, exist_ok=True)

        db = db_connection.db
        collections = db.list_collection_names()

        for name in collections:
            docs = list(db[name].find({}))
            filepath = backup_dir / f"{name}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(docs, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"Backup {name}: {len(docs)} documentos")

        logger.info(f"Backup concluído: {backup_dir} ({len(collections)} collections)")
        limpar_backups_antigos()
        return True

    except Exception as e:
        logger.error(f"Erro no backup: {e}")
        return False


def limpar_backups_antigos(dias: int = 30) -> int:
    """Remove pastas de backup mais velhas que `dias`. Retorna quantas foram apagadas.

    A data vem dos 10 primeiros caracteres do nome da pasta ("2026-08-11" e
    "2026-08-11-saida" contam como o mesmo dia). Pasta com nome fora desse padrão é
    ignorada — nunca apagamos algo que o usuário criou à mão.
    """
    removidas = 0
    try:
        backups_root = _project_root() / "backups"
        if not backups_root.exists():
            return 0

        limite = date.today() - timedelta(days=dias)

        for pasta in backups_root.iterdir():
            if not pasta.is_dir():
                continue
            try:
                data_pasta = datetime.strptime(pasta.name[:10], "%Y-%m-%d").date()
            except ValueError:
                continue
            if data_pasta < limite:
                shutil.rmtree(pasta, ignore_errors=True)
                removidas += 1
                logger.info(f"Backup antigo removido: {pasta}")

        return removidas

    except Exception as e:
        logger.error(f"Erro ao limpar backups antigos: {e}")
        return removidas


def restore_database(backup_date: str, collections: list) -> dict:
    """Restaura collections MongoDB a partir de JSON em backups/<backup_date>/."""
    try:
        from database.db_connection import db_connection

        backup_dir = _project_root() / "backups" / backup_date

        db = db_connection.db
        results = {}

        for name in collections:
            filepath = backup_dir / f"{name}.json"
            if not filepath.exists():
                results[name] = {"status": "arquivo não encontrado", "count": 0}
                continue
            with open(filepath, encoding='utf-8') as f:
                docs = json.load(f)
            for d in docs:
                d.pop('_id', None)
            db[name].drop()
            if docs:
                db[name].insert_many(docs)
            results[name] = {"status": "ok", "count": len(docs)}
            logger.info(f"Restaurado {name}: {len(docs)} documentos")

        return results

    except Exception as e:
        logger.error(f"Erro no restore: {e}")
        raise
