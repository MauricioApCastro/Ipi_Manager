from typing import List, Optional
from src.models.aluno import Aluno
from src.models.maquina import Maquina

class AlunoRepository:
    def __init__(self, db):
        self.db = db

    def add(self, aluno: Aluno):
        """Salva um novo aluno no banco de dados."""
        query = """
            INSERT INTO alunos (nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento, modulo_atual, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                aluno.nome, aluno.whatsapp_aluno, aluno.whatsapp_resp, 
                aluno.cpf, aluno.nascimento, aluno.modulo_atual, aluno.observacoes
            ))
            conn.commit()
            aluno.id = cursor.lastrowid

    def get_all(self) -> List[Aluno]:
        """Busca todos os alunos cadastrados."""
        query = "SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento, licao_atual, modulo_atual, observacoes FROM alunos"
        alunos = []
        with self.db.connection() as conn:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                aluno = Aluno(*row[:6])
                aluno.licao_atual = row[6]
                aluno.modulo_atual = row[7]
                aluno.observacoes = row[8]
                alunos.append(aluno)
        return alunos

    def get_by_name(self, nome: str) -> Optional[Aluno]:
        """Busca um aluno específico pelo nome."""
        query = "SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento, licao_atual, modulo_atual, observacoes FROM alunos WHERE nome = ?"
        with self.db.connection() as conn:
            row = conn.execute(query, (nome,)).fetchone()
            if row:
                aluno = Aluno(*row[:6])
                aluno.licao_atual = row[6]
                aluno.modulo_atual = row[7]
                aluno.observacoes = row[8]
                return aluno
            return None

    def seed_alunos_teste(self):
        """Cria alunos fictícios para testar a interface se o banco estiver vazio."""
        if len(self.get_all()) > 0:
            return
        alunos_fake = [
            ("Maurício", "11999999999", "", "123.456.789-00", "15/05/1990"),
            ("Ana Paula", "11888888888", "", "987.654.321-11", "20/10/1985"),
            ("Carlos Eduardo", "", "11777777777", "444.555.666-77", "10/01/2012"),
            ("Mariana Silva", "11666666666", "", "222.333.111-88", "05/03/1998")
        ]
        query = """
            INSERT INTO alunos (nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento, modulo_atual) 
            VALUES (?, ?, ?, ?, ?, 'Introdução')
        """
        with self.db.connection() as conn:
            conn.executemany(query, alunos_fake)
            conn.commit()
            print(f"{len(alunos_fake)} alunos de teste semeados.")

    def atualizar_progresso(self, aluno_id, nova_licao, novo_modulo=None):
        """Atualiza a aula e opcionalmente o módulo do aluno."""
        if novo_modulo:
            query = "UPDATE alunos SET licao_atual = ?, modulo_atual = ? WHERE id = ?"
            params = (nova_licao, novo_modulo, aluno_id)
        else:
            query = "UPDATE alunos SET licao_atual = ? WHERE id = ?"
            params = (nova_licao, aluno_id)
            
        with self.db.connection() as conn:
            conn.execute(query, params)
            conn.commit()

    def salvar_observacao_aluno(self, nome_aluno, texto_obs):
        """Grava as anotações da professora na ficha do aluno."""
        query = "UPDATE alunos SET observacoes = ? WHERE nome = ?"
        with self.db.connection() as conn:
            conn.execute(query, (texto_obs, nome_aluno))
            conn.commit()

class MaquinaRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self) -> List[Maquina]:
        """Busca o estado de todas as máquinas."""
        query = "SELECT id, tag, status, ocupante FROM maquinas ORDER BY tag"
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
            for i in range(1, quantidade + 1):
                tag = f"PC-{i:02d}"
                conn.execute(query, (tag, "VAGO"))
            conn.commit()
            print(f"{quantidade} máquinas semeadas no banco.")

    def salvar_alocacao(self, tag_maquina, nome_aluno):
        """Vincula um aluno a uma máquina no banco."""
        query = "UPDATE maquinas SET status = 'OCUPADO', ocupante = ? WHERE tag = ?"
        with self.db.connection() as conn:
            conn.execute(query, (nome_aluno, tag_maquina))
            conn.commit()
    
    def finalizar_alocacao(self, tag_maquina):
        """Libera a máquina no banco de dados."""
        query = "UPDATE maquinas SET status = 'VAGO', ocupante = NULL WHERE tag = ?"
        with self.db.connection() as conn:
            conn.execute(query, (tag_maquina,))
            conn.commit()