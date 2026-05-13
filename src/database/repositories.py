from typing import List, Optional
from src.models.aluno import Aluno
from src.models.maquina import Maquina

class AlunoRepository:
    def __init__(self, db):
        self.db = db

    def add(self, aluno: Aluno):
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
        query = "SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento, licao_atual FROM alunos"
        alunos = []
        with self.db.connection() as conn:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                aluno = Aluno(*row[:6])
                aluno.licao_atual = row[6]
                alunos.append(aluno)
        return alunos

    def get_by_name(self, nome: str) -> Optional[Aluno]:
        query = "SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento, licao_atual FROM alunos WHERE nome = ?"
        with self.db.connection() as conn:
            row = conn.execute(query, (nome,)).fetchone()
            if row:
                aluno = Aluno(*row[:6])
                aluno.licao_atual = row[6]
                return aluno
            return None

    def seed_alunos_teste(self):
        if len(self.get_all()) > 0:
            return
        alunos_fake = [
            ("Maurício", "11999999999", "", "123.456.789-00", "15/05/1990"),
            ("Ana Paula", "11888888888", "", "987.654.321-11", "20/10/1985"),
            ("Carlos Eduardo", "", "11777777777", "444.555.666-77", "10/01/2012"),
            ("Mariana Silva", "11666666666", "", "222.333.111-88", "05/03/1998")
        ]
        query = "INSERT INTO alunos (nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento) VALUES (?, ?, ?, ?, ?)"
        with self.db.connection() as conn:
            conn.executemany(query, alunos_fake)
            conn.commit()
            print(f"{len(alunos_fake)} alunos de teste semeados.")

    def atualizar_licao(self, aluno_id, nova_licao):
        query = "UPDATE alunos SET licao_atual = ? WHERE id = ?"
        with self.db.connection() as conn:
            conn.execute(query, (nova_licao, aluno_id))
            conn.commit()

class MaquinaRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self) -> List[Maquina]:
        # Busca as 4 colunas: id, tag, status, ocupante
        query = "SELECT id, tag, status, ocupante FROM maquinas ORDER BY tag"
        maquinas = []
        with self.db.connection() as conn:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                # Aqui o row tem 4 itens, que o Maquina(*row) desempacota
                maquinas.append(Maquina(*row))
        return maquinas

    def seed_maquinas(self, quantidade=8):
        if len(self.get_all()) > 0:
            return
        query = "INSERT INTO maquinas (tag, status) VALUES (?, ?)"
        with self.db.connection() as conn:
            for i in range(1, quantidade + 1):
                tag = f"PC-{i:02d}"
                conn.execute(query, (tag, "VAGO"))
            conn.commit()
            print(f"{quantidade} máquinas semeadas no banco.")

    def salvar_alocacao(self, tag_maquina, nome_aluno):
        """Atualiza o banco para OCUPADO e grava o nome do aluno."""
        query = "UPDATE maquinas SET status = 'OCUPADO', ocupante = ? WHERE tag = ?"
        with self.db.connection() as conn:
            conn.execute(query, (nome_aluno, tag_maquina))
            conn.commit() # ISSO AQUI É O QUE FAZ O SAVE DE VERDADE
            print(f"Banco: {tag_maquina} agora ocupada por {nome_aluno}")
    
    def finalizar_alocacao(self, tag_maquina):
        query = "UPDATE maquinas SET status = 'VAGO', ocupante = NULL WHERE tag = ?"
        with self.db.connection() as conn:
            conn.execute(query, (tag_maquina,))
            conn.commit()