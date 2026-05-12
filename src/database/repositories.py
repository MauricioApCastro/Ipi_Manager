from typing import List, Optional
from src.models.aluno import Aluno
from src.models.maquina import Maquina
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
    
    def seed_alunos_teste(self):
        """Cria alunos fictícios para testar a interface."""
        if len(self.get_all()) > 0:
            return

        alunos_fake = [
            ("Maurício", "11999999999", "", "123.456.789-00", "15/05/1990"),
            ("Ana Paula", "11888888888", "", "987.654.321-11", "20/10/1985"),
            ("Carlos Eduardo", "", "11777777777", "444.555.666-77", "10/01/2012"), # Menor de idade
            ("Mariana Silva", "11666666666", "", "222.333.111-88", "05/03/1998")
        ]

        query = """
            INSERT INTO alunos (nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento)
            VALUES (?, ?, ?, ?, ?)
        """
        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, alunos_fake)
            conn.commit()
            print(f"{len(alunos_fake)} alunos de teste semeados.")


        
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

    
        """Cria alunos fictícios para testar a interface."""
        if len(self.get_all()) > 0:
            return

        alunos_fake = [
            ("Maurício", "11999999999", "", "123.456.789-00", "15/05/1990"),
            ("Ana Paula", "11888888888", "", "987.654.321-11", "20/10/1985"),
            ("Carlos Eduardo", "", "11777777777", "444.555.666-77", "10/01/2012"), # Menor de idade
            ("Mariana Silva", "11666666666", "", "222.333.111-88", "05/03/1998")
        ]

        query = """
            INSERT INTO alunos (nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento)
            VALUES (?, ?, ?, ?, ?)
        """
        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, alunos_fake)
            conn.commit()
            print(f"{len(alunos_fake)} alunos de teste semeados.")

            
    def salvar_alocacao(self, tag_maquina, nome_aluno):

        """Salva o nome do aluno e muda o status da máquina no banco."""
        query = "UPDATE maquinas SET status = 'OCUPADO', ocupante = ? WHERE tag = ?"
        with self.db.connection() as conn:
            conn.execute(query, (nome_aluno, tag_maquina))
            conn.commit()