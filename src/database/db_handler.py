import sqlite3
from contextlib import contextmanager
import os
import sys


def default_database_path():
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "data", "escola.db")


class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or default_database_path()
        # Garante que a pasta 'data' exista
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    @contextmanager
    def connection(self):
        """Gerenciador de contexto para garantir que a conexão sempre feche."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def execute_script(self, script_path):
        """Executa um arquivo .sql para criar ou atualizar as tabelas."""
        with self.connection() as conn:
            with open(script_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
