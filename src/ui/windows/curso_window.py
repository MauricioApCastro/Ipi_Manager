from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QCheckBox,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QSplitter,
)
from PyQt5.QtCore import Qt

from src.database.repositories import CursoRepository


class CursoWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.repo = CursoRepository(db)
        self.curso_atual_id = None
        self.curso_atual = None
        self.modulo_em_edicao_id = None
        self.modulos = []

        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        titulo = QLabel("Cursos")
        titulo.setStyleSheet("color: #0f172a; font-size: 36px; font-weight: 900;")
        subtitulo = QLabel("Cronograma principal de 14 meses, com módulos flexíveis para exceções.")
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet("color: #64748b; font-size: 20px; font-weight: 600;")

        title_box.addWidget(titulo)
        title_box.addWidget(subtitulo)
        header.addLayout(title_box)
        header.addStretch()

        self.combo_cursos = QComboBox()
        self.combo_cursos.setMinimumWidth(180)
        self.combo_cursos.setMinimumHeight(38)
        self.combo_cursos.currentIndexChanged.connect(self.trocar_curso)
        self.combo_cursos.setStyleSheet(self._input_style())
        header.addWidget(self.combo_cursos)
        layout.addLayout(header)

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)

        forms_widget = QWidget()
        forms = QVBoxLayout(forms_widget)
        forms.setContentsMargins(0, 0, 0, 0)
        forms.setSpacing(8)
        forms.addWidget(self._criar_painel_curso())
        forms.addWidget(self._criar_painel_modulo())
        forms.addWidget(self._criar_painel_aula())

        tabelas_widget = QWidget()
        tabelas = QVBoxLayout(tabelas_widget)
        tabelas.setContentsMargins(0, 0, 0, 0)
        tabelas.setSpacing(8)
        tabelas.addWidget(self._criar_tabela_modulos(), 1)
        tabelas.addWidget(self._criar_tabela_aulas(), 1)

        body.addWidget(forms_widget)
        body.addWidget(tabelas_widget)
        body.setStretchFactor(0, 5)
        body.setStretchFactor(1, 7)
        body.setSizes([460, 700])
        layout.addWidget(body, 1)

    def _criar_painel_curso(self):
        painel = self._painel_base("Curso")
        layout = painel.layout()

        self.txt_curso = self._line_edit("Nome do curso")

        linha = QHBoxLayout()
        self.spin_meses = QSpinBox()
        self.spin_meses.setRange(1, 36)
        self.spin_meses.setValue(14)
        self.spin_meses.setSuffix(" meses")
        self._preparar_campo(self.spin_meses)

        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(0, 9999)
        self.spin_valor.setValue(135.00)
        self.spin_valor.setPrefix("R$ ")
        self._preparar_campo(self.spin_valor)

        linha.addWidget(self.spin_meses)
        linha.addWidget(self.spin_valor)

        botoes = QHBoxLayout()
        self.btn_salvar_curso = QPushButton("Novo curso")
        self._preparar_botao(self.btn_salvar_curso)
        self.btn_salvar_curso.clicked.connect(self.salvar_curso)
        self.btn_salvar_curso.setStyleSheet(self._primary_button_style())

        self.btn_atualizar_curso = QPushButton("Atualizar curso")
        self._preparar_botao(self.btn_atualizar_curso)
        self.btn_atualizar_curso.clicked.connect(self.atualizar_curso)
        self.btn_atualizar_curso.setStyleSheet(self._secondary_button_style())

        self.btn_excluir_curso = QPushButton("Excluir curso")
        self._preparar_botao(self.btn_excluir_curso)
        self.btn_excluir_curso.clicked.connect(self.excluir_curso)
        self.btn_excluir_curso.setStyleSheet(self._danger_button_style())

        botoes.addWidget(self.btn_salvar_curso)
        botoes.addWidget(self.btn_atualizar_curso)
        botoes.addWidget(self.btn_excluir_curso)

        self.btn_gerar = QPushButton("Gerar cronograma principal")
        self._preparar_botao(self.btn_gerar)
        self.btn_gerar.clicked.connect(self.gerar_cronograma)
        self.btn_gerar.setStyleSheet(self._secondary_button_style())

        layout.addWidget(self.txt_curso)
        layout.addLayout(linha)
        layout.addLayout(botoes)
        layout.addWidget(self.btn_gerar)
        return painel

    def _criar_painel_modulo(self):
        painel = self._painel_base("Módulo")
        layout = painel.layout()

        self.txt_modulo = self._line_edit("Nome do módulo")

        linha = QHBoxLayout()
        self.spin_ordem_modulo = QSpinBox()
        self.spin_ordem_modulo.setRange(1, 200)
        self.spin_ordem_modulo.setPrefix("Ordem ")
        self._preparar_campo(self.spin_ordem_modulo)

        self.spin_carga_modulo = QSpinBox()
        self.spin_carga_modulo.setRange(1, 14)
        self.spin_carga_modulo.setSuffix(" mês(es)")
        self._preparar_campo(self.spin_carga_modulo)

        linha.addWidget(self.spin_ordem_modulo)
        linha.addWidget(self.spin_carga_modulo)

        self.combo_pre_requisito = QComboBox()
        self._preparar_campo(self.combo_pre_requisito)

        self.check_flexivel = QCheckBox("Permitir troca de ordem em exceções")
        self.check_flexivel.setStyleSheet("color: #334155; font-size: 20px; font-weight: 700;")

        botoes = QGridLayout()
        botoes.setHorizontalSpacing(10)
        botoes.setVerticalSpacing(10)
        botoes.setRowMinimumHeight(0, 38)
        botoes.setRowMinimumHeight(1, 38)
        self.btn_add_modulo = QPushButton("Adicionar")
        self._preparar_botao(self.btn_add_modulo)
        self.btn_add_modulo.clicked.connect(self.salvar_modulo)
        self.btn_add_modulo.setStyleSheet(self._primary_button_style())

        self.btn_update_modulo = QPushButton("Atualizar")
        self._preparar_botao(self.btn_update_modulo)
        self.btn_update_modulo.clicked.connect(self.atualizar_modulo)
        self.btn_update_modulo.setStyleSheet(self._secondary_button_style())

        self.btn_limpar_modulo = QPushButton("Limpar")
        self._preparar_botao(self.btn_limpar_modulo)
        self.btn_limpar_modulo.clicked.connect(self.limpar_form_modulo)
        self.btn_limpar_modulo.setStyleSheet(self._secondary_button_style())

        self.btn_excluir_modulo = QPushButton("Excluir")
        self._preparar_botao(self.btn_excluir_modulo)
        self.btn_excluir_modulo.clicked.connect(self.excluir_modulo)
        self.btn_excluir_modulo.setStyleSheet(self._danger_button_style())

        for botao in (
            self.btn_add_modulo,
            self.btn_update_modulo,
            self.btn_excluir_modulo,
            self.btn_limpar_modulo,
        ):
            botao.setMinimumWidth(110)

        botoes.addWidget(self.btn_add_modulo, 0, 0)
        botoes.addWidget(self.btn_update_modulo, 0, 1)
        botoes.addWidget(self.btn_excluir_modulo, 1, 0)
        botoes.addWidget(self.btn_limpar_modulo, 1, 1)

        layout.addWidget(self.txt_modulo)
        layout.addLayout(linha)
        layout.addWidget(self.combo_pre_requisito)
        layout.addWidget(self.check_flexivel)
        layout.addLayout(botoes)
        return painel

    def _criar_painel_aula(self):
        painel = self._painel_base("Aula")
        layout = painel.layout()

        self.combo_modulo_aula = QComboBox()
        self._preparar_campo(self.combo_modulo_aula)

        linha = QHBoxLayout()
        self.txt_aula = self._line_edit("Título da aula")

        self.spin_ordem_aula = QSpinBox()
        self.spin_ordem_aula.setRange(1, 500)
        self.spin_ordem_aula.setPrefix("Aula ")
        self._preparar_campo(self.spin_ordem_aula)

        linha.addWidget(self.txt_aula, 2)
        linha.addWidget(self.spin_ordem_aula, 1)

        self.txt_obs_aula = self._line_edit("Observação opcional")

        self.btn_add_aula = QPushButton("Adicionar aula")
        self._preparar_botao(self.btn_add_aula)
        self.btn_add_aula.clicked.connect(self.salvar_aula)
        self.btn_add_aula.setStyleSheet(self._primary_button_style())

        layout.addWidget(self.combo_modulo_aula)
        layout.addLayout(linha)
        layout.addWidget(self.txt_obs_aula)
        layout.addWidget(self.btn_add_aula)
        return painel

    def _criar_tabela_modulos(self):
        painel = self._painel_base("Cronograma de módulos")
        layout = painel.layout()

        self.tbl_modulos = QTableWidget(0, 5)
        self.tbl_modulos.setHorizontalHeaderLabels(["Ordem", "Módulo", "Duração", "Flexível", "Pré-requisito"])
        self.tbl_modulos.itemSelectionChanged.connect(self.carregar_modulo_selecionado)
        self._preparar_tabela(self.tbl_modulos)

        layout.addWidget(self.tbl_modulos)
        return painel

    def _criar_tabela_aulas(self):
        painel = self._painel_base("Aulas do curso")
        layout = painel.layout()

        self.tbl_aulas = QTableWidget(0, 4)
        self.tbl_aulas.setHorizontalHeaderLabels(["Ordem", "Módulo", "Aula", "Observação"])
        self._preparar_tabela(self.tbl_aulas)

        layout.addWidget(self.tbl_aulas)
        return painel

    def carregar_dados(self, curso_id_preferido=None):
        cursos = self.repo.get_cursos()
        self.combo_cursos.blockSignals(True)
        self.combo_cursos.clear()

        for curso in cursos:
            self.combo_cursos.addItem(f"{curso[1]} ({curso[2]} meses)", curso[0])

        self.combo_cursos.blockSignals(False)

        if cursos:
            index = self.combo_cursos.findData(curso_id_preferido)
            self.combo_cursos.setCurrentIndex(index if index >= 0 else 0)
            self.curso_atual_id = self.combo_cursos.currentData()
        else:
            self.curso_atual_id = None
            self.curso_atual = None

        self.carregar_cronograma()

    def trocar_curso(self):
        self.curso_atual_id = self.combo_cursos.currentData()
        self.carregar_cronograma()

    def carregar_cronograma(self):
        self.modulo_em_edicao_id = None
        self.modulos = []
        self.combo_pre_requisito.clear()
        self.combo_modulo_aula.clear()
        self.combo_pre_requisito.addItem("Sem pré-requisito fixo", None)
        self.tbl_modulos.setRowCount(0)
        self.tbl_aulas.setRowCount(0)

        if not self.curso_atual_id:
            self.txt_curso.clear()
            return

        cursos = self.repo.get_cursos()
        self.curso_atual = next((curso for curso in cursos if curso[0] == self.curso_atual_id), None)
        if self.curso_atual:
            self.txt_curso.setText(self.curso_atual[1])
            self.spin_meses.setValue(self.curso_atual[2] or 14)
            self.spin_valor.setValue(float(self.curso_atual[3] or 0))

        self.modulos = self.repo.get_modulos(self.curso_atual_id)
        pre_requisitos = {modulo[0]: modulo[2] for modulo in self.modulos}

        self.tbl_modulos.blockSignals(True)
        for row, modulo in enumerate(self.modulos):
            modulo_id, _, nome, ordem, carga, flexivel, pre_id = modulo
            self.combo_pre_requisito.addItem(nome, modulo_id)
            self.combo_modulo_aula.addItem(nome, modulo_id)

            self.tbl_modulos.insertRow(row)
            self.tbl_modulos.setItem(row, 0, QTableWidgetItem(str(ordem or "")))
            self.tbl_modulos.setItem(row, 1, QTableWidgetItem(nome))
            self.tbl_modulos.setItem(row, 2, QTableWidgetItem(f"{carga or 1} mês(es)"))
            self.tbl_modulos.setItem(row, 3, QTableWidgetItem("Sim" if flexivel else "Não"))
            self.tbl_modulos.setItem(row, 4, QTableWidgetItem(pre_requisitos.get(pre_id, "-")))
        self.tbl_modulos.blockSignals(False)

        aulas = self.repo.get_aulas(self.curso_atual_id)
        for row, aula in enumerate(aulas):
            _, _, modulo_nome, titulo, ordem, observacoes = aula
            self.tbl_aulas.insertRow(row)
            self.tbl_aulas.setItem(row, 0, QTableWidgetItem(str(ordem or "")))
            self.tbl_aulas.setItem(row, 1, QTableWidgetItem(modulo_nome))
            self.tbl_aulas.setItem(row, 2, QTableWidgetItem(titulo))
            self.tbl_aulas.setItem(row, 3, QTableWidgetItem(observacoes or ""))

        self.limpar_form_modulo()
        self.spin_ordem_modulo.setValue(len(self.modulos) + 1)
        self.spin_ordem_aula.setValue(len(aulas) + 1)

    def salvar_curso(self):
        nome = self.txt_curso.text().strip()
        if not nome:
            QMessageBox.warning(self, "Curso", "Informe o nome do curso.")
            return

        curso_id = self.repo.add_curso(nome, self.spin_meses.value(), self.spin_valor.value())
        self.carregar_dados(curso_id)

    def atualizar_curso(self):
        if not self.curso_atual_id:
            QMessageBox.warning(self, "Curso", "Selecione um curso para editar.")
            return

        nome = self.txt_curso.text().strip()
        if not nome:
            QMessageBox.warning(self, "Curso", "Informe o nome do curso.")
            return

        self.repo.update_curso(self.curso_atual_id, nome, self.spin_meses.value(), self.spin_valor.value())
        self.carregar_dados(self.curso_atual_id)

    def excluir_curso(self):
        if not self.curso_atual_id:
            QMessageBox.warning(self, "Curso", "Selecione um curso para excluir.")
            return

        nome = self.txt_curso.text().strip() or "este curso"
        resposta = QMessageBox.question(
            self,
            "Excluir curso",
            f"Deseja excluir {nome}? Todos os módulos e aulas desse curso também serão removidos.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return

        self.repo.delete_curso(self.curso_atual_id)
        self.curso_atual_id = None
        self.curso_atual = None
        self.carregar_dados()

    def salvar_modulo(self):
        if not self.curso_atual_id:
            QMessageBox.warning(self, "Módulo", "Cadastre ou gere um curso antes de adicionar módulos.")
            return

        nome = self.txt_modulo.text().strip()
        if not nome:
            QMessageBox.warning(self, "Módulo", "Informe o nome do módulo.")
            return

        self.repo.add_modulo(
            self.curso_atual_id,
            nome,
            self.spin_ordem_modulo.value(),
            self.spin_carga_modulo.value(),
            self.check_flexivel.isChecked(),
            self._pre_requisito_valido(),
        )
        self.carregar_cronograma()

    def atualizar_modulo(self):
        if not self.modulo_em_edicao_id:
            QMessageBox.warning(self, "Módulo", "Selecione um módulo na tabela para editar.")
            return

        nome = self.txt_modulo.text().strip()
        if not nome:
            QMessageBox.warning(self, "Módulo", "Informe o nome do módulo.")
            return

        self.repo.update_modulo(
            self.modulo_em_edicao_id,
            nome,
            self.spin_ordem_modulo.value(),
            self.spin_carga_modulo.value(),
            self.check_flexivel.isChecked(),
            self._pre_requisito_valido(),
        )
        self.carregar_cronograma()

    def excluir_modulo(self):
        if not self.modulo_em_edicao_id:
            QMessageBox.warning(self, "Módulo", "Selecione um módulo na tabela para excluir.")
            return

        nome = self.txt_modulo.text().strip() or "este módulo"
        resposta = QMessageBox.question(
            self,
            "Excluir módulo",
            f"Deseja excluir {nome}? As aulas desse módulo também serão removidas.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return

        self.repo.delete_modulo(self.modulo_em_edicao_id)
        self.carregar_cronograma()

    def carregar_modulo_selecionado(self):
        row = self.tbl_modulos.currentRow()
        if row < 0 or row >= len(self.modulos):
            return

        modulo = self.modulos[row]
        modulo_id, _, nome, ordem, carga, flexivel, pre_id = modulo
        self.modulo_em_edicao_id = modulo_id
        self.txt_modulo.setText(nome)
        self.spin_ordem_modulo.setValue(ordem or 1)
        self.spin_carga_modulo.setValue(carga or 1)
        self.check_flexivel.setChecked(bool(flexivel))

        index = self.combo_pre_requisito.findData(pre_id)
        self.combo_pre_requisito.setCurrentIndex(index if index >= 0 else 0)

    def limpar_form_modulo(self):
        self.modulo_em_edicao_id = None
        self.txt_modulo.clear()
        self.check_flexivel.setChecked(False)
        self.combo_pre_requisito.setCurrentIndex(0 if self.combo_pre_requisito.count() else -1)

    def salvar_aula(self):
        modulo_id = self.combo_modulo_aula.currentData()
        if not modulo_id:
            QMessageBox.warning(self, "Aula", "Cadastre um módulo antes de adicionar aulas.")
            return

        titulo = self.txt_aula.text().strip()
        if not titulo:
            QMessageBox.warning(self, "Aula", "Informe o título da aula.")
            return

        self.repo.add_aula(
            modulo_id,
            titulo,
            self.spin_ordem_aula.value(),
            self.txt_obs_aula.text().strip(),
        )
        self.txt_aula.clear()
        self.txt_obs_aula.clear()
        self.carregar_cronograma()

    def gerar_cronograma(self):
        curso_id = self.repo.gerar_cronograma_padrao()
        self.carregar_dados(curso_id)
        QMessageBox.information(self, "Cronograma", "Cronograma principal de 14 meses gerado.")

    def _pre_requisito_valido(self):
        pre_id = self.combo_pre_requisito.currentData()
        if pre_id == self.modulo_em_edicao_id:
            return None
        return pre_id

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
        layout.setContentsMargins(14, 10, 14, 12)
        layout.setSpacing(7)

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
        campo.setMinimumHeight(34)
        campo.setStyleSheet(self._input_style())

    def _preparar_botao(self, botao):
        botao.setMinimumHeight(38)

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
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                padding: 7px 10px;
                font-size: 20px;
                font-weight: 600;
            }

            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
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
