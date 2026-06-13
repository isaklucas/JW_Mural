import json
import logging
import sys
from pathlib import Path
from datetime import date

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


def backup_database() -> bool:
    """Exporta todas as collections MongoDB para JSON em backups/<YYYY-MM-DD>/ na raiz do projeto."""
    try:
        from database.db_connection import db_connection

        if db_connection.db_type != 'mongodb':
            logger.info("Backup ignorado: banco não é MongoDB")
            return True

        backup_dir = _project_root() / "backups" / str(date.today())

        if backup_dir.exists():
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
        return True

    except Exception as e:
        logger.error(f"Erro no backup: {e}")
        return False


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
