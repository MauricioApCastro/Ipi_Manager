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
    QApplication,
)
from PyQt5.QtCore import Qt

from src.database.repositories import CursoDuplicadoError, CursoRepository


class CursoWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.repo = CursoRepository(db)
        self.curso_atual_id = None
        self.curso_atual = None
        self.modulo_em_edicao_id = None
        self.aula_em_edicao_id = None
        self.modulos = []
        self.aulas_modulo = []
        monitor = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
        self.compacto = bool(monitor and (monitor.width() <= 1366 or monitor.height() <= 760))

        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        margem = 8 if self.compacto else 12
        layout.setContentsMargins(margem, margem, margem, margem)
        layout.setSpacing(6 if self.compacto else 10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(0)

        titulo = QLabel("Cursos")
        titulo.setStyleSheet(f"color: #0f172a; font-size: {26 if self.compacto else 30}px; font-weight: 900;")

        title_box.addWidget(titulo)
        header.addLayout(title_box)
        header.addStretch()

        self.combo_cursos = QComboBox()
        self.combo_cursos.setMinimumWidth(190 if self.compacto else 220)
        self.combo_cursos.setMinimumHeight(28 if self.compacto else 30)
        self.combo_cursos.currentIndexChanged.connect(self.trocar_curso)
        self.combo_cursos.setStyleSheet(self._input_style())
        header.addWidget(self.combo_cursos)
        layout.addLayout(header)

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)

        forms_widget = QWidget()
        forms_widget.setMinimumWidth(360 if self.compacto else 430)
        forms = QVBoxLayout(forms_widget)
        forms.setContentsMargins(0, 0, 0, 0)
        forms.setSpacing(6 if self.compacto else 10)
        forms.addWidget(self._criar_painel_curso())
        forms.addWidget(self._criar_painel_modulo())
        forms.addWidget(self._criar_painel_aula())

        tabelas_widget = QWidget()
        tabelas = QVBoxLayout(tabelas_widget)
        tabelas.setContentsMargins(0, 0, 0, 0)
        tabelas.setSpacing(8 if self.compacto else 10)
        tabelas.addWidget(self._criar_tabela_modulos(), 1)
        tabelas.addWidget(self._criar_tabela_aulas(), 1)

        body.addWidget(forms_widget)
        body.addWidget(tabelas_widget)
        body.setStretchFactor(0, 4)
        body.setStretchFactor(1, 6)
        body.setSizes([420 if self.compacto else 500, 620 if self.compacto else 720])
        layout.addWidget(body, 1)

    def _criar_painel_curso(self):
        painel = self._painel_base("Curso", "#2563eb", "#eff6ff")
        layout = painel.layout()

        self.txt_curso = self._line_edit("Nome do curso")

        linha = QHBoxLayout()
        self.spin_meses = QSpinBox()
        self.spin_meses.setRange(0, 36)
        self.spin_meses.setValue(0)
        self.spin_meses.setSuffix(" meses")
        self._preparar_campo(self.spin_meses)

        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(0, 9999)
        self.spin_valor.setSpecialValueText("")
        self.spin_valor.setValue(0)
        self.spin_valor.setPrefix("R$ ")
        self._preparar_campo(self.spin_valor)

        linha.addWidget(self.spin_meses)
        linha.addWidget(self.spin_valor)

        botoes = QHBoxLayout()
        self.btn_salvar_curso = QPushButton("Salvar")
        self._preparar_botao(self.btn_salvar_curso)
        self.btn_salvar_curso.clicked.connect(self.salvar_curso)
        self.btn_salvar_curso.setStyleSheet(self._primary_button_style())

        self.btn_atualizar_curso = QPushButton("Editar")
        self._preparar_botao(self.btn_atualizar_curso)
        self.btn_atualizar_curso.clicked.connect(self.atualizar_curso)
        self.btn_atualizar_curso.setStyleSheet(self._secondary_button_style())

        self.btn_excluir_curso = QPushButton("Excluir")
        self._preparar_botao(self.btn_excluir_curso)
        self.btn_excluir_curso.clicked.connect(self.excluir_curso)
        self.btn_excluir_curso.setStyleSheet(self._danger_button_style())

        self._adicionar_botoes_padrao(botoes, self.btn_salvar_curso, self.btn_atualizar_curso, self.btn_excluir_curso)

        layout.addWidget(self.txt_curso)
        layout.addLayout(linha)
        layout.addLayout(botoes)
        return painel

    def _criar_painel_modulo(self):
        painel = self._painel_base("Módulo", "#16a34a", "#f0fdf4")
        layout = painel.layout()

        self.txt_modulo = self._line_edit("Nome do módulo")

        linha = QHBoxLayout()
        self.spin_ordem_modulo = QSpinBox()
        self.spin_ordem_modulo.setRange(1, 200)
        self.spin_ordem_modulo.setPrefix("Ordem ")
        self._preparar_campo(self.spin_ordem_modulo)

        linha.addWidget(self.spin_ordem_modulo, 1)
        linha.addStretch(1)

        self.combo_pre_requisito = QComboBox()
        self._preparar_campo(self.combo_pre_requisito)

        self.check_flexivel = QCheckBox("Ritmo flexível para o aluno")
        self.check_flexivel.setStyleSheet("color: #334155; font-size: 16px; font-weight: 700;")

        botoes = QHBoxLayout()
        botoes.setSpacing(8)
        self.btn_add_modulo = QPushButton("Salvar")
        self._preparar_botao(self.btn_add_modulo)
        self.btn_add_modulo.clicked.connect(self.salvar_modulo)
        self.btn_add_modulo.setStyleSheet(self._primary_button_style())

        self.btn_update_modulo = QPushButton("Editar")
        self._preparar_botao(self.btn_update_modulo)
        self.btn_update_modulo.clicked.connect(self.atualizar_modulo)
        self.btn_update_modulo.setStyleSheet(self._secondary_button_style())

        self.btn_excluir_modulo = QPushButton("Excluir")
        self._preparar_botao(self.btn_excluir_modulo)
        self.btn_excluir_modulo.clicked.connect(self.excluir_modulo)
        self.btn_excluir_modulo.setStyleSheet(self._danger_button_style())

        self._adicionar_botoes_padrao(botoes, self.btn_add_modulo, self.btn_update_modulo, self.btn_excluir_modulo)

        layout.addWidget(self.txt_modulo)
        layout.addLayout(linha)
        layout.addWidget(self.combo_pre_requisito)
        layout.addWidget(self.check_flexivel)
        layout.addLayout(botoes)
        return painel

    def _criar_painel_aula(self):
        painel = self._painel_base("Aula", "#d97706", "#fffbeb")
        layout = painel.layout()

        self.combo_modulo_aula = QComboBox()
        self._preparar_campo(self.combo_modulo_aula)
        self.combo_modulo_aula.currentIndexChanged.connect(self.filtrar_aulas_por_combo)

        linha = QHBoxLayout()
        self.txt_aula = self._line_edit("Título da aula")

        self.spin_ordem_aula = QSpinBox()
        self.spin_ordem_aula.setRange(0, 500)
        self.spin_ordem_aula.setSpecialValueText("")
        self._preparar_campo(self.spin_ordem_aula)

        linha.addWidget(self.txt_aula, 2)
        linha.addWidget(self.spin_ordem_aula, 1)

        self.txt_descricao_aula = self._line_edit("Descrição da aula")

        botoes = QHBoxLayout()
        botoes.setSpacing(8)

        self.btn_add_aula = QPushButton("Salvar")
        self._preparar_botao(self.btn_add_aula)
        self.btn_add_aula.clicked.connect(self.salvar_aula)
        self.btn_add_aula.setStyleSheet(self._primary_button_style())

        self.btn_update_aula = QPushButton("Editar")
        self._preparar_botao(self.btn_update_aula)
        self.btn_update_aula.clicked.connect(self.atualizar_aula)
        self.btn_update_aula.setStyleSheet(self._secondary_button_style())

        self.btn_excluir_aula = QPushButton("Excluir")
        self._preparar_botao(self.btn_excluir_aula)
        self.btn_excluir_aula.clicked.connect(self.excluir_aula)
        self.btn_excluir_aula.setStyleSheet(self._danger_button_style())

        self._adicionar_botoes_padrao(botoes, self.btn_add_aula, self.btn_update_aula, self.btn_excluir_aula)

        layout.addWidget(self.combo_modulo_aula)
        layout.addLayout(linha)
        layout.addWidget(self.txt_descricao_aula)
        layout.addLayout(botoes)
        return painel

    def _criar_tabela_modulos(self):
        painel = self._painel_base("Cronograma de módulos")
        layout = painel.layout()

        self.tbl_modulos = QTableWidget(0, 4)
        self.tbl_modulos.setHorizontalHeaderLabels(["Ordem", "Módulo", "Flex.", "Pré-req."])
        self.tbl_modulos.itemSelectionChanged.connect(self.carregar_modulo_selecionado)
        self._preparar_tabela(self.tbl_modulos)

        layout.addWidget(self.tbl_modulos)
        return painel

    def _criar_tabela_aulas(self):
        painel = self._painel_base("Aulas do curso")
        layout = painel.layout()

        self.tbl_aulas = QTableWidget(0, 4)
        self.tbl_aulas.setHorizontalHeaderLabels(["Ordem", "Módulo", "Aula", "Descrição"])
        self.tbl_aulas.itemSelectionChanged.connect(self.carregar_aula_selecionada)
        self._preparar_tabela(self.tbl_aulas)

        layout.addWidget(self.tbl_aulas)
        return painel

    def carregar_dados(self, curso_id_preferido=None):
        cursos = self.repo.get_cursos()
        self.combo_cursos.blockSignals(True)
        self.combo_cursos.clear()
        self.combo_cursos.addItem("Selecione um curso", None)

        for curso in cursos:
            self.combo_cursos.addItem(curso[1], curso[0])

        self.combo_cursos.blockSignals(False)

        if curso_id_preferido:
            index = self.combo_cursos.findData(curso_id_preferido)
            self.combo_cursos.setCurrentIndex(index if index >= 0 else 0)
        else:
            self.combo_cursos.setCurrentIndex(0)

        self.curso_atual_id = self.combo_cursos.currentData()
        self.curso_atual = None

        self.carregar_cronograma()

    def trocar_curso(self):
        self.curso_atual_id = self.combo_cursos.currentData()
        self.carregar_cronograma()

    def carregar_cronograma(self):
        self.modulo_em_edicao_id = None
        self.aula_em_edicao_id = None
        self.modulos = []
        self.aulas_modulo = []
        self.combo_modulo_aula.blockSignals(True)
        self.combo_pre_requisito.clear()
        self.combo_modulo_aula.clear()
        self.combo_pre_requisito.addItem("Sem pré-requisito fixo", None)
        self.combo_modulo_aula.addItem("", None)
        self.tbl_modulos.setRowCount(0)
        self.tbl_aulas.setRowCount(0)

        if not self.curso_atual_id:
            self.limpar_form_curso()
            self.limpar_form_modulo()
            self.limpar_form_aula()
            self.combo_modulo_aula.blockSignals(False)
            return

        cursos = self.repo.get_cursos()
        self.curso_atual = next((curso for curso in cursos if curso[0] == self.curso_atual_id), None)
        if self.curso_atual:
            self.txt_curso.setText(self.curso_atual[1])
            self.spin_meses.setValue(int(self.curso_atual[2] or 0))
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
            self.tbl_modulos.setItem(row, 2, QTableWidgetItem("Sim" if flexivel else "Não"))
            self.tbl_modulos.setItem(row, 3, QTableWidgetItem(pre_requisitos.get(pre_id, "-")))
        self.tbl_modulos.blockSignals(False)
        self.combo_modulo_aula.blockSignals(False)

        self.limpar_form_modulo()
        self.spin_ordem_modulo.setValue(len(self.modulos) + 1)
        self.limpar_form_aula()

    def salvar_curso(self):
        nome = self.txt_curso.text().strip()
        if not nome:
            QMessageBox.warning(self, "Curso", "Informe o nome do curso.")
            return
        if self.spin_valor.value() <= 0:
            QMessageBox.warning(self, "Curso", "Informe o valor do curso.")
            return

        try:
            self.repo.add_curso(nome, self.spin_meses.value(), self.spin_valor.value())
        except CursoDuplicadoError as erro:
            QMessageBox.warning(self, "Curso", str(erro))
            return
        self.carregar_dados()

    def atualizar_curso(self):
        if not self.curso_atual_id:
            QMessageBox.warning(self, "Curso", "Selecione um curso para editar.")
            return

        nome = self.txt_curso.text().strip()
        if not nome:
            QMessageBox.warning(self, "Curso", "Informe o nome do curso.")
            return
        if self.spin_valor.value() <= 0:
            QMessageBox.warning(self, "Curso", "Informe o valor do curso.")
            return

        curso_id = self.curso_atual_id
        try:
            self.repo.update_curso(curso_id, nome, self.spin_meses.value(), self.spin_valor.value())
        except CursoDuplicadoError as erro:
            QMessageBox.warning(self, "Curso", str(erro))
            return
        self.carregar_dados(curso_id)

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
            1,
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
            1,
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
        self.check_flexivel.setChecked(bool(flexivel))

        index = self.combo_pre_requisito.findData(pre_id)
        self.combo_pre_requisito.setCurrentIndex(index if index >= 0 else 0)
        index_aula = self.combo_modulo_aula.findData(modulo_id)
        self.combo_modulo_aula.setCurrentIndex(index_aula if index_aula >= 0 else 0)
        self.carregar_aulas_modulo(modulo_id)

    def filtrar_aulas_por_combo(self):
        self.limpar_campos_aula()
        self.carregar_aulas_modulo(self.combo_modulo_aula.currentData())

    def carregar_aulas_modulo(self, modulo_id):
        self.aula_em_edicao_id = None
        self.aulas_modulo = []
        self.tbl_aulas.setRowCount(0)
        if not modulo_id:
            return

        self.aulas_modulo = self.repo.get_aulas_modulo(modulo_id)
        for row, aula in enumerate(self.aulas_modulo):
            _, _, modulo_nome, titulo, ordem, descricao = aula
            self.tbl_aulas.insertRow(row)
            self.tbl_aulas.setItem(row, 0, QTableWidgetItem(str(ordem or "")))
            self.tbl_aulas.setItem(row, 1, QTableWidgetItem(modulo_nome))
            self.tbl_aulas.setItem(row, 2, QTableWidgetItem(titulo))
            self.tbl_aulas.setItem(row, 3, QTableWidgetItem(descricao or ""))

    def carregar_aula_selecionada(self):
        row = self.tbl_aulas.currentRow()
        if row < 0 or row >= len(self.aulas_modulo):
            return

        aula_id, modulo_id, _, titulo, ordem, descricao = self.aulas_modulo[row]
        self.aula_em_edicao_id = aula_id
        index = self.combo_modulo_aula.findData(modulo_id)
        self.combo_modulo_aula.blockSignals(True)
        self.combo_modulo_aula.setCurrentIndex(index if index >= 0 else 0)
        self.combo_modulo_aula.blockSignals(False)
        self.txt_aula.setText(titulo)
        self.spin_ordem_aula.setValue(ordem or 0)
        self.txt_descricao_aula.setText(descricao or "")

    def limpar_form_modulo(self):
        self.modulo_em_edicao_id = None
        self.txt_modulo.clear()
        self.check_flexivel.setChecked(False)
        self.combo_pre_requisito.setCurrentIndex(0 if self.combo_pre_requisito.count() else -1)

    def limpar_form_curso(self):
        self.txt_curso.clear()
        self.spin_meses.setValue(0)
        self.spin_valor.setValue(0)

    def limpar_form_aula(self):
        self.combo_modulo_aula.setCurrentIndex(0 if self.combo_modulo_aula.count() else -1)
        self.limpar_campos_aula()

    def limpar_campos_aula(self):
        self.aula_em_edicao_id = None
        self.txt_aula.clear()
        self.txt_descricao_aula.clear()
        self.spin_ordem_aula.setValue(0)

    def salvar_aula(self):
        modulo_id = self.combo_modulo_aula.currentData()
        if not modulo_id:
            QMessageBox.warning(self, "Aula", "Cadastre um módulo antes de adicionar aulas.")
            return

        titulo = self.txt_aula.text().strip()
        if not titulo:
            QMessageBox.warning(self, "Aula", "Informe o título da aula.")
            return
        if self.spin_ordem_aula.value() <= 0:
            QMessageBox.warning(self, "Aula", "Informe o número da aula.")
            return

        self.repo.add_aula(
            modulo_id,
            titulo,
            self.spin_ordem_aula.value(),
            self.txt_descricao_aula.text().strip(),
        )
        self.limpar_campos_aula()
        self.carregar_aulas_modulo(modulo_id)

    def atualizar_aula(self):
        if not self.aula_em_edicao_id:
            QMessageBox.warning(self, "Aula", "Selecione uma aula na tabela para editar.")
            return

        modulo_id = self.combo_modulo_aula.currentData()
        if not modulo_id:
            QMessageBox.warning(self, "Aula", "Selecione um módulo para a aula.")
            return

        titulo = self.txt_aula.text().strip()
        if not titulo:
            QMessageBox.warning(self, "Aula", "Informe o título da aula.")
            return
        if self.spin_ordem_aula.value() <= 0:
            QMessageBox.warning(self, "Aula", "Informe o número da aula.")
            return

        self.repo.update_aula(
            self.aula_em_edicao_id,
            modulo_id,
            titulo,
            self.spin_ordem_aula.value(),
            self.txt_descricao_aula.text().strip(),
        )
        self.limpar_campos_aula()
        self.carregar_aulas_modulo(modulo_id)

    def excluir_aula(self):
        if not self.aula_em_edicao_id:
            QMessageBox.warning(self, "Aula", "Selecione uma aula na tabela para excluir.")
            return

        titulo = self.txt_aula.text().strip() or "esta aula"
        resposta = QMessageBox.question(
            self,
            "Excluir aula",
            f"Deseja excluir {titulo}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return

        modulo_id = self.combo_modulo_aula.currentData()
        self.repo.delete_aula(self.aula_em_edicao_id)
        self.limpar_campos_aula()
        self.carregar_aulas_modulo(modulo_id)

    def _pre_requisito_valido(self):
        pre_id = self.combo_pre_requisito.currentData()
        if pre_id == self.modulo_em_edicao_id:
            return None
        return pre_id

    def _adicionar_botoes_padrao(self, layout, botao_salvar, botao_editar, botao_excluir):
        for botao in (botao_salvar, botao_editar, botao_excluir):
            botao.setMinimumWidth(0)
            layout.addWidget(botao, 1)

    def _painel_base(self, titulo, cor="#64748b", fundo_titulo="#f8fafc"):
        painel = QFrame()
        painel.setObjectName("painelBase")
        painel.setMinimumWidth(240)
        painel.setStyleSheet(f"""
            QFrame#painelBase {{
                background-color: white;
                border: 1px solid {cor};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(painel)
        margem_h = 10 if self.compacto else 14
        margem_v = 6 if self.compacto else 12
        layout.setContentsMargins(margem_h, margem_v, margem_h, margem_v)
        layout.setSpacing(4 if self.compacto else 8)

        label = QLabel(titulo)
        fonte = 17 if self.compacto else 19
        padding = "4px 8px" if self.compacto else "7px 10px"
        label.setStyleSheet(f"""
            color: {cor};
            background-color: {fundo_titulo};
            border: none;
            border-left: 5px solid {cor};
            border-radius: 8px;
            padding: {padding};
            font-size: {fonte}px;
            font-weight: 900;
        """)
        layout.addWidget(label)

        divisor = QFrame()
        divisor.setFrameShape(QFrame.HLine)
        divisor.setStyleSheet(f"border: none; border-top: 1px solid {cor};")
        layout.addWidget(divisor)
        return painel

    def _line_edit(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        self._preparar_campo(edit)
        return edit

    def _preparar_campo(self, campo):
        campo.setMinimumHeight(26 if self.compacto else 32)
        campo.setStyleSheet(self._input_style())

    def _preparar_botao(self, botao):
        botao.setMinimumHeight(28 if self.compacto else 34)

    def _preparar_tabela(self, tabela):
        tabela.setAlternatingRowColors(True)
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.verticalHeader().setVisible(False)
        tabela.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tabela.horizontalHeader().setStretchLastSection(False)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        tabela.horizontalHeader().setMinimumSectionSize(58 if self.compacto else 72)
        larguras = (68, 210, 74, 145) if self.compacto else (80, 260, 90, 180)
        for coluna, largura in enumerate(larguras):
            tabela.setColumnWidth(coluna, largura)
        fonte = 15 if self.compacto else 17
        padding_header = "6px 8px" if self.compacto else "8px 10px"
        tabela.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                gridline-color: #e2e8f0;
                color: #0f172a;
                font-size: {fonte}px;
                alternate-background-color: #f8fafc;
            }}

            QHeaderView::section {{
                background-color: #f1f5f9;
                color: #475569;
                border: none;
                padding: {padding_header};
                font-weight: 800;
                font-size: {fonte}px;
            }}
        """)

    def _input_style(self):
        fonte = 16 if self.compacto else 17
        padding = "3px 8px" if self.compacto else "5px 10px"
        return f"""
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                padding: {padding};
                font-size: {fonte}px;
                font-weight: 600;
            }}

            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                background-color: white;
                border-color: #3b82f6;
            }}
        """

    def _primary_button_style(self):
        fonte = 16 if self.compacto else 17
        padding = "5px 8px" if self.compacto else "7px 10px"
        return f"""
            QPushButton {{
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 11px;
                padding: {padding};
                font-size: {fonte}px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                background-color: #1d4ed8;
            }}
        """

    def _secondary_button_style(self):
        fonte = 16 if self.compacto else 17
        padding = "5px 8px" if self.compacto else "7px 10px"
        return f"""
            QPushButton {{
                background-color: white;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 11px;
                padding: {padding};
                font-size: {fonte}px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                border-color: #bfdbfe;
                color: #1d4ed8;
            }}
        """

    def _danger_button_style(self):
        fonte = 16 if self.compacto else 17
        padding = "5px 8px" if self.compacto else "7px 10px"
        return f"""
            QPushButton {{
                background-color: #fff1f2;
                color: #be123c;
                border: 1px solid #fecdd3;
                border-radius: 11px;
                padding: {padding};
                font-size: {fonte}px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                background-color: #ffe4e6;
                border-color: #fda4af;
            }}
        """
