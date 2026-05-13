import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, db_name="escola.db"):
        self.db_name = db_name
        self.inicializar_tabelas()

    @contextmanager
    def connection(self):
        """Cria um gerenciador de contexto para a conexão."""
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query, params=()):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def inicializar_tabelas(self):
        query_alunos = """
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            whatsapp_aluno TEXT,
            whatsapp_resp TEXT,
            cpf TEXT,
            nascimento TEXT,
            modulo_atual TEXT,
            licao_atual INTEGER DEFAULT 1,
            observacoes TEXT
        );"""
        query_maquinas = """
        CREATE TABLE IF NOT EXISTS maquinas (
            tag TEXT PRIMARY KEY,
            status TEXT DEFAULT 'VAGO',
            ocupante TEXT
        );"""
        self.execute_query(query_alunos)
        self.execute_query(query_maquinas)