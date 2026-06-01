import os
import tempfile
import unittest
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication

from src.database.db_handler import Database
from src.database.repositories import (
    AlunoRepository,
    CursoDuplicadoError,
    CursoRepository,
    FinanceiroRepository,
    MaquinaRepository,
    TurmaRepository,
)
from src.models.aluno import Aluno
from src.services.recibo_service import gerar_recibo_pagamento_pdf
from src.ui.windows.main_window import MainWindow


APP = QApplication.instance() or QApplication([])


class SistemaFluxosTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "teste.db")
        self.db = Database(self.db_path)
        self.db.execute_script(os.path.join(os.getcwd(), "src", "database", "schema.sql"))

        self.alunos = AlunoRepository(self.db)
        self.cursos = CursoRepository(self.db)
        self.maquinas = MaquinaRepository(self.db)
        self.turmas = TurmaRepository(self.db)
        self.financeiro = FinanceiroRepository(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def criar_aluno(self, nome="Aluno Teste", nascimento="10/01/2010", turma_id=None, modulos_ids=None):
        aluno = Aluno(
            None,
            nome,
            "(11) 98888-7777",
            "(11) 97777-6666",
            "529.982.247-25",
            nascimento,
        )
        aluno.turma_id = turma_id
        aluno.licao_atual = 1
        aluno.modulo_atual = "Modulo 01"
        aluno.observacoes = "Observacao inicial"
        aluno.modulos_ids = modulos_ids or []
        self.alunos.add(aluno)
        return aluno

    def test_curso_modulo_aula_cronograma_e_exclusao(self):
        curso_id = self.cursos.add_curso("Curso Teste", 14, 135.0)
        modulo_id = self.cursos.add_modulo(curso_id, "Modulo Inicial", 1, permite_flexibilidade=True)
        aula_id = self.cursos.add_aula(modulo_id, "Aula 01", 1, "Introducao")

        cursos = self.cursos.get_cursos()
        modulos = self.cursos.get_modulos(curso_id)
        aulas = self.cursos.get_aulas(curso_id)

        self.assertEqual(cursos[0][1], "Curso Teste")
        self.assertEqual(modulos[0][2], "Modulo Inicial")
        self.assertEqual(aulas[0][0], aula_id)
        self.assertEqual(aulas[0][3], "Aula 01")
        self.assertEqual(aulas[0][5], "Introducao")

        self.cursos.update_modulo(modulo_id, "Modulo Editado", 2, 1, False, None)
        self.assertEqual(self.cursos.get_modulos(curso_id)[0][2], "Modulo Editado")

        self.cursos.delete_modulo(modulo_id)
        self.assertEqual(self.cursos.get_aulas(curso_id), [])
        self.assertEqual(self.cursos.get_modulos(curso_id), [])

    def test_nao_permite_cursos_com_mesmo_nome(self):
        curso_id = self.cursos.add_curso("Curso Teste", 14, 135.0)
        outro_id = self.cursos.add_curso("Curso Avancado", 14, 135.0)

        with self.assertRaises(CursoDuplicadoError):
            self.cursos.add_curso(" curso teste ", 12, 150.0)

        with self.assertRaises(CursoDuplicadoError):
            self.cursos.update_curso(outro_id, "CURSO TESTE", 10, 120.0)

        self.cursos.update_curso(curso_id, "Curso Teste", 15, 140.0)
        cursos = self.cursos.get_cursos()
        self.assertEqual(len(cursos), 2)
        self.assertEqual(next(curso for curso in cursos if curso[0] == curso_id)[2], 15)

    def test_curso_pode_ter_menos_de_14_meses_e_modulos_podem_variar(self):
        curso_id = self.cursos.add_curso("Curso Flexivel", 10, 135.0)
        modulo_rapido_id = self.cursos.add_modulo(curso_id, "Modulo Rapido", 1, carga_meses=1)
        modulo_lento_id = self.cursos.add_modulo(
            curso_id,
            "Modulo Lento",
            2,
            carga_meses=3,
            permite_flexibilidade=True,
        )

        curso = next(curso for curso in self.cursos.get_cursos() if curso[0] == curso_id)
        modulos = self.cursos.get_modulos(curso_id)

        self.assertEqual(curso[2], 10)
        self.assertEqual(next(modulo for modulo in modulos if modulo[0] == modulo_rapido_id)[4], 1)
        self.assertEqual(next(modulo for modulo in modulos if modulo[0] == modulo_lento_id)[4], 3)

        self.cursos.update_curso(curso_id, "Curso Flexivel", 8, 135.0)
        curso = next(curso for curso in self.cursos.get_cursos() if curso[0] == curso_id)
        self.assertEqual(curso[2], 8)

    def test_curso_pode_ficar_com_zero_meses_por_padrao(self):
        curso_id = self.cursos.add_curso("Curso Sem Duracao", valor_base=135.0)
        curso = next(curso for curso in self.cursos.get_cursos() if curso[0] == curso_id)
        self.assertEqual(curso[2], 0)

        self.cursos.update_curso(curso_id, "Curso Sem Duracao", 0, 140.0)
        curso = next(curso for curso in self.cursos.get_cursos() if curso[0] == curso_id)
        self.assertEqual(curso[2], 0)

    def test_duracao_do_curso_nao_depende_da_quantidade_de_modulos(self):
        curso_id = self.cursos.add_curso("Curso Independente", 6, 135.0)

        for ordem in range(1, 4):
            self.cursos.add_modulo(curso_id, f"Modulo {ordem}", ordem)

        curso = next(curso for curso in self.cursos.get_cursos() if curso[0] == curso_id)
        self.assertEqual(curso[2], 6)
        self.assertEqual(len(self.cursos.get_modulos(curso_id)), 3)

        self.cursos.gerar_cronograma_padrao()
        curso = next(curso for curso in self.cursos.get_cursos() if curso[0] == curso_id)
        self.assertEqual(curso[2], 6)
        self.assertEqual(len(self.cursos.get_modulos(curso_id)), 3)

    def test_cronograma_padrao_nao_cria_modulos_automaticos(self):
        curso_id = self.cursos.gerar_cronograma_padrao()

        curso = next(curso for curso in self.cursos.get_cursos() if curso[0] == curso_id)
        self.assertEqual(curso[2], 0)
        self.assertEqual(self.cursos.get_modulos(curso_id), [])

    def test_card_mostra_modulo_e_titulo_real_da_aula(self):
        curso_id = self.cursos.add_curso("Curso Card", 6, 135.0)
        modulo_id = self.cursos.add_modulo(curso_id, "digitacao", 1)
        self.cursos.add_aula(modulo_id, "teste com livro", 1, "Descricao")

        aluno = self.criar_aluno("Aluno Card", turma_id=None, modulos_ids=[modulo_id])
        aluno.modulo_atual = "digitacao"
        aluno.licao_atual = 1
        self.alunos.update(aluno)

        window = MainWindow.__new__(MainWindow)
        window.repo_curso = self.cursos

        self.assertEqual(window._texto_aula_card(aluno), "digitacao\nteste com livro")

    def test_aluno_crud_modulos_turma_e_exclusao_libera_maquina(self):
        curso_id = self.cursos.add_curso("Curso Aluno", 14, 135.0)
        modulo_id = self.cursos.add_modulo(curso_id, "Modulo 01", 1)
        turma_id = self.turmas.add("Turma A", "Segunda", "08:00", "Quarta", "08:00", 8)

        aluno = self.criar_aluno("Aluno CRUD", turma_id=turma_id, modulos_ids=[modulo_id])
        salvo = self.alunos.get_by_name("Aluno CRUD")

        self.assertIsNotNone(salvo.id)
        self.assertEqual(salvo.turma_id, turma_id)
        self.assertEqual(salvo.modulos_ids, [modulo_id])

        salvo.nome = "Aluno Editado"
        salvo.licao_atual = 3
        salvo.modulos_ids = []
        self.alunos.update(salvo)
        editado = self.alunos.get_by_name("Aluno Editado")

        self.assertEqual(editado.licao_atual, 3)
        self.assertEqual(editado.modulos_ids, [])

        self.maquinas.seed_maquinas(1)
        self.maquinas.salvar_alocacao("PC-01", "Aluno Editado")
        self.alunos.delete(editado.id)
        maquina = self.maquinas.get_all()[0]
        self.assertEqual(maquina.status, "VAGO")
        self.assertIsNone(maquina.ocupante)

    def test_turmas_capacidade_vagas_e_horario_atual(self):
        agora = datetime.now()
        dia = self.alunos._normalizar_dia_semana(agora.weekday()).capitalize()
        inicio = (agora - timedelta(minutes=10)).strftime("%H:%M")
        turma_id = self.turmas.add("Turma Agora", dia, inicio, "Sexta", "18:00", 8)
        self.criar_aluno("Aluno Horario", turma_id=turma_id)

        turmas = self.alunos.get_turmas_com_vagas()
        turma = next(t for t in turmas if t[0] == turma_id)
        self.assertEqual(turma[8], 8)
        self.assertEqual(turma[9], 1)

        ativos = self.alunos.get_turmas_ativas_agora()
        self.assertTrue(any(t[0] == turma_id for t in ativos))
        alunos_horario = self.alunos.get_alunos_do_horario_atual()
        self.assertTrue(any(a.nome == "Aluno Horario" for a in alunos_horario))

    def test_financeiro_registra_pagamento_e_limite_14(self):
        aluno = self.criar_aluno("Aluno Financeiro")
        self.financeiro.salvar_config(
            aluno.id,
            "10/03/2026",
            13,
            135.0,
            155.0,
            10,
            "1196321-6999",
        )

        pagas = self.financeiro.registrar_pagamento(aluno.id)
        self.assertEqual(pagas, 14)
        pagas = self.financeiro.registrar_pagamento(aluno.id)
        self.assertEqual(pagas, 14)

        config = self.financeiro.get_config(aluno.id)
        self.assertEqual(config["parcelas_pagas"], 14)
        self.assertEqual(config["valor_mensalidade"], 135.0)

    def test_presenca_e_mensagem_responsavel(self):
        aluno = self.criar_aluno("Aluno Menor", nascimento="10/01/2015")
        data_presenca = self.alunos.registrar_presenca(aluno.id, "PC-01")
        data_mensagem = self.alunos.registrar_mensagem_responsavel(
            aluno.id,
            "11977776666",
            "Presenca registrada",
        )

        self.assertRegex(data_presenca, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
        self.assertRegex(data_mensagem, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

        with self.db.connection() as conn:
            presencas = conn.execute("SELECT COUNT(*) FROM presencas WHERE aluno_id = ?", (aluno.id,)).fetchone()[0]
            mensagens = conn.execute(
                "SELECT COUNT(*) FROM mensagens_responsavel WHERE aluno_id = ?",
                (aluno.id,),
            ).fetchone()[0]

        self.assertEqual(presencas, 1)
        self.assertEqual(mensagens, 1)

    def test_maquina_alocacao_e_finalizacao(self):
        self.maquinas.seed_maquinas(2)
        self.maquinas.salvar_alocacao("PC-01", "Aluno Maquina")

        maquina = next(m for m in self.maquinas.get_all() if m.tag == "PC-01")
        self.assertEqual(maquina.status, "OCUPADO")
        self.assertEqual(maquina.ocupante, "Aluno Maquina")

        self.maquinas.finalizar_alocacao("PC-01")
        maquina = next(m for m in self.maquinas.get_all() if m.tag == "PC-01")
        self.assertEqual(maquina.status, "VAGO")
        self.assertIsNone(maquina.ocupante)

    def test_recibo_pdf_eh_gerado(self):
        aluno = self.criar_aluno("Aluno PDF")
        destino = os.path.join(self.tmp.name, "recibo.pdf")
        gerar_recibo_pagamento_pdf(
            aluno=aluno,
            turma_texto="Turma A - Segunda 08:00 + Quarta 08:00",
            data_primeiro_pagamento="10/03/2026",
            parcelas_pagas=3,
            valor_mensalidade=135.0,
            valor_atraso=155.0,
            dia_vencimento=10,
            pix="1196321-6999",
            destino=destino,
        )

        self.assertTrue(os.path.exists(destino))
        self.assertGreater(os.path.getsize(destino), 1000)


if __name__ == "__main__":
    unittest.main()
