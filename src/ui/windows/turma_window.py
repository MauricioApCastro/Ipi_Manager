from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QSplitter,
)
from PyQt5.QtCore import Qt

from src.database.repositories import TurmaRepository


class TurmaWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.repo = TurmaRepository(db)
        self.turmas = []
        self.turma_em_edicao_id = None

        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        titulo = QLabel("Turmas")
        titulo.setStyleSheet("color: #0f172a; font-size: 42px; font-weight: 900;")
        subtitulo = QLabel("Forme turmas com 2 aulas semanais de 1 hora e vagas conforme os 8 PCs.")
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet("color: #64748b; font-size: 20px; font-weight: 600;")

        title_box.addWidget(titulo)
        title_box.addWidget(subtitulo)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)
        body.addWidget(self._criar_painel_form())
        body.addWidget(self._criar_painel_tabela())
        body.setStretchFactor(0, 4)
        body.setStretchFactor(1, 8)
        body.setSizes([340, 760])
        layout.addWidget(body, 1)

    def _criar_painel_form(self):
        painel = self._painel_base("Dados da turma")
        layout = painel.layout()

        self.txt_nome = self._line_edit("Nome da turma")

        linha1 = QHBoxLayout()
        self.combo_dia1 = self._combo_dias()
        self.txt_horario1 = self._line_edit("08:00")
        self.txt_horario1.setInputMask("00:00;_")
        linha1.addWidget(self.combo_dia1)
        linha1.addWidget(self.txt_horario1)

        linha2 = QHBoxLayout()
        self.combo_dia2 = self._combo_dias()
        self.txt_horario2 = self._line_edit("08:00")
        self.txt_horario2.setInputMask("00:00;_")
        linha2.addWidget(self.combo_dia2)
        linha2.addWidget(self.txt_horario2)

        self.spin_capacidade = QSpinBox()
        self.spin_capacidade.setRange(1, 99)
        self.spin_capacidade.setValue(8)
        self.spin_capacidade.setPrefix("Capacidade ")
        self.spin_capacidade.setSuffix(" PCs")
        self._preparar_campo(self.spin_capacidade)

        regra = QLabel("Regra fixa: 2 aulas por semana, 60 minutos cada.")
        regra.setStyleSheet("color: #64748b; font-size: 20px; font-weight: 700;")

        botoes = QGridLayout()
        botoes.setHorizontalSpacing(10)
        botoes.setVerticalSpacing(10)

        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_adicionar.clicked.connect(self.salvar_turma)
        self.btn_adicionar.setStyleSheet(self._primary_button_style())

        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.atualizar_turma)
        self.btn_atualizar.setStyleSheet(self._secondary_button_style())

        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_turma)
        self.btn_excluir.setStyleSheet(self._danger_button_style())

        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.clicked.connect(self.limpar_form)
        self.btn_limpar.setStyleSheet(self._secondary_button_style())

        for botao in (self.btn_adicionar, self.btn_atualizar, self.btn_excluir, self.btn_limpar):
            botao.setMinimumHeight(38)

        botoes.addWidget(self.btn_adicionar, 0, 0)
        botoes.addWidget(self.btn_atualizar, 0, 1)
        botoes.addWidget(self.btn_excluir, 1, 0)
        botoes.addWidget(self.btn_limpar, 1, 1)

        layout.addWidget(self.txt_nome)
        layout.addLayout(linha1)
        layout.addLayout(linha2)
        layout.addWidget(self.spin_capacidade)
        layout.addWidget(regra)
        layout.addLayout(botoes)
        layout.addStretch()
        return painel

    def _criar_painel_tabela(self):
        painel = self._painel_base("Turmas formadas")
        layout = painel.layout()

        self.tbl_turmas = QTableWidget(0, 7)
        self.tbl_turmas.setHorizontalHeaderLabels([
            "Turma",
            "1ª aula",
            "2ª aula",
            "Regra",
            "Capacidade",
            "Ocupadas",
            "Livres",
        ])
        self.tbl_turmas.itemSelectionChanged.connect(self.carregar_turma_selecionada)
        self._preparar_tabela(self.tbl_turmas)
        layout.addWidget(self.tbl_turmas)
        return painel

    def carregar_dados(self):
        self.turmas = self.repo.get_all()
        self.tbl_turmas.blockSignals(True)
        self.tbl_turmas.setRowCount(0)

        for row, turma in enumerate(self.turmas):
            (
                _turma_id,
                nome,
                dia1,
                horario1,
                dia2,
                horario2,
                duracao,
                aulas_semana,
                capacidade,
                ocupadas,
            ) = turma
            livres = max((capacidade or 8) - (ocupadas or 0), 0)

            self.tbl_turmas.insertRow(row)
            self.tbl_turmas.setItem(row, 0, QTableWidgetItem(nome or ""))
            self.tbl_turmas.setItem(row, 1, QTableWidgetItem(f"{dia1} {horario1}"))
            self.tbl_turmas.setItem(row, 2, QTableWidgetItem(f"{dia2} {horario2}"))
            self.tbl_turmas.setItem(row, 3, QTableWidgetItem(f"{aulas_semana}x {duracao}min"))
            self.tbl_turmas.setItem(row, 4, QTableWidgetItem(str(capacidade or 8)))
            self.tbl_turmas.setItem(row, 5, QTableWidgetItem(str(ocupadas or 0)))
            self.tbl_turmas.setItem(row, 6, QTableWidgetItem(str(livres)))

        self.tbl_turmas.blockSignals(False)

    def salvar_turma(self):
        dados = self._dados_form()
        if not dados:
            return
        self.repo.add(*dados)
        self.carregar_dados()
        self.limpar_form()

    def atualizar_turma(self):
        if not self.turma_em_edicao_id:
            QMessageBox.warning(self, "Turma", "Selecione uma turma na tabela para editar.")
            return

        dados = self._dados_form()
        if not dados:
            return
        self.repo.update(self.turma_em_edicao_id, *dados)
        self.carregar_dados()
        self.limpar_form()

    def excluir_turma(self):
        if not self.turma_em_edicao_id:
            QMessageBox.warning(self, "Turma", "Selecione uma turma na tabela para excluir.")
            return

        resposta = QMessageBox.question(
            self,
            "Excluir turma",
            "Deseja excluir esta turma? Os alunos vinculados ficarão sem turma definida.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return

        self.repo.delete(self.turma_em_edicao_id)
        self.carregar_dados()
        self.limpar_form()

    def carregar_turma_selecionada(self):
        row = self.tbl_turmas.currentRow()
        if row < 0 or row >= len(self.turmas):
            return

        turma = self.turmas[row]
        (
            turma_id,
            nome,
            dia1,
            horario1,
            dia2,
            horario2,
            _duracao,
            _aulas_semana,
            capacidade,
            _ocupadas,
        ) = turma

        self.turma_em_edicao_id = turma_id
        self.txt_nome.setText(nome or "")
        self.combo_dia1.setCurrentText(dia1 or "Segunda")
        self.txt_horario1.setText(horario1 or "")
        self.combo_dia2.setCurrentText(dia2 or "Quarta")
        self.txt_horario2.setText(horario2 or "")
        self.spin_capacidade.setValue(capacidade or 8)

    def limpar_form(self):
        self.turma_em_edicao_id = None
        self.txt_nome.clear()
        self.combo_dia1.setCurrentIndex(0)
        self.txt_horario1.clear()
        self.combo_dia2.setCurrentIndex(2)
        self.txt_horario2.clear()
        self.spin_capacidade.setValue(8)

    def _dados_form(self):
        nome = self.txt_nome.text().strip()
        horario1 = self.txt_horario1.text().strip()
        horario2 = self.txt_horario2.text().strip()

        if not nome:
            QMessageBox.warning(self, "Turma", "Informe o nome da turma.")
            return None
        if "_" in horario1 or "_" in horario2:
            QMessageBox.warning(self, "Horários", "Informe os dois horários no formato HH:MM.")
            return None

        return (
            nome,
            self.combo_dia1.currentText(),
            horario1,
            self.combo_dia2.currentText(),
            horario2,
            self.spin_capacidade.value(),
        )

    def _combo_dias(self):
        combo = QComboBox()
        combo.addItems(["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado"])
        self._preparar_campo(combo)
        return combo

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
        campo.setMinimumHeight(36)
        campo.setStyleSheet(self._input_style())

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
                font-size: 20px;
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
            QLineEdit, QSpinBox, QComboBox {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                padding: 7px 10px;
                font-size: 20px;
                font-weight: 600;
            }

            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                background-color: white;
                border-color: #3b82f6;
            }
        """

    def _primary_button_style(self):
        return """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 11px;
                padding: 10px 12px;
                font-size: 20px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """

    def _secondary_button_style(self):
        return """
            QPushButton {
                background-color: white;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 11px;
                padding: 10px 12px;
                font-size: 20px;
                font-weight: 800;
            }

            QPushButton:hover {
                border-color: #bfdbfe;
                color: #1d4ed8;
            }
        """

    def _danger_button_style(self):
        return """
            QPushButton {
                background-color: #fff1f2;
                color: #be123c;
                border: 1px solid #fecdd3;
                border-radius: 11px;
                padding: 10px 12px;
                font-size: 20px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: #ffe4e6;
                border-color: #fda4af;
            }
        """
