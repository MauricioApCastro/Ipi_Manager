from typing import List, Optional
from src.models.aluno import Aluno

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
            aluno.id = cursor.lastrowid # Atualiza o objeto com o ID gerado

    def get_all(self) -> List[Aluno]:
        """Busca todos os alunos e os transforma em objetos Aluno."""
        query = "SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento FROM alunos"
        alunos = []
        with self.db.connection() as conn:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                # Desempacota a linha do banco diretamente no construtor da Dataclass
                alunos.append(Aluno(*row))
        return alunos

    def get_by_id(self, aluno_id: int) -> Optional[Aluno]:
        """Busca um aluno específico pelo ID."""
        query = "SELECT * FROM alunos WHERE id = ?"
        with self.db.connection() as conn:
            row = conn.execute(query, (aluno_id,)).fetchone()
            return Aluno(*row) if row else None