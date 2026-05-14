from datetime import datetime, timedelta
from typing import List, Optional

from src.models.aluno import Aluno
from src.models.maquina import Maquina


class AlunoRepository:
    def __init__(self, db):
        self.db = db
        self.ensure_schema()

    def ensure_schema(self):
        with self.db.connection() as conn:
            self._add_column_if_missing(conn, "alunos", "turma_id", "INTEGER")
            self._add_column_if_missing(conn, "turmas", "segundo_dia_semana", "TEXT")
            self._add_column_if_missing(conn, "turmas", "segundo_horario", "TEXT")
            self._add_column_if_missing(conn, "turmas", "duracao_aula_minutos", "INTEGER DEFAULT 60")
            self._add_column_if_missing(conn, "turmas", "aulas_por_semana", "INTEGER DEFAULT 2")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS aluno_modulos (
                    aluno_id INTEGER NOT NULL,
                    modulo_id INTEGER NOT NULL,
                    PRIMARY KEY (aluno_id, modulo_id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS presencas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno_id INTEGER NOT NULL,
                    maquina_tag TEXT,
                    data_hora TEXT NOT NULL,
                    observacao TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mensagens_responsavel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno_id INTEGER NOT NULL,
                    telefone TEXT,
                    mensagem TEXT NOT NULL,
                    data_hora TEXT NOT NULL,
                    status TEXT DEFAULT 'GERADA'
                )
            """)
            conn.commit()

    def _add_column_if_missing(self, conn, tabela, coluna, definicao):
        colunas = [row[1] for row in conn.execute(f"PRAGMA table_info({tabela})").fetchall()]
        if coluna not in colunas:
            conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")

    def add(self, aluno: Aluno):
        query = """
            INSERT INTO alunos (
                nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento,
                modulo_atual, observacoes, turma_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.connection() as conn:
            cursor = conn.execute(
                query,
                (
                    aluno.nome,
                    aluno.whatsapp_aluno,
                    aluno.whatsapp_resp,
                    aluno.cpf,
                    aluno.nascimento,
                    aluno.modulo_atual,
                    aluno.observacoes,
                    aluno.turma_id,
                ),
            )
            aluno.id = cursor.lastrowid
            self._salvar_modulos(conn, aluno.id, getattr(aluno, "modulos_ids", []))
            conn.commit()

    def update(self, aluno: Aluno):
        query = """
            UPDATE alunos
            SET nome = ?,
                whatsapp_aluno = ?,
                whatsapp_resp = ?,
                cpf = ?,
                nascimento = ?,
                licao_atual = ?,
                modulo_atual = ?,
                observacoes = ?,
                turma_id = ?
            WHERE id = ?
        """
        with self.db.connection() as conn:
            conn.execute(
                query,
                (
                    aluno.nome,
                    aluno.whatsapp_aluno,
                    aluno.whatsapp_resp,
                    aluno.cpf,
                    aluno.nascimento,
                    aluno.licao_atual,
                    aluno.modulo_atual,
                    aluno.observacoes,
                    aluno.turma_id,
                    aluno.id,
                ),
            )
            self._salvar_modulos(conn, aluno.id, getattr(aluno, "modulos_ids", []))
            conn.commit()

    def delete(self, aluno_id):
        with self.db.connection() as conn:
            aluno = conn.execute("SELECT nome FROM alunos WHERE id = ?", (aluno_id,)).fetchone()
            if aluno:
                conn.execute("UPDATE maquinas SET status = 'VAGO', ocupante = NULL WHERE ocupante = ?", (aluno[0],))
            conn.execute("DELETE FROM aluno_modulos WHERE aluno_id = ?", (aluno_id,))
            conn.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
            conn.commit()

    def get_all(self) -> List[Aluno]:
        query = """
            SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento,
                   licao_atual, modulo_atual, observacoes, turma_id
            FROM alunos
            ORDER BY nome
        """
        alunos = []
        with self.db.connection() as conn:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                aluno = Aluno(*row[:6])
                aluno.licao_atual = row[6]
                aluno.modulo_atual = row[7]
                aluno.observacoes = row[8]
                aluno.turma_id = row[9]
                aluno.modulos_ids = self.get_modulos_aluno(aluno.id)
                alunos.append(aluno)
        return alunos

    def get_by_name(self, nome: str) -> Optional[Aluno]:
        query = """
            SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento,
                   licao_atual, modulo_atual, observacoes, turma_id
            FROM alunos
            WHERE nome = ?
        """
        with self.db.connection() as conn:
            row = conn.execute(query, (nome,)).fetchone()
            if row:
                aluno = Aluno(*row[:6])
                aluno.licao_atual = row[6]
                aluno.modulo_atual = row[7]
                aluno.observacoes = row[8]
                aluno.turma_id = row[9]
                aluno.modulos_ids = self.get_modulos_aluno(aluno.id)
                return aluno
            return None

    def get_modulos_aluno(self, aluno_id):
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT modulo_id FROM aluno_modulos WHERE aluno_id = ?",
                (aluno_id,),
            ).fetchall()
            return [row[0] for row in rows]

    def _salvar_modulos(self, conn, aluno_id, modulos_ids):
        conn.execute("DELETE FROM aluno_modulos WHERE aluno_id = ?", (aluno_id,))
        for modulo_id in modulos_ids:
            conn.execute(
                "INSERT OR IGNORE INTO aluno_modulos (aluno_id, modulo_id) VALUES (?, ?)",
                (aluno_id, modulo_id),
            )

    def get_turmas_com_vagas(self, capacidade_padrao=8):
        query = """
            SELECT turmas.id,
                   turmas.nome,
                   turmas.dia_semana,
                   turmas.horario,
                   turmas.segundo_dia_semana,
                   turmas.segundo_horario,
                   COALESCE(turmas.duracao_aula_minutos, 60) AS duracao,
                   COALESCE(turmas.aulas_por_semana, 2) AS aulas_semana,
                   COALESCE(turmas.capacidade_manual, ?) AS capacidade,
                   COUNT(alunos.id) AS ocupadas
            FROM turmas
            LEFT JOIN alunos ON alunos.turma_id = turmas.id
            GROUP BY turmas.id
            ORDER BY turmas.dia_semana, turmas.horario
        """
        with self.db.connection() as conn:
            return conn.execute(query, (capacidade_padrao,)).fetchall()

    def get_alunos_do_horario_atual(self):
        turmas_ativas = self.get_turmas_ativas_agora()
        if not turmas_ativas:
            return []

        turma_ids = [turma[0] for turma in turmas_ativas]
        placeholders = ",".join("?" for _ in turma_ids)
        query = f"""
            SELECT id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento,
                   licao_atual, modulo_atual, observacoes, turma_id
            FROM alunos
            WHERE turma_id IN ({placeholders})
            ORDER BY nome
        """
        alunos = []
        with self.db.connection() as conn:
            for row in conn.execute(query, turma_ids).fetchall():
                aluno = Aluno(*row[:6])
                aluno.licao_atual = row[6]
                aluno.modulo_atual = row[7]
                aluno.observacoes = row[8]
                aluno.turma_id = row[9]
                aluno.modulos_ids = self.get_modulos_aluno(aluno.id)
                alunos.append(aluno)
        return alunos

    def get_turmas_ativas_agora(self):
        agora = datetime.now()
        dia_atual = self._normalizar_dia_semana(agora.weekday())
        turmas = self.get_turmas_com_vagas()
        ativas = []

        for turma in turmas:
            (
                _turma_id,
                _nome,
                dia1,
                horario1,
                dia2,
                horario2,
                duracao,
                _aulas_semana,
                _capacidade,
                _ocupadas,
            ) = turma
            if self._horario_em_andamento(agora, dia_atual, dia1, horario1, duracao):
                ativas.append(turma)
            elif self._horario_em_andamento(agora, dia_atual, dia2, horario2, duracao):
                ativas.append(turma)

        return ativas

    def _horario_em_andamento(self, agora, dia_atual, dia_turma, horario_turma, duracao):
        if self._normalizar_texto_dia(dia_turma) != dia_atual:
            return False
        try:
            hora, minuto = [int(parte) for parte in (horario_turma or "").split(":")[:2]]
        except ValueError:
            return False

        inicio = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        fim = inicio + timedelta(minutes=duracao or 60)
        return inicio <= agora <= fim

    def _normalizar_dia_semana(self, weekday):
        dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
        return dias[weekday]

    def _normalizar_texto_dia(self, texto):
        substituicoes = {
            "á": "a", "à": "a", "ã": "a", "â": "a",
            "é": "e", "ê": "e",
            "í": "i",
            "ó": "o", "ô": "o", "õ": "o",
            "ú": "u",
            "ç": "c",
        }
        normalizado = (texto or "").strip().lower()
        for origem, destino in substituicoes.items():
            normalizado = normalizado.replace(origem, destino)
        return normalizado

    def seed_turmas_padrao(self):
        with self.db.connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM turmas").fetchone()[0]
            if total:
                ajustes = [
                    ("Manha 1", "Segunda", "08:00", "Quarta", "08:00"),
                    ("Manha 2", "Terca", "08:00", "Quinta", "08:00"),
                    ("Tarde 1", "Segunda", "14:00", "Quarta", "14:00"),
                    ("Noite 1", "Terca", "19:00", "Quinta", "19:00"),
                ]
                conn.executemany(
                    """
                    UPDATE turmas
                    SET dia_semana = ?,
                        horario = ?,
                        segundo_dia_semana = ?,
                        segundo_horario = ?,
                        duracao_aula_minutos = 60,
                        aulas_por_semana = 2,
                        capacidade_manual = COALESCE(capacidade_manual, 8)
                    WHERE nome = ?
                    """,
                    [(dia1, hora1, dia2, hora2, nome) for nome, dia1, hora1, dia2, hora2 in ajustes],
                )
                conn.execute("""
                    UPDATE turmas
                    SET segundo_dia_semana = COALESCE(segundo_dia_semana, dia_semana),
                        segundo_horario = COALESCE(segundo_horario, horario),
                        duracao_aula_minutos = COALESCE(duracao_aula_minutos, 60),
                        aulas_por_semana = COALESCE(aulas_por_semana, 2),
                        capacidade_manual = COALESCE(capacidade_manual, 8)
                """)
                conn.commit()
                return
            turmas = [
                ("Manha 1", "Segunda", "08:00", "Quarta", "08:00", 60, 2, 8),
                ("Manha 2", "Terca", "08:00", "Quinta", "08:00", 60, 2, 8),
                ("Tarde 1", "Segunda", "14:00", "Quarta", "14:00", 60, 2, 8),
                ("Noite 1", "Terca", "19:00", "Quinta", "19:00", 60, 2, 8),
            ]
            conn.executemany(
                """
                INSERT INTO turmas (
                    nome, dia_semana, horario, segundo_dia_semana, segundo_horario,
                    duracao_aula_minutos, aulas_por_semana, capacidade_manual
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                turmas,
            )
            conn.commit()

    def seed_alunos_teste(self):
        if len(self.get_all()) > 0:
            return
        alunos_fake = [
            ("Mauricio", "11999999999", "", "123.456.789-00", "15/05/1990"),
            ("Ana Paula", "11888888888", "", "987.654.321-11", "20/10/1985"),
            ("Carlos Eduardo", "", "11777777777", "444.555.666-77", "10/01/2012"),
            ("Mariana Silva", "11666666666", "", "222.333.111-88", "05/03/1998"),
        ]
        query = """
            INSERT INTO alunos (nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento, modulo_atual)
            VALUES (?, ?, ?, ?, ?, 'Introducao')
        """
        with self.db.connection() as conn:
            conn.executemany(query, alunos_fake)
            conn.commit()

    def atualizar_progresso(self, aluno_id, nova_licao, novo_modulo=None):
        if novo_modulo:
            query = "UPDATE alunos SET licao_atual = ?, modulo_atual = ? WHERE id = ?"
            params = (nova_licao, novo_modulo, aluno_id)
        else:
            query = "UPDATE alunos SET licao_atual = ? WHERE id = ?"
            params = (nova_licao, aluno_id)

        with self.db.connection() as conn:
            conn.execute(query, params)
            conn.commit()

    def concluir_curso(self, aluno_id):
        query = """
            UPDATE alunos
            SET licao_atual = 0,
                modulo_atual = 'Curso concluído',
                turma_id = NULL
            WHERE id = ?
        """
        with self.db.connection() as conn:
            conn.execute(query, (aluno_id,))
            conn.commit()

    def salvar_observacao_aluno(self, nome_aluno, texto_obs):
        query = "UPDATE alunos SET observacoes = ? WHERE nome = ?"
        with self.db.connection() as conn:
            conn.execute(query, (texto_obs, nome_aluno))
            conn.commit()

    def registrar_presenca(self, aluno_id, maquina_tag, observacao="Entrada registrada por alocação"):
        query = """
            INSERT INTO presencas (aluno_id, maquina_tag, data_hora, observacao)
            VALUES (?, ?, ?, ?)
        """
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.db.connection() as conn:
            conn.execute(query, (aluno_id, maquina_tag, data_hora, observacao))
            conn.commit()
        return data_hora

    def registrar_mensagem_responsavel(self, aluno_id, telefone, mensagem, status="GERADA"):
        query = """
            INSERT INTO mensagens_responsavel (aluno_id, telefone, mensagem, data_hora, status)
            VALUES (?, ?, ?, ?, ?)
        """
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.db.connection() as conn:
            conn.execute(query, (aluno_id, telefone, mensagem, data_hora, status))
            conn.commit()
        return data_hora


class MaquinaRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self) -> List[Maquina]:
        query = "SELECT id, tag, status, ocupante FROM maquinas ORDER BY tag"
        maquinas = []
        with self.db.connection() as conn:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
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

    def salvar_alocacao(self, tag_maquina, nome_aluno):
        query = "UPDATE maquinas SET status = 'OCUPADO', ocupante = ? WHERE tag = ?"
        with self.db.connection() as conn:
            conn.execute(query, (nome_aluno, tag_maquina))
            conn.commit()

    def finalizar_alocacao(self, tag_maquina):
        query = "UPDATE maquinas SET status = 'VAGO', ocupante = NULL WHERE tag = ?"
        with self.db.connection() as conn:
            conn.execute(query, (tag_maquina,))
            conn.commit()


class TurmaRepository:
    def __init__(self, db):
        self.db = db
        self.ensure_schema()

    def ensure_schema(self):
        with self.db.connection() as conn:
            self._add_column_if_missing(conn, "turmas", "segundo_dia_semana", "TEXT")
            self._add_column_if_missing(conn, "turmas", "segundo_horario", "TEXT")
            self._add_column_if_missing(conn, "turmas", "duracao_aula_minutos", "INTEGER DEFAULT 60")
            self._add_column_if_missing(conn, "turmas", "aulas_por_semana", "INTEGER DEFAULT 2")
            conn.commit()

    def _add_column_if_missing(self, conn, tabela, coluna, definicao):
        colunas = [row[1] for row in conn.execute(f"PRAGMA table_info({tabela})").fetchall()]
        if coluna not in colunas:
            conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")

    def get_all(self):
        query = """
            SELECT turmas.id,
                   turmas.nome,
                   turmas.dia_semana,
                   turmas.horario,
                   turmas.segundo_dia_semana,
                   turmas.segundo_horario,
                   COALESCE(turmas.duracao_aula_minutos, 60) AS duracao,
                   COALESCE(turmas.aulas_por_semana, 2) AS aulas_semana,
                   COALESCE(turmas.capacidade_manual, 8) AS capacidade,
                   COUNT(alunos.id) AS ocupadas
            FROM turmas
            LEFT JOIN alunos ON alunos.turma_id = turmas.id
            GROUP BY turmas.id
            ORDER BY turmas.dia_semana, turmas.horario
        """
        with self.db.connection() as conn:
            return conn.execute(query).fetchall()

    def add(self, nome, dia1, horario1, dia2, horario2, capacidade=8):
        query = """
            INSERT INTO turmas (
                nome, dia_semana, horario, segundo_dia_semana, segundo_horario,
                duracao_aula_minutos, aulas_por_semana, capacidade_manual
            )
            VALUES (?, ?, ?, ?, ?, 60, 2, ?)
        """
        with self.db.connection() as conn:
            cursor = conn.execute(query, (nome, dia1, horario1, dia2, horario2, capacidade))
            conn.commit()
            return cursor.lastrowid

    def update(self, turma_id, nome, dia1, horario1, dia2, horario2, capacidade=8):
        query = """
            UPDATE turmas
            SET nome = ?,
                dia_semana = ?,
                horario = ?,
                segundo_dia_semana = ?,
                segundo_horario = ?,
                duracao_aula_minutos = 60,
                aulas_por_semana = 2,
                capacidade_manual = ?
            WHERE id = ?
        """
        with self.db.connection() as conn:
            conn.execute(query, (nome, dia1, horario1, dia2, horario2, capacidade, turma_id))
            conn.commit()

    def delete(self, turma_id):
        with self.db.connection() as conn:
            conn.execute("UPDATE alunos SET turma_id = NULL WHERE turma_id = ?", (turma_id,))
            conn.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
            conn.commit()


class FinanceiroRepository:
    def __init__(self, db):
        self.db = db
        self.ensure_schema()

    def ensure_schema(self):
        with self.db.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS financeiro_alunos (
                    aluno_id INTEGER PRIMARY KEY,
                    data_primeiro_pagamento TEXT,
                    parcelas_pagas INTEGER DEFAULT 0,
                    valor_mensalidade REAL DEFAULT 135.00,
                    valor_atraso REAL DEFAULT 155.00,
                    dia_vencimento INTEGER DEFAULT 10,
                    pix TEXT DEFAULT '1196321-6999',
                    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
                )
            """)
            conn.commit()

    def get_config(self, aluno_id):
        query = """
            SELECT aluno_id, data_primeiro_pagamento, parcelas_pagas, valor_mensalidade,
                   valor_atraso, dia_vencimento, pix
            FROM financeiro_alunos
            WHERE aluno_id = ?
        """
        with self.db.connection() as conn:
            row = conn.execute(query, (aluno_id,)).fetchone()
            if row:
                return {
                    "aluno_id": row[0],
                    "data_primeiro_pagamento": row[1] or "",
                    "parcelas_pagas": row[2] or 0,
                    "valor_mensalidade": row[3] or 135.00,
                    "valor_atraso": row[4] or 155.00,
                    "dia_vencimento": row[5] or 10,
                    "pix": row[6] or "1196321-6999",
                }
        return {
            "aluno_id": aluno_id,
            "data_primeiro_pagamento": "",
            "parcelas_pagas": 0,
            "valor_mensalidade": 135.00,
            "valor_atraso": 155.00,
            "dia_vencimento": 10,
            "pix": "1196321-6999",
        }

    def salvar_config(self, aluno_id, data_primeiro_pagamento, parcelas_pagas, valor_mensalidade, valor_atraso, dia_vencimento, pix):
        query = """
            INSERT INTO financeiro_alunos (
                aluno_id, data_primeiro_pagamento, parcelas_pagas, valor_mensalidade,
                valor_atraso, dia_vencimento, pix
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(aluno_id) DO UPDATE SET
                data_primeiro_pagamento = excluded.data_primeiro_pagamento,
                parcelas_pagas = excluded.parcelas_pagas,
                valor_mensalidade = excluded.valor_mensalidade,
                valor_atraso = excluded.valor_atraso,
                dia_vencimento = excluded.dia_vencimento,
                pix = excluded.pix
        """
        with self.db.connection() as conn:
            conn.execute(
                query,
                (
                    aluno_id,
                    data_primeiro_pagamento,
                    parcelas_pagas,
                    valor_mensalidade,
                    valor_atraso,
                    dia_vencimento,
                    pix,
                ),
            )
            conn.commit()

    def registrar_pagamento(self, aluno_id):
        config = self.get_config(aluno_id)
        novas_pagas = min((config["parcelas_pagas"] or 0) + 1, 14)
        self.salvar_config(
            aluno_id,
            config["data_primeiro_pagamento"],
            novas_pagas,
            config["valor_mensalidade"],
            config["valor_atraso"],
            config["dia_vencimento"],
            config["pix"],
        )
        return novas_pagas


class CursoDuplicadoError(ValueError):
    pass


class CursoRepository:
    DURACAO_PADRAO_MESES = 14

    def __init__(self, db):
        self.db = db
        self.ensure_schema()

    def ensure_schema(self):
        with self.db.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cursos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    duracao_meses INTEGER DEFAULT 14,
                    valor_base REAL DEFAULT 135.00
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS modulos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_curso INTEGER,
                    nome TEXT NOT NULL,
                    ordem INTEGER,
                    carga_meses INTEGER DEFAULT 1,
                    permite_flexibilidade INTEGER DEFAULT 0,
                    pre_requisito_id INTEGER,
                    FOREIGN KEY (id_curso) REFERENCES cursos(id),
                    FOREIGN KEY (pre_requisito_id) REFERENCES modulos(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS aulas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_modulo INTEGER NOT NULL,
                    titulo TEXT NOT NULL,
                    ordem INTEGER,
                    observacoes TEXT,
                    FOREIGN KEY (id_modulo) REFERENCES modulos(id)
                )
            """)

            self._add_column_if_missing(conn, "cursos", "duracao_meses", "INTEGER DEFAULT 14")
            self._add_column_if_missing(conn, "modulos", "carga_meses", "INTEGER DEFAULT 1")
            self._add_column_if_missing(conn, "modulos", "permite_flexibilidade", "INTEGER DEFAULT 0")
            conn.execute(
                "UPDATE cursos SET duracao_meses = ? WHERE duracao_meses IS NULL OR duracao_meses <> ?",
                (self.DURACAO_PADRAO_MESES, self.DURACAO_PADRAO_MESES),
            )
            conn.commit()

    def _add_column_if_missing(self, conn, tabela, coluna, definicao):
        colunas = [row[1] for row in conn.execute(f"PRAGMA table_info({tabela})").fetchall()]
        if coluna not in colunas:
            conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")

    def get_cursos(self):
        query = "SELECT id, nome, duracao_meses, valor_base FROM cursos ORDER BY nome"
        with self.db.connection() as conn:
            return conn.execute(query).fetchall()

    def _nome_curso_em_uso(self, conn, nome, curso_id_ignorado=None):
        nome_normalizado = (nome or "").strip().lower()
        query = "SELECT id FROM cursos WHERE LOWER(TRIM(nome)) = ?"
        params = [nome_normalizado]
        if curso_id_ignorado is not None:
            query += " AND id <> ?"
            params.append(curso_id_ignorado)
        return conn.execute(query, params).fetchone() is not None

    def add_curso(self, nome, duracao_meses=14, valor_base=135.0):
        query = "INSERT INTO cursos (nome, duracao_meses, valor_base) VALUES (?, ?, ?)"
        with self.db.connection() as conn:
            if self._nome_curso_em_uso(conn, nome):
                raise CursoDuplicadoError("Já existe um curso com este nome.")
            cursor = conn.execute(query, (nome, self.DURACAO_PADRAO_MESES, valor_base))
            conn.commit()
            return cursor.lastrowid

    def update_curso(self, curso_id, nome, duracao_meses=14, valor_base=135.0):
        query = "UPDATE cursos SET nome = ?, duracao_meses = ?, valor_base = ? WHERE id = ?"
        with self.db.connection() as conn:
            if self._nome_curso_em_uso(conn, nome, curso_id):
                raise CursoDuplicadoError("Já existe um curso com este nome.")
            conn.execute(query, (nome, self.DURACAO_PADRAO_MESES, valor_base, curso_id))
            conn.commit()

    def delete_curso(self, curso_id):
        with self.db.connection() as conn:
            conn.execute(
                """
                DELETE FROM aluno_modulos
                WHERE modulo_id IN (
                    SELECT id FROM modulos WHERE id_curso = ?
                )
                """,
                (curso_id,),
            )
            conn.execute(
                """
                DELETE FROM aulas
                WHERE id_modulo IN (
                    SELECT id FROM modulos WHERE id_curso = ?
                )
                """,
                (curso_id,),
            )
            conn.execute("DELETE FROM modulos WHERE id_curso = ?", (curso_id,))
            conn.execute("DELETE FROM cursos WHERE id = ?", (curso_id,))
            conn.commit()

    def get_modulos(self, curso_id):
        query = """
            SELECT id, id_curso, nome, ordem, carga_meses, permite_flexibilidade, pre_requisito_id
            FROM modulos
            WHERE id_curso = ?
            ORDER BY ordem, id
        """
        with self.db.connection() as conn:
            return conn.execute(query, (curso_id,)).fetchall()

    def get_all_modulos(self):
        query = """
            SELECT modulos.id, modulos.id_curso, modulos.nome, modulos.ordem,
                   modulos.carga_meses, modulos.permite_flexibilidade,
                   modulos.pre_requisito_id
            FROM modulos
            ORDER BY modulos.ordem, modulos.nome
        """
        with self.db.connection() as conn:
            return conn.execute(query).fetchall()

    def add_modulo(self, curso_id, nome, ordem, carga_meses=1, permite_flexibilidade=False, pre_requisito_id=None):
        query = """
            INSERT INTO modulos (
                id_curso, nome, ordem, carga_meses, permite_flexibilidade, pre_requisito_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.db.connection() as conn:
            cursor = conn.execute(
                query,
                (curso_id, nome, ordem, carga_meses, int(permite_flexibilidade), pre_requisito_id),
            )
            conn.commit()
            return cursor.lastrowid

    def update_modulo(self, modulo_id, nome, ordem, carga_meses=1, permite_flexibilidade=False, pre_requisito_id=None):
        query = """
            UPDATE modulos
            SET nome = ?, ordem = ?, carga_meses = ?, permite_flexibilidade = ?, pre_requisito_id = ?
            WHERE id = ?
        """
        with self.db.connection() as conn:
            conn.execute(
                query,
                (nome, ordem, carga_meses, int(permite_flexibilidade), pre_requisito_id, modulo_id),
            )
            conn.commit()

    def delete_modulo(self, modulo_id):
        with self.db.connection() as conn:
            conn.execute("UPDATE modulos SET pre_requisito_id = NULL WHERE pre_requisito_id = ?", (modulo_id,))
            conn.execute("DELETE FROM aluno_modulos WHERE modulo_id = ?", (modulo_id,))
            conn.execute("DELETE FROM aulas WHERE id_modulo = ?", (modulo_id,))
            conn.execute("DELETE FROM modulos WHERE id = ?", (modulo_id,))
            conn.commit()

    def get_aulas(self, curso_id):
        query = """
            SELECT aulas.id, aulas.id_modulo, modulos.nome, aulas.titulo, aulas.ordem, aulas.observacoes
            FROM aulas
            INNER JOIN modulos ON modulos.id = aulas.id_modulo
            WHERE modulos.id_curso = ?
            ORDER BY modulos.ordem, aulas.ordem, aulas.id
        """
        with self.db.connection() as conn:
            return conn.execute(query, (curso_id,)).fetchall()

    def get_aulas_modulo(self, modulo_id):
        query = """
            SELECT aulas.id, aulas.id_modulo, modulos.nome, aulas.titulo, aulas.ordem, aulas.observacoes
            FROM aulas
            INNER JOIN modulos ON modulos.id = aulas.id_modulo
            WHERE aulas.id_modulo = ?
            ORDER BY aulas.ordem, aulas.id
        """
        with self.db.connection() as conn:
            return conn.execute(query, (modulo_id,)).fetchall()

    def add_aula(self, modulo_id, titulo, ordem, observacoes=""):
        query = "INSERT INTO aulas (id_modulo, titulo, ordem, observacoes) VALUES (?, ?, ?, ?)"
        with self.db.connection() as conn:
            cursor = conn.execute(query, (modulo_id, titulo, ordem, observacoes))
            conn.commit()
            return cursor.lastrowid

    def update_aula(self, aula_id, modulo_id, titulo, ordem, observacoes=""):
        query = """
            UPDATE aulas
            SET id_modulo = ?, titulo = ?, ordem = ?, observacoes = ?
            WHERE id = ?
        """
        with self.db.connection() as conn:
            conn.execute(query, (modulo_id, titulo, ordem, observacoes, aula_id))
            conn.commit()

    def delete_aula(self, aula_id):
        with self.db.connection() as conn:
            conn.execute("DELETE FROM aulas WHERE id = ?", (aula_id,))
            conn.commit()

    def gerar_cronograma_padrao(self):
        cursos = self.get_cursos()
        curso_id = cursos[0][0] if cursos else self.add_curso("Curso Completo IPI", 14)

        if self.get_modulos(curso_id):
            return curso_id

        for mes in range(1, 15):
            modulo_id = self.add_modulo(
                curso_id,
                f"Modulo {mes:02d}",
                mes,
                carga_meses=1,
                permite_flexibilidade=mes > 1,
            )
            for aula in range(1, 5):
                ordem = ((mes - 1) * 4) + aula
                self.add_aula(modulo_id, f"Aula {aula:02d}", ordem)

        return curso_id
