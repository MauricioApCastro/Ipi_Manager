from typing import List, Optional
from src.models.aluno import Aluno
from src.models.maquina import Maquina  # Faltava esse import!

class AlunoRepository:
    def __init__(self, db):
        self.db = db

    def add(self, aluno: Aluno):
        """Salva um novo aluno no banco de dados."""
        query = """
            INSERT INTO alunos (nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento)
            VALUES (?, ?, ?, ?, ?)
        """
        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                aluno.nome, 
                aluno.whatsapp_aluno, 
                aluno.whatsapp_resp, 
                aluno.cpf, 
                aluno.nascimento
            ))
            conn.commit()
            aluno.id = cursor.lastrowid

    def get_all(self) -> List[Aluno]:
        """Busca todos os alunos e os transforma em objetos Aluno."""
        query = "SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento FROM alunos"
        alunos = []
        with self.db.connection() as conn:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                alunos.append(Aluno(*row))
        return alunos

    def get_by_id(self, aluno_id: int) -> Optional[Aluno]:
        """Busca um aluno específico pelo ID."""
        query = "SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento FROM alunos WHERE id = ?"
        with self.db.connection() as conn:
            row = conn.execute(query, (aluno_id,)).fetchone()
            return Aluno(*row) if row else None

        
class MaquinaRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self) -> List[Maquina]:
        """Busca todas as máquinas cadastradas."""
        query = "SELECT id, tag, status FROM maquinas ORDER BY tag"
        maquinas = []
        with self.db.connection() as conn:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                maquinas.append(Maquina(*row))
        return maquinas

    def seed_maquinas(self, quantidade=8):
        """Cria os PCs iniciais se a tabela estiver vazia."""
        if len(self.get_all()) > 0:
            return

        query = "INSERT INTO maquinas (tag, status) VALUES (?, ?)"
        with self.db.connection() as conn:
            cursor = conn.cursor()
            for i in range(1, quantidade + 1):
                tag = f"PC-{i:02d}"
                cursor.execute(query, (tag, "ATIVO"))
            conn.commit()
            print(f"{quantidade} máquinas semeadas no banco.")