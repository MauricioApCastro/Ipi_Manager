from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QLineEdit,
    QSpinBox, QDateEdit, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog,
)
from PyQt5.QtCore import Qt, QDate

from src.database.repositories import CalendarioRepository
from src.services.app_config import definir_config, obter_config


class ConfigWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.repo_calendario = CalendarioRepository(db)
        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        titulo = QLabel("Configuracoes")
        titulo.setStyleSheet("color: #0f172a; font-size: 42px; font-weight: 900;")
        layout.addWidget(titulo)

        painel_backup = self._painel_base("Backup automatico")
        backup_layout = painel_backup.layout()

        linha_backup = QHBoxLayout()
        self.txt_backup_nuvem = self._line_edit("Pasta da nuvem")
        self.btn_escolher_backup = QPushButton("Escolher pasta")
        self.btn_escolher_backup.clicked.connect(self.escolher_pasta_backup)
        self.btn_escolher_backup.setStyleSheet(self._primary_button_style())
        self.btn_salvar_backup = QPushButton("Salvar")
        self.btn_salvar_backup.clicked.connect(self.salvar_pasta_backup)
        self.btn_salvar_backup.setStyleSheet(self._primary_button_style())
        linha_backup.addWidget(self.txt_backup_nuvem, 1)
        linha_backup.addWidget(self.btn_escolher_backup)
        linha_backup.addWidget(self.btn_salvar_backup)

        self.lbl_backup_info = QLabel("Ao meio-dia, o sistema salva backup no PC e nesta pasta da nuvem.")
        self.lbl_backup_info.setWordWrap(True)
        self.lbl_backup_info.setStyleSheet("color: #64748b; font-size: 18px; font-weight: 700; border: none;")

        backup_layout.addLayout(linha_backup)
        backup_layout.addWidget(self.lbl_backup_info)
        layout.addWidget(painel_backup)

        painel = self._painel_base("Feriados, recessos e aulas canceladas")
        form = painel.layout()

        linha = QHBoxLayout()
        self.data_excecao = QDateEdit()
        self.data_excecao.setCalendarPopup(True)
        self.data_excecao.setDisplayFormat("dd/MM/yyyy")
        self.data_excecao.setDate(QDate.currentDate())
        self._preparar_campo(self.data_excecao)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["FERIADO", "RECESSO", "AULA CANCELADA"])
        self._preparar_campo(self.combo_tipo)

        self.txt_descricao = self._line_edit("Descricao")
        linha.addWidget(self.data_excecao)
        linha.addWidget(self.combo_tipo)
        linha.addWidget(self.txt_descricao, 1)

        botoes = QHBoxLayout()
        self.btn_salvar = QPushButton("Salvar data")
        self.btn_salvar.clicked.connect(self.salvar_excecao)
        self.btn_salvar.setStyleSheet(self._primary_button_style())
        self.btn_excluir = QPushButton("Excluir selecionada")
        self.btn_excluir.clicked.connect(self.excluir_excecao)
        self.btn_excluir.setStyleSheet(self._danger_button_style())
        botoes.addWidget(self.btn_salvar)
        botoes.addWidget(self.btn_excluir)

        filtro = QHBoxLayout()
        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(2020, 2100)
        self.spin_ano.setPrefix("Ano ")
        self.spin_ano.setValue(datetime.now().year)
        self.spin_ano.valueChanged.connect(self.carregar_dados)
        self._preparar_campo(self.spin_ano)
        filtro.addWidget(self.spin_ano)
        filtro.addStretch()

        self.tbl_excecoes = QTableWidget(0, 3)
        self.tbl_excecoes.setHorizontalHeaderLabels(["Data", "Tipo", "Descricao"])
        self._preparar_tabela(self.tbl_excecoes)

        form.addLayout(linha)
        form.addLayout(botoes)
        form.addLayout(filtro)
        form.addWidget(self.tbl_excecoes)
        layout.addWidget(painel, 1)

    def carregar_dados(self):
        if not hasattr(self, "tbl_excecoes"):
            return
        self.txt_backup_nuvem.setText(obter_config(self.db, "backup_nuvem_path", ""))
        excecoes = self.repo_calendario.get_excecoes_ano(self.spin_ano.value())
        self.tbl_excecoes.setRowCount(0)
        for row, (excecao_id, data, descricao, tipo) in enumerate(excecoes):
            self.tbl_excecoes.insertRow(row)
            item_data = QTableWidgetItem(self._data_para_tela(data))
            item_data.setData(Qt.UserRole, excecao_id)
            self.tbl_excecoes.setItem(row, 0, item_data)
            self.tbl_excecoes.setItem(row, 1, QTableWidgetItem(tipo or ""))
            self.tbl_excecoes.setItem(row, 2, QTableWidgetItem(descricao or ""))

    def escolher_pasta_backup(self):
        pasta = QFileDialog.getExistingDirectory(
            self,
            "Escolher pasta da nuvem para backup",
            self.txt_backup_nuvem.text().strip() or "",
        )
        if not pasta:
            return
        self.txt_backup_nuvem.setText(pasta)
        self.salvar_pasta_backup()

    def salvar_pasta_backup(self):
        definir_config(self.db, "backup_nuvem_path", self.txt_backup_nuvem.text().strip())
        QMessageBox.information(self, "Backup", "Pasta da nuvem salva.")

    def salvar_excecao(self):
        descricao = self.txt_descricao.text().strip()
        if not descricao:
            QMessageBox.warning(self, "Configuracoes", "Informe uma descricao.")
            return
        self.repo_calendario.add_excecao(
            self.data_excecao.date().toString("yyyy-MM-dd"),
            descricao,
            self.combo_tipo.currentText(),
        )
        self.txt_descricao.clear()
        self.carregar_dados()

    def excluir_excecao(self):
        itens = self.tbl_excecoes.selectedItems()
        if not itens:
            QMessageBox.warning(self, "Configuracoes", "Selecione uma data.")
            return
        excecao_id = self.tbl_excecoes.item(itens[0].row(), 0).data(Qt.UserRole)
        self.repo_calendario.delete_excecao(excecao_id)
        self.carregar_dados()

    def _data_para_tela(self, texto):
        try:
            return datetime.strptime(texto or "", "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return texto or ""

    def _painel_base(self, titulo):
        painel = QFrame()
        painel.setStyleSheet("QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; }")
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

    def _preparar_tabela(self, tabela):
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.verticalHeader().setVisible(False)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabela.setStyleSheet("QTableWidget { border: none; color: #0f172a; font-size: 18px; } QHeaderView::section { background-color: #f1f5f9; padding: 8px; font-weight: 800; }")

    def _input_style(self):
        return "QLineEdit, QDateEdit, QComboBox, QSpinBox { background-color: #f8fafc; color: #0f172a; border: 1px solid #dbe3ef; border-radius: 10px; padding: 7px 10px; font-size: 20px; font-weight: 600; }"

    def _primary_button_style(self):
        return "QPushButton { background-color: #2563eb; color: white; border: none; border-radius: 11px; padding: 10px 12px; font-size: 20px; font-weight: 800; } QPushButton:hover { background-color: #1d4ed8; }"

    def _danger_button_style(self):
        return "QPushButton { background-color: #dc2626; color: white; border: none; border-radius: 11px; padding: 10px 12px; font-size: 20px; font-weight: 800; } QPushButton:hover { background-color: #b91c1c; }"
