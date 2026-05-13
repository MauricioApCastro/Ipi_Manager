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
    QCheckBox,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from src.database.repositories import AlunoRepository, CursoRepository
from src.models.aluno import Aluno


class AlunoWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.repo = AlunoRepository(db)
        self.repo_curso = CursoRepository(db)
        self.repo.seed_turmas_padrao()
        self.alunos = []
        self.modulo_checks = []
        self.aluno_em_edicao_id = None

        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        titulo = QLabel("Alunos")
        titulo.setStyleSheet("color: #0f172a; font-size: 32px; font-weight: 900;")
        subtitulo = QLabel("Cada turma tem 2 aulas semanais de 1 hora, com 8 PCs por horário.")
        subtitulo.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 600;")
        title_box.addWidget(titulo)
        title_box.addWidget(subtitulo)
        header.addLayout(title_box)
        header.addStretch()

        self.txt_busca = QLineEdit()
        self.txt_busca.setPlaceholderText("Buscar aluno")
        self.txt_busca.setMinimumWidth(280)
        self.txt_busca.textChanged.connect(self.filtrar_tabela)
        self._preparar_campo(self.txt_busca)
        header.addWidget(self.txt_busca)
        layout.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(14)
        body.addWidget(self._criar_painel_dados(), 4)
        body.addWidget(self._criar_painel_academico(), 4)
        body.addWidget(self._criar_painel_tabela(), 7)
        layout.addLayout(body, 1)

    def _criar_painel_dados(self):
        painel = self._painel_base("Dados do aluno")
        layout = painel.layout()

        self.txt_nome = self._line_edit("Nome completo")

        self.txt_cpf = self._line_edit("CPF")
        self.txt_cpf.setInputMask("000.000.000-00;_")

        self.txt_nascimento = self._line_edit("Nascimento")
        self.txt_nascimento.setInputMask("00/00/0000;_")

        self.txt_whatsapp = self._line_edit("WhatsApp aluno")
        self.txt_whatsapp.setInputMask("(00) 00000-0000;_")

        self.txt_whatsapp_resp = self._line_edit("WhatsApp responsável")
        self.txt_whatsapp_resp.setInputMask("(00) 00000-0000;_")

        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Observações rápidas")
        self.txt_obs.setFixedHeight(58)
        self.txt_obs.setStyleSheet(self._text_edit_style())

        botoes = QGridLayout()
        botoes.setHorizontalSpacing(10)
        botoes.setVerticalSpacing(10)

        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_adicionar.clicked.connect(self.salvar_aluno)
        self.btn_adicionar.setStyleSheet(self._primary_button_style())

        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.atualizar_aluno)
        self.btn_atualizar.setStyleSheet(self._secondary_button_style())

        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_aluno)
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
        layout.addWidget(self.txt_cpf)
        layout.addWidget(self.txt_nascimento)
        layout.addWidget(self.txt_whatsapp)
        layout.addWidget(self.txt_whatsapp_resp)
        layout.addWidget(self.txt_obs)
        layout.addLayout(botoes)
        layout.addStretch()
        return painel

    def _criar_painel_academico(self):
        painel = self._painel_base("Turma e módulos")
        layout = painel.layout()

        self.combo_turma = QComboBox()
        self._preparar_campo(self.combo_turma)

        self.spin_licao = QSpinBox()
        self.spin_licao.setRange(1, 500)
        self.spin_licao.setPrefix("Aula ")
        self._preparar_campo(self.spin_licao)

        self.chk_todos_modulos = QCheckBox("Selecionar todos os módulos")
        self.chk_todos_modulos.stateChanged.connect(self.marcar_todos_modulos)
        self.chk_todos_modulos.setStyleSheet(self._checkbox_style())

        self.modulos_grid = QGridLayout()
        self.modulos_grid.setHorizontalSpacing(10)
        self.modulos_grid.setVerticalSpacing(6)

        layout.addWidget(self.combo_turma)
        layout.addWidget(self.spin_licao)
        layout.addWidget(self.chk_todos_modulos)
        layout.addLayout(self.modulos_grid)
        layout.addStretch()
        return painel

    def _criar_painel_tabela(self):
        painel = self._painel_base("Lista de alunos")
        layout = painel.layout()

        self.tbl_alunos = QTableWidget(0, 8)
        self.tbl_alunos.setHorizontalHeaderLabels([
            "Nome",
            "CPF",
            "Nascimento",
            "WhatsApp",
            "Responsável",
            "Turma",
            "Módulos",
            "Aula",
        ])
        self.tbl_alunos.itemSelectionChanged.connect(self.carregar_aluno_selecionado)
        self._preparar_tabela(self.tbl_alunos)

        layout.addWidget(self.tbl_alunos)
        return painel

    def carregar_dados(self):
        self._carregar_turmas()
        self._carregar_modulos()
        self.alunos = self.repo.get_all()
        self.preencher_tabela(self.alunos)
        self.limpar_form()

    def _carregar_turmas(self):
        atual = self.combo_turma.currentData() if hasattr(self, "combo_turma") else None
        self.combo_turma.clear()
        self.combo_turma.addItem("Sem turma definida", None)
        for turma in self.repo.get_turmas_com_vagas():
            (
                turma_id,
                nome,
                dia,
                horario,
                segundo_dia,
                segundo_horario,
                duracao,
                aulas_semana,
                capacidade,
                ocupadas,
            ) = turma
            vagas = max((capacidade or 8) - (ocupadas or 0), 0)
            texto = (
                f"{nome} - {dia} {horario} + {segundo_dia} {segundo_horario} "
                f"({aulas_semana or 2}x {duracao or 60}min, {vagas}/{capacidade or 8} vagas)"
            )
            self.combo_turma.addItem(texto, turma_id)
        index = self.combo_turma.findData(atual)
        if index >= 0:
            self.combo_turma.setCurrentIndex(index)

    def _carregar_modulos(self):
        self.modulo_checks = []
        self._limpar_layout(self.modulos_grid)

        modulos = self.repo_curso.get_all_modulos()
        if not modulos:
            label = QLabel("Gere ou cadastre módulos na tela Cursos.")
            label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 700;")
            self.modulos_grid.addWidget(label, 0, 0)
            return

        for idx, modulo in enumerate(modulos):
            chk = QCheckBox(modulo[2])
            chk.setProperty("modulo_id", modulo[0])
            chk.setStyleSheet(self._checkbox_style())
            self.modulo_checks.append(chk)
            self.modulos_grid.addWidget(chk, idx // 2, idx % 2)

    def preencher_tabela(self, alunos):
        self.tbl_alunos.blockSignals(True)
        self.tbl_alunos.setRowCount(0)

        for row, aluno in enumerate(alunos):
            turma_txt = self._texto_turma(aluno.turma_id)
            self.tbl_alunos.insertRow(row)
            self.tbl_alunos.setItem(row, 0, QTableWidgetItem(aluno.nome or ""))
            self.tbl_alunos.setItem(row, 1, QTableWidgetItem(aluno.cpf or ""))
            self.tbl_alunos.setItem(row, 2, QTableWidgetItem(aluno.nascimento or ""))
            self.tbl_alunos.setItem(row, 3, QTableWidgetItem(aluno.whatsapp_aluno or ""))
            self.tbl_alunos.setItem(row, 4, QTableWidgetItem(aluno.whatsapp_resp or ""))
            self.tbl_alunos.setItem(row, 5, QTableWidgetItem(turma_txt))
            self.tbl_alunos.setItem(row, 6, QTableWidgetItem(aluno.modulo_atual or ""))
            self.tbl_alunos.setItem(row, 7, QTableWidgetItem(str(aluno.licao_atual or 1)))

        self.tbl_alunos.blockSignals(False)

    def filtrar_tabela(self):
        termo = self.txt_busca.text().strip().lower()
        if not termo:
            self.preencher_tabela(self.alunos)
            return

        filtrados = [
            aluno for aluno in self.alunos
            if termo in (aluno.nome or "").lower()
            or termo in (aluno.cpf or "").lower()
            or termo in (aluno.modulo_atual or "").lower()
        ]
        self.preencher_tabela(filtrados)

    def carregar_aluno_selecionado(self):
        row = self.tbl_alunos.currentRow()
        if row < 0:
            return

        nome = self.tbl_alunos.item(row, 0).text()
        aluno = self.repo.get_by_name(nome)
        if not aluno:
            return

        self.aluno_em_edicao_id = aluno.id
        self.txt_nome.setText(aluno.nome or "")
        self.txt_cpf.setText(aluno.cpf or "")
        self.txt_nascimento.setText(aluno.nascimento or "")
        self.txt_whatsapp.setText(aluno.whatsapp_aluno or "")
        self.txt_whatsapp_resp.setText(aluno.whatsapp_resp or "")
        self.spin_licao.setValue(aluno.licao_atual or 1)
        self.txt_obs.setPlainText(aluno.observacoes or "")

        index = self.combo_turma.findData(aluno.turma_id)
        self.combo_turma.setCurrentIndex(index if index >= 0 else 0)

        selecionados = set(aluno.modulos_ids or [])
        for chk in self.modulo_checks:
            chk.setChecked(chk.property("modulo_id") in selecionados)

    def salvar_aluno(self):
        aluno = self._aluno_from_form()
        if not aluno:
            return
        self.repo.add(aluno)
        self.carregar_dados()

    def atualizar_aluno(self):
        if not self.aluno_em_edicao_id:
            QMessageBox.warning(self, "Aluno", "Selecione um aluno na tabela para editar.")
            return

        aluno = self._aluno_from_form()
        if not aluno:
            return
        aluno.id = self.aluno_em_edicao_id
        self.repo.update(aluno)
        self.carregar_dados()

    def excluir_aluno(self):
        if not self.aluno_em_edicao_id:
            QMessageBox.warning(self, "Aluno", "Selecione um aluno na tabela para excluir.")
            return

        nome = self.txt_nome.text().strip() or "este aluno"
        resposta = QMessageBox.question(
            self,
            "Excluir aluno",
            f"Deseja excluir {nome}? Se ele estiver em uma máquina, a máquina será liberada.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return

        self.repo.delete(self.aluno_em_edicao_id)
        self.carregar_dados()

    def limpar_form(self):
        self.aluno_em_edicao_id = None
        self.txt_nome.clear()
        self.txt_cpf.clear()
        self.txt_nascimento.clear()
        self.txt_whatsapp.clear()
        self.txt_whatsapp_resp.clear()
        self.spin_licao.setValue(1)
        self.txt_obs.clear()
        self.combo_turma.setCurrentIndex(0)
        self.chk_todos_modulos.setChecked(False)
        for chk in self.modulo_checks:
            chk.setChecked(False)

    def marcar_todos_modulos(self):
        marcado = self.chk_todos_modulos.isChecked()
        for chk in self.modulo_checks:
            chk.setChecked(marcado)

    def _aluno_from_form(self):
        nome = self.txt_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aluno", "Informe o nome do aluno.")
            return None

        cpf = self.txt_cpf.text().strip()
        if not self._cpf_valido(cpf):
            QMessageBox.warning(self, "CPF", "Informe um CPF válido.")
            return None

        nascimento = self.txt_nascimento.text().strip()
        if "_" in nascimento or len(nascimento) != 10:
            QMessageBox.warning(self, "Nascimento", "Informe a data de nascimento no formato dd/mm/aaaa.")
            return None

        modulos_ids = [
            chk.property("modulo_id")
            for chk in self.modulo_checks
            if chk.isChecked()
        ]
        if not modulos_ids:
            QMessageBox.warning(self, "Módulos", "Selecione pelo menos um módulo.")
            return None

        nomes_modulos = [
            chk.text()
            for chk in self.modulo_checks
            if chk.isChecked()
        ]

        aluno = Aluno(
            None,
            nome,
            self.txt_whatsapp.text().strip(),
            self.txt_whatsapp_resp.text().strip(),
            cpf,
            nascimento,
        )
        aluno.licao_atual = self.spin_licao.value()
        aluno.modulo_atual = ", ".join(nomes_modulos)
        aluno.modulos_ids = modulos_ids
        aluno.turma_id = self.combo_turma.currentData()
        aluno.observacoes = self.txt_obs.toPlainText().strip()
        return aluno

    def _cpf_valido(self, cpf):
        numeros = [int(char) for char in cpf if char.isdigit()]
        if len(numeros) != 11 or len(set(numeros)) == 1:
            return False

        soma = sum(numeros[i] * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        digito1 = 0 if digito1 == 10 else digito1

        soma = sum(numeros[i] * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        digito2 = 0 if digito2 == 10 else digito2

        return numeros[9] == digito1 and numeros[10] == digito2

    def _texto_turma(self, turma_id):
        if not turma_id:
            return "-"
        index = self.combo_turma.findData(turma_id)
        if index < 0:
            return "-"
        return self.combo_turma.itemText(index).split(" (")[0]

    def _limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _painel_base(self, titulo):
        painel = QFrame()
        painel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(9)

        label = QLabel(titulo)
        label.setStyleSheet("color: #0f172a; font-size: 15px; font-weight: 900; border: none;")
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
                font-size: 13px;
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
                font-size: 13px;
                font-weight: 600;
            }

            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                background-color: white;
                border-color: #3b82f6;
            }
        """

    def _checkbox_style(self):
        return "color: #334155; font-size: 13px; font-weight: 700;"

    def _text_edit_style(self):
        return """
            QTextEdit {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                padding: 8px 10px;
                font-size: 13px;
                font-weight: 600;
            }

            QTextEdit:focus {
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
                font-size: 13px;
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
                font-size: 13px;
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
                font-size: 13px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: #ffe4e6;
                border-color: #fda4af;
            }
        """
