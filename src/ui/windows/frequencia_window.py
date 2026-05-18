from datetime import date, datetime, timedelta
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QDateEdit,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, QDate

from src.database.repositories import AlunoRepository, CalendarioRepository, CursoRepository, ReposicaoRepository
from src.services.diploma_service import gerar_diploma_pdf


class FrequenciaWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.repo_aluno = AlunoRepository(db)
        self.repo_curso = CursoRepository(db)
        self.repo_calendario = CalendarioRepository(db)
        self.repo_reposicao = ReposicaoRepository(db)
        self.alunos = []
        self.alunos_filtrados = []
        self.aluno_selecionado_id = None
        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        header = QHBoxLayout()
        titulo = QLabel("Frequência")
        titulo.setStyleSheet("color: #0f172a; font-size: 42px; font-weight: 900;")
        header.addWidget(titulo)
        header.addStretch()

        layout.addLayout(header)

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)
        body.addWidget(self._criar_painel_aluno())
        body.addWidget(self._criar_painel_acompanhamento())
        body.setStretchFactor(0, 4)
        body.setStretchFactor(1, 8)
        body.setSizes([360, 780])
        layout.addWidget(body, 1)

    def _criar_painel_aluno(self):
        painel = self._painel_base("Aluno")
        layout = painel.layout()

        self.txt_busca = self._line_edit("Buscar pelas iniciais")
        self.txt_busca.textChanged.connect(self.filtrar_alunos)

        self.lista_alunos = QListWidget()
        self.lista_alunos.itemClicked.connect(self.selecionar_aluno_lista)
        self._preparar_lista(self.lista_alunos)

        self.lbl_resumo = QLabel("")
        self.lbl_resumo.setWordWrap(True)
        self.lbl_resumo.setStyleSheet("""
            color: #0f172a;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px;
            font-size: 18px;
            font-weight: 700;
        """)

        self.lbl_status_diploma = QLabel("")
        self.lbl_status_diploma.setWordWrap(True)
        self.lbl_status_diploma.setStyleSheet("""
            color: #166534;
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 10px;
            font-size: 18px;
            font-weight: 800;
        """)

        self.btn_diploma = QPushButton("Gerar diploma")
        self.btn_diploma.clicked.connect(self.gerar_diploma)
        self.btn_diploma.setMinimumHeight(42)
        self.btn_diploma.setStyleSheet(self._primary_button_style())

        linha_reposicao = QHBoxLayout()
        self.data_reposicao = QDateEdit()
        self.data_reposicao.setCalendarPopup(True)
        self.data_reposicao.setDisplayFormat("dd/MM/yyyy")
        self.data_reposicao.setDate(QDate.currentDate())
        self._preparar_campo(self.data_reposicao)

        self.btn_reposicao = QPushButton("Agendar reposicao")
        self.btn_reposicao.clicked.connect(self.agendar_reposicao)
        self.btn_reposicao.setMinimumHeight(42)
        self.btn_reposicao.setStyleSheet(self._secondary_button_style())
        linha_reposicao.addWidget(self.data_reposicao)
        linha_reposicao.addWidget(self.btn_reposicao)

        layout.addWidget(self.txt_busca)
        layout.addWidget(self.lista_alunos)
        layout.addWidget(self.lbl_resumo)
        layout.addWidget(self.lbl_status_diploma)
        layout.addWidget(self.btn_diploma)
        layout.addLayout(linha_reposicao)
        layout.addStretch()
        return painel

    def _criar_painel_acompanhamento(self):
        painel = self._painel_base("Frequência e aulas")
        layout = painel.layout()

        cards = QHBoxLayout()
        self.card_presencas = self._card_numero("Presenças", "0")
        self.card_aulas = self._card_numero("Aulas concluídas", "0")
        self.card_progresso = self._card_numero("Progresso", "0%")
        cards.addWidget(self.card_presencas)
        cards.addWidget(self.card_aulas)
        cards.addWidget(self.card_progresso)

        tabelas = QSplitter(Qt.Vertical)
        tabelas.setChildrenCollapsible(False)

        self.tbl_presencas = QTableWidget(0, 3)
        self.tbl_presencas.setHorizontalHeaderLabels(["Data", "Máquina", "Status"])
        self._preparar_tabela(self.tbl_presencas)

        self.tbl_aulas = QTableWidget(0, 4)
        self.tbl_aulas.setHorizontalHeaderLabels(["Módulo", "Aula", "Ordem", "Status"])
        self._preparar_tabela(self.tbl_aulas)

        tabelas.addWidget(self.tbl_presencas)
        tabelas.addWidget(self.tbl_aulas)
        tabelas.setSizes([260, 360])

        layout.addLayout(cards)
        layout.addWidget(tabelas, 1)
        return painel

    def carregar_dados(self):
        self.alunos = self.repo_aluno.get_all()
        self.alunos_filtrados = []
        self.aluno_selecionado_id = None
        self._popular_lista_alunos()
        self.carregar_aluno_atual()

    def filtrar_alunos(self):
        termo = self.txt_busca.text().strip().lower()
        self.aluno_selecionado_id = None
        if not termo:
            self.alunos_filtrados = []
        else:
            self.alunos_filtrados = [
                aluno for aluno in self.alunos
                if (aluno.nome or "").strip().lower().startswith(termo)
            ]
        self._popular_lista_alunos()
        self.carregar_aluno_atual()

    def _popular_lista_alunos(self):
        self.lista_alunos.blockSignals(True)
        self.lista_alunos.clear()
        for aluno in self.alunos_filtrados:
            item = QListWidgetItem(aluno.nome or "")
            item.setData(Qt.UserRole, aluno.id)
            self.lista_alunos.addItem(item)
            if aluno.id == self.aluno_selecionado_id:
                self.lista_alunos.setCurrentItem(item)
        self.lista_alunos.blockSignals(False)

    def aluno_atual(self):
        aluno_id = self.aluno_selecionado_id
        if not aluno_id:
            return None
        return next((aluno for aluno in self.alunos if aluno.id == aluno_id), None)

    def selecionar_aluno_lista(self, item):
        aluno_id = item.data(Qt.UserRole)
        if not aluno_id:
            return
        self.aluno_selecionado_id = aluno_id
        self.carregar_aluno_atual()

    def carregar_aluno_atual(self):
        aluno = self.aluno_atual()
        if not aluno:
            self._limpar_visualizacao()
            return

        presencas = self._presencas_aluno(aluno.id)
        aulas = self._aulas_do_aluno(aluno)
        concluidas, total = self._totais_aulas(aluno, aulas)
        percentual = int((concluidas / total) * 100) if total else 0
        status = "Curso concluído" if self._curso_concluido(aluno) else "Em andamento"

        self.card_presencas.findChild(QLabel, "valor").setText(str(len(presencas)))
        self.card_aulas.findChild(QLabel, "valor").setText(f"{concluidas}/{total}")
        self.card_progresso.findChild(QLabel, "valor").setText(f"{percentual}%")
        self.lbl_resumo.setText(
            f"Aluno: {aluno.nome}\n"
            f"CPF: {aluno.cpf or '-'}\n"
            f"Status: {status}\n"
            f"Módulo atual: {aluno.modulo_atual or '-'}"
        )
        self.lbl_status_diploma.setText(
            "Pronto para gerar diploma." if self._curso_concluido(aluno)
            else "Diploma disponível quando o curso estiver concluído."
        )
        self.btn_diploma.setEnabled(self._curso_concluido(aluno))

        self._preencher_presencas(self._frequencia_aluno(aluno, presencas))
        self._preencher_aulas(aluno, aulas)

    def agendar_reposicao(self):
        aluno = self.aluno_atual()
        if not aluno:
            QMessageBox.warning(self, "Reposicao", "Selecione um aluno.")
            return

        itens = self.tbl_presencas.selectedItems()
        if not itens:
            QMessageBox.warning(self, "Reposicao", "Selecione uma falta na tabela.")
            return

        row = itens[0].row()
        status = self.tbl_presencas.item(row, 2).text()
        if not status.startswith("Falta"):
            QMessageBox.warning(self, "Reposicao", "Selecione uma linha marcada como falta.")
            return

        data_falta = self.tbl_presencas.item(row, 0).data(Qt.UserRole)
        data_reposicao = self.data_reposicao.date().toString("yyyy-MM-dd")
        self.repo_reposicao.agendar(aluno.id, data_falta, data_reposicao, "Reposicao agendada pela frequencia")
        self.carregar_aluno_atual()
        QMessageBox.information(self, "Reposicao", "Reposicao agendada.")

    def gerar_diploma(self):
        aluno = self.aluno_atual()
        if not aluno:
            QMessageBox.warning(self, "Diploma", "Selecione um aluno.")
            return
        if not self._curso_concluido(aluno):
            QMessageBox.warning(self, "Diploma", "O diploma só pode ser gerado após concluir o curso.")
            return

        aulas = self._aulas_do_aluno(aluno)
        concluidas, _total = self._totais_aulas(aluno, aulas)
        presencas = self._presencas_aluno(aluno.id)
        nome_limpo = "".join(char for char in aluno.nome if char.isalnum() or char in (" ", "_")).strip()
        destino_padrao = Path("recibos") / f"DIPLOMA_{nome_limpo.replace(' ', '_')}.pdf"
        destino, _ = QFileDialog.getSaveFileName(self, "Salvar diploma", str(destino_padrao), "PDF (*.pdf)")
        if not destino:
            return

        arquivo = gerar_diploma_pdf(
            aluno=aluno,
            curso_nome="Curso Completo IPI",
            total_aulas=concluidas,
            total_presencas=len(presencas),
            destino=destino,
        )
        QMessageBox.information(self, "Diploma", f"Diploma gerado:\n{arquivo}")

    def _presencas_aluno(self, aluno_id):
        with self.db.connection() as conn:
            return conn.execute(
                """
                SELECT data_hora, maquina_tag, observacao
                FROM presencas
                WHERE aluno_id = ?
                ORDER BY data_hora DESC
                """,
                (aluno_id,),
            ).fetchall()

    def _frequencia_aluno(self, aluno, presencas):
        reposicoes_por_falta = {
            row[1]: row
            for row in self.repo_reposicao.get_aluno(aluno.id)
        }
        presencas_por_dia = {}
        for data_hora, maquina, _obs in presencas:
            data = self._data_presenca(data_hora)
            if not data:
                continue
            atual = presencas_por_dia.get(data)
            if not atual or (data_hora or "") > (atual[0] or ""):
                presencas_por_dia[data] = (data_hora, maquina)

        aulas_programadas = self._aulas_programadas_aluno(aluno)
        if not aulas_programadas or not presencas_por_dia:
            return [
                (data_hora, maquina, "Presente")
                for data_hora, maquina, _obs in presencas
            ]

        inicio = min(presencas_por_dia)
        hoje = datetime.now().date()
        linhas = []
        dia = hoje
        while dia >= inicio:
            if self._tem_aula_passada_no_dia(dia, aulas_programadas):
                if dia in presencas_por_dia:
                    data_hora, maquina = presencas_por_dia[dia]
                    linhas.append((data_hora, maquina, "Presente"))
                else:
                    data_falta = dia.strftime("%Y-%m-%d")
                    reposicao = reposicoes_por_falta.get(data_falta)
                    status = "Falta"
                    if reposicao:
                        status = "Falta - reposicao " + self._data_para_tela(reposicao[2])
                        if reposicao[3] == "CONCLUIDA":
                            status = "Falta - reposicao concluida"
                    linhas.append((data_falta, "-", status))
            dia -= timedelta(days=1)

        dias_listados = {self._data_presenca(data_hora) for data_hora, _maquina, _status in linhas}
        for data_hora, maquina, _obs in presencas:
            data = self._data_presenca(data_hora)
            if data and data not in dias_listados:
                linhas.append((data_hora, maquina, "Presente"))

        return sorted(linhas, key=lambda item: item[0] or "", reverse=True)

    def _aulas_programadas_aluno(self, aluno):
        if not aluno.turma_id:
            return []

        for turma in self.repo_aluno.get_turmas_com_vagas():
            (
                turma_id,
                _nome,
                dia1,
                _horario1,
                dia2,
                _horario2,
                _duracao,
                _aulas_semana,
                _capacidade,
                _ocupadas,
            ) = turma
            if turma_id == aluno.turma_id:
                aulas = []
                for dia, horario in ((dia1, _horario1), (dia2, _horario2)):
                    indice = self._indice_dia_semana(dia)
                    if indice is not None:
                        aulas.append((indice, horario, _duracao))
                return aulas
        return []

    def _tem_aula_passada_no_dia(self, dia, aulas_programadas):
        if self._eh_feriado(dia):
            return False

        for indice, horario, duracao in aulas_programadas:
            if dia.weekday() != indice:
                continue
            if dia < datetime.now().date():
                return True
            try:
                hora, minuto = [int(parte) for parte in (horario or "").split(":")[:2]]
            except ValueError:
                return True
            fim = datetime.combine(dia, datetime.min.time()).replace(hour=hora, minute=minuto)
            fim += timedelta(minutes=duracao or 60)
            if datetime.now() >= fim:
                return True
        return False

    def _eh_feriado(self, dia):
        return dia in self._feriados_ano(dia.year) or dia.strftime("%Y-%m-%d") in self.repo_calendario.datas_excecao_ano(dia.year)

    def _feriados_ano(self, ano):
        pascoa = self._domingo_pascoa(ano)
        return {
            date(ano, 1, 1),
            pascoa - timedelta(days=48),
            pascoa - timedelta(days=47),
            pascoa - timedelta(days=2),
            date(ano, 4, 21),
            date(ano, 5, 1),
            pascoa + timedelta(days=60),
            date(ano, 9, 7),
            date(ano, 10, 12),
            date(ano, 11, 2),
            date(ano, 11, 15),
            date(ano, 11, 20),
            date(ano, 12, 25),
        }

    def _domingo_pascoa(self, ano):
        a = ano % 19
        b = ano // 100
        c = ano % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        mes = (h + l - 7 * m + 114) // 31
        dia = ((h + l - 7 * m + 114) % 31) + 1
        return date(ano, mes, dia)

    def _indice_dia_semana(self, dia):
        normalizado = (dia or "").strip().lower()
        normalizado = (
            normalizado
            .replace("á", "a")
            .replace("ã", "a")
            .replace("é", "e")
            .replace("ç", "c")
        )
        dias = {
            "segunda": 0,
            "terca": 1,
            "terça": 1,
            "quarta": 2,
            "quinta": 3,
            "sexta": 4,
            "sabado": 5,
            "sábado": 5,
            "domingo": 6,
        }
        return dias.get(normalizado)

    def _data_presenca(self, data_hora):
        for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(data_hora or "", formato).date()
            except ValueError:
                continue
        return None

    def _data_para_tela(self, texto):
        try:
            return datetime.strptime(texto or "", "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return texto or ""

    def _aulas_do_aluno(self, aluno):
        modulos_ids = aluno.modulos_ids or []
        if not modulos_ids:
            return []
        placeholders = ",".join("?" for _ in modulos_ids)
        with self.db.connection() as conn:
            return conn.execute(
                f"""
                SELECT modulos.id, modulos.nome, COALESCE(modulos.ordem, 0),
                       aulas.titulo, COALESCE(aulas.ordem, 0)
                FROM modulos
                LEFT JOIN aulas ON aulas.id_modulo = modulos.id
                WHERE modulos.id IN ({placeholders})
                ORDER BY COALESCE(modulos.ordem, 0), COALESCE(aulas.ordem, 0), aulas.id
                """,
                modulos_ids,
            ).fetchall()

    def _totais_aulas(self, aluno, aulas):
        total = sum(1 for aula in aulas if aula[3])
        if self._curso_concluido(aluno):
            return total, total

        concluidas = 0
        modulo_atual = (aluno.modulo_atual or "").split(",")[0].strip().lower()
        licao_atual = max((aluno.licao_atual or 1) - 1, 0)
        ordem_modulo_atual = next(
            (
                ordem_modulo
                for _modulo_id, modulo_nome, ordem_modulo, titulo, _ordem_aula in aulas
                if titulo and (modulo_nome or "").strip().lower() == modulo_atual
            ),
            None,
        )
        for _modulo_id, modulo_nome, ordem_modulo, titulo, ordem_aula in aulas:
            if not titulo:
                continue
            nome = (modulo_nome or "").strip().lower()
            if modulo_atual and nome == modulo_atual:
                if (ordem_aula or 0) <= licao_atual:
                    concluidas += 1
            elif ordem_modulo_atual is not None and (ordem_modulo or 0) < ordem_modulo_atual:
                concluidas += 1
        return min(concluidas, total), total

    def _preencher_presencas(self, presencas):
        self.tbl_presencas.setRowCount(0)
        for row, (data_hora, maquina, status) in enumerate(presencas):
            self.tbl_presencas.insertRow(row)
            item_data = QTableWidgetItem(self._formatar_data(data_hora))
            data = self._data_presenca(data_hora)
            item_data.setData(Qt.UserRole, data.strftime("%Y-%m-%d") if data else data_hora)
            self.tbl_presencas.setItem(row, 0, item_data)
            self.tbl_presencas.setItem(row, 1, QTableWidgetItem(maquina or "-"))
            self.tbl_presencas.setItem(row, 2, QTableWidgetItem(status or ""))

    def _preencher_aulas(self, aluno, aulas):
        concluidas, _total = self._totais_aulas(aluno, aulas)
        self.tbl_aulas.setRowCount(0)
        numero_aula = 0
        for _modulo_id, modulo, _ordem_modulo, titulo, ordem in aulas:
            if not titulo:
                continue
            numero_aula += 1
            self.tbl_aulas.insertRow(self.tbl_aulas.rowCount())
            row = self.tbl_aulas.rowCount() - 1
            status = "Concluída" if numero_aula <= concluidas else "Pendente"
            self.tbl_aulas.setItem(row, 0, QTableWidgetItem(modulo or ""))
            self.tbl_aulas.setItem(row, 1, QTableWidgetItem(titulo or ""))
            self.tbl_aulas.setItem(row, 2, QTableWidgetItem(str(ordem or "")))
            self.tbl_aulas.setItem(row, 3, QTableWidgetItem(status))

    def _limpar_visualizacao(self):
        self.card_presencas.findChild(QLabel, "valor").setText("0")
        self.card_aulas.findChild(QLabel, "valor").setText("0")
        self.card_progresso.findChild(QLabel, "valor").setText("0%")
        self.lbl_resumo.setText("Cadastre ou selecione um aluno.")
        self.lbl_status_diploma.setText("")
        self.btn_diploma.setEnabled(False)
        self.tbl_presencas.setRowCount(0)
        self.tbl_aulas.setRowCount(0)

    def _curso_concluido(self, aluno):
        return (aluno.modulo_atual or "").strip().lower() == "curso concluído"

    def _formatar_data(self, data_hora):
        for formato, saida in (
            ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"),
            ("%Y-%m-%d", "%d/%m/%Y"),
        ):
            try:
                return datetime.strptime(data_hora, formato).strftime(saida)
            except ValueError:
                continue
        return data_hora or ""

    def _card_numero(self, titulo, valor):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        label = QLabel(titulo)
        label.setStyleSheet("color: #64748b; font-size: 16px; font-weight: 800; border: none;")
        numero = QLabel(valor)
        numero.setObjectName("valor")
        numero.setStyleSheet("color: #0f172a; font-size: 30px; font-weight: 900; border: none;")
        layout.addWidget(label)
        layout.addWidget(numero)
        return card

    def _painel_base(self, titulo):
        painel = QFrame()
        painel.setMinimumWidth(240)
        painel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)
        label = QLabel(titulo)
        label.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: 900; border: none;")
        layout.addWidget(label)
        return painel

    def _line_edit(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        self._preparar_campo(edit)
        return edit

    def _preparar_campo(self, campo):
        campo.setMinimumHeight(38)
        campo.setStyleSheet(self._input_style())

    def _preparar_lista(self, lista):
        lista.setMinimumHeight(130)
        lista.setStyleSheet("""
            QListWidget {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                font-size: 20px;
                font-weight: 600;
                outline: none;
            }

            QListWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid #e2e8f0;
            }

            QListWidget::item:selected {
                background-color: #ccfbf1;
                color: #134e4a;
            }
        """)

    def _preparar_tabela(self, tabela):
        tabela.setAlternatingRowColors(True)
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.verticalHeader().setVisible(False)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabela.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #e2e8f0;
                color: #0f172a;
                font-size: 17px;
                alternate-background-color: #f8fafc;
            }

            QHeaderView::section {
                background-color: #f1f5f9;
                color: #475569;
                border: none;
                padding: 8px;
                font-weight: 800;
            }
        """)

    def _input_style(self):
        return """
            QLineEdit, QDateEdit {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                padding: 7px 10px;
                font-size: 20px;
                font-weight: 600;
            }
        """

    def _secondary_button_style(self):
        return """
            QPushButton {
                background-color: #e2e8f0;
                color: #0f172a;
                border: none;
                border-radius: 11px;
                padding: 10px 12px;
                font-size: 20px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: #cbd5e1;
            }
        """

    def _primary_button_style(self):
        return """
            QPushButton {
                background-color: #0f766e;
                color: white;
                border: none;
                border-radius: 11px;
                padding: 10px 12px;
                font-size: 20px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: #115e59;
            }
        """
