import csv
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox, QFileDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
)
from PyQt5.QtCore import Qt, QDate

from src.database.repositories import CaixaRepository


class CaixaWindow(QWidget):
    CATEGORIAS_ENTRADA = ["Matricula", "Mensalidade", "Croche", "Tarot", "Filhos", "Outros"]
    CATEGORIAS_SAIDA = ["Aluguel", "Energia", "Internet", "Material", "Manutencao", "Retirada", "Outros"]
    STATUS = [("Previsto", "PREVISTO"), ("Recebido/Pago", "RECEBIDO")]

    def __init__(self, db):
        super().__init__()
        self.repo = CaixaRepository(db)
        self.entrada_selecionada_id = None
        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        titulo = QLabel("Caixa")
        titulo.setStyleSheet("color: #0f172a; font-size: 42px; font-weight: 900;")
        subtitulo = QLabel("Controle entradas, saidas e saldo do mes.")
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet("color: #64748b; font-size: 20px; font-weight: 600;")
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)
        body.addWidget(self._criar_painel_lancamento())
        body.addWidget(self._criar_painel_mes())
        body.setStretchFactor(0, 4)
        body.setStretchFactor(1, 8)
        body.setSizes([420, 780])
        layout.addWidget(body, 1)

    def _criar_painel_lancamento(self):
        painel = self._painel_base("Movimento")
        layout = painel.layout()

        self.data_entrada = QDateEdit()
        self.data_entrada.setCalendarPopup(True)
        self.data_entrada.setDisplayFormat("dd/MM/yyyy")
        self.data_entrada.setDate(QDate.currentDate())
        self._preparar_campo(self.data_entrada)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Entrada", "ENTRADA")
        self.combo_tipo.addItem("Saida", "SAIDA")
        self.combo_tipo.currentIndexChanged.connect(self.atualizar_tipo_movimento)
        self._preparar_campo(self.combo_tipo)

        self.txt_descricao = self._line_edit("Descricao")

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(self.CATEGORIAS_ENTRADA)
        self.combo_categoria.currentIndexChanged.connect(self.limpar_campos_ao_trocar_categoria)
        self._preparar_campo(self.combo_categoria)

        self.combo_status = QComboBox()
        for texto, valor in self.STATUS:
            self.combo_status.addItem(texto, valor)
        self._preparar_campo(self.combo_status)

        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(0, 999999)
        self.spin_valor.setPrefix("R$ ")
        self.spin_valor.setDecimals(2)
        self._preparar_campo(self.spin_valor)

        self.txt_observacoes = self._line_edit("Observacoes")

        botoes = QGridLayout()
        botoes.setHorizontalSpacing(10)
        botoes.setVerticalSpacing(10)

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_entrada)
        self.btn_salvar.setStyleSheet(self._primary_button_style())

        self.btn_recebido = QPushButton("Marcar recebido")
        self.btn_recebido.clicked.connect(self.marcar_recebido)
        self.btn_recebido.setStyleSheet(self._success_button_style())

        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_entrada)
        self.btn_excluir.setStyleSheet(self._danger_button_style())

        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.clicked.connect(self.limpar_form)
        self.btn_limpar.setStyleSheet(self._secondary_button_style())

        for botao in (self.btn_salvar, self.btn_recebido, self.btn_excluir, self.btn_limpar):
            botao.setMinimumHeight(42)

        botoes.addWidget(self.btn_salvar, 0, 0)
        botoes.addWidget(self.btn_recebido, 0, 1)
        botoes.addWidget(self.btn_excluir, 1, 0)
        botoes.addWidget(self.btn_limpar, 1, 1)

        layout.addWidget(self.data_entrada)
        layout.addWidget(self.combo_tipo)
        layout.addWidget(self.txt_descricao)
        layout.addWidget(self.combo_categoria)
        layout.addWidget(self.combo_status)
        layout.addWidget(self.spin_valor)
        layout.addWidget(self.txt_observacoes)
        layout.addLayout(botoes)
        layout.addStretch()
        return painel

    def _criar_painel_mes(self):
        painel = self._painel_base("Movimentos do mes")
        layout = painel.layout()

        filtros = QHBoxLayout()
        self.spin_mes = QSpinBox()
        self.spin_mes.setRange(1, 12)
        self.spin_mes.setPrefix("Mes ")
        self.spin_mes.setValue(datetime.now().month)
        self.spin_mes.valueChanged.connect(self.carregar_dados)
        self._preparar_campo(self.spin_mes)

        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(2020, 2100)
        self.spin_ano.setPrefix("Ano ")
        self.spin_ano.setValue(datetime.now().year)
        self.spin_ano.valueChanged.connect(self.carregar_dados)
        self._preparar_campo(self.spin_ano)

        self.combo_filtro_tipo = QComboBox()
        self.combo_filtro_tipo.addItem("Entradas e saidas", None)
        self.combo_filtro_tipo.addItem("Entradas", "ENTRADA")
        self.combo_filtro_tipo.addItem("Saidas", "SAIDA")
        self.combo_filtro_tipo.currentIndexChanged.connect(self.carregar_dados)
        self._preparar_campo(self.combo_filtro_tipo)

        self.combo_filtro_categoria = QComboBox()
        self.combo_filtro_categoria.addItem("Todos os tipos", None)
        for categoria in sorted(set(self.CATEGORIAS_ENTRADA + self.CATEGORIAS_SAIDA)):
            self.combo_filtro_categoria.addItem(categoria, categoria)
        self.combo_filtro_categoria.currentIndexChanged.connect(self.carregar_dados)
        self._preparar_campo(self.combo_filtro_categoria)

        self.btn_exportar = QPushButton("Exportar CSV")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        self.btn_exportar.setStyleSheet(self._secondary_button_style())
        self.btn_exportar.setMinimumHeight(38)

        filtros.addWidget(self.spin_mes)
        filtros.addWidget(self.spin_ano)
        filtros.addWidget(self.combo_filtro_tipo)
        filtros.addWidget(self.combo_filtro_categoria)
        filtros.addWidget(self.btn_exportar)

        cards = QHBoxLayout()
        self.card_previsto = self._card_total("Entradas", "R$ 0,00")
        self.card_recebido = self._card_total("Recebido", "R$ 0,00")
        self.card_saidas = self._card_total("Saidas", "R$ 0,00")
        self.card_saldo = self._card_total("Saldo", "R$ 0,00")
        cards.addWidget(self.card_previsto)
        cards.addWidget(self.card_recebido)
        cards.addWidget(self.card_saidas)
        cards.addWidget(self.card_saldo)

        self.tbl_entradas = QTableWidget(0, 7)
        self.tbl_entradas.setHorizontalHeaderLabels(["Data", "Tipo", "Descricao", "Categoria", "Valor", "Status", "Obs."])
        self.tbl_entradas.itemSelectionChanged.connect(self.carregar_entrada_selecionada)
        self._preparar_tabela(self.tbl_entradas)

        layout.addLayout(filtros)
        layout.addLayout(cards)
        layout.addWidget(self.tbl_entradas, 1)
        return painel

    def carregar_dados(self):
        if not hasattr(self, "tbl_entradas"):
            return

        entradas = self.repo.get_entradas_mes(self.spin_ano.value(), self.spin_mes.value())
        tipo_filtro = self.combo_filtro_tipo.currentData()
        if tipo_filtro:
            entradas = [entrada for entrada in entradas if entrada[7] == tipo_filtro]
        categoria_filtro = self.combo_filtro_categoria.currentData()
        if categoria_filtro:
            entradas = [entrada for entrada in entradas if entrada[3] == categoria_filtro]

        self.tbl_entradas.blockSignals(True)
        self.tbl_entradas.setRowCount(0)
        for row, entrada in enumerate(entradas):
            entrada_id, data, descricao, categoria, valor, status, observacoes, tipo = entrada
            self.tbl_entradas.insertRow(row)
            item_data = QTableWidgetItem(self._data_para_tela(data))
            item_data.setData(Qt.UserRole, entrada_id)
            self.tbl_entradas.setItem(row, 0, item_data)
            self.tbl_entradas.setItem(row, 1, QTableWidgetItem(self._texto_tipo(tipo)))
            self.tbl_entradas.setItem(row, 2, QTableWidgetItem(descricao or ""))
            self.tbl_entradas.setItem(row, 3, QTableWidgetItem(categoria or ""))
            self.tbl_entradas.setItem(row, 4, QTableWidgetItem(self._formatar_moeda(valor)))
            self.tbl_entradas.setItem(row, 5, QTableWidgetItem(self._texto_status(status, tipo)))
            self.tbl_entradas.setItem(row, 6, QTableWidgetItem(observacoes or ""))
        self.tbl_entradas.blockSignals(False)
        self._atualizar_totais(entradas)

    def salvar_entrada(self):
        dados = self._dados_form()
        if not dados:
            return
        if self.entrada_selecionada_id:
            self.repo.update_entrada(self.entrada_selecionada_id, *dados)
        else:
            self.repo.add_entrada(*dados)
        self.limpar_form()
        self.carregar_dados()

    def marcar_recebido(self):
        self.combo_status.setCurrentIndex(self.combo_status.findData("RECEBIDO"))
        if self.entrada_selecionada_id:
            self.salvar_entrada()

    def excluir_entrada(self):
        if not self.entrada_selecionada_id:
            QMessageBox.warning(self, "Caixa", "Selecione um movimento para excluir.")
            return
        resposta = QMessageBox.question(self, "Caixa", "Deseja excluir este movimento?", QMessageBox.Yes | QMessageBox.No)
        if resposta != QMessageBox.Yes:
            return
        self.repo.delete_entrada(self.entrada_selecionada_id)
        self.limpar_form()
        self.carregar_dados()

    def carregar_entrada_selecionada(self):
        itens = self.tbl_entradas.selectedItems()
        if not itens:
            return
        row = itens[0].row()
        entrada_id = self.tbl_entradas.item(row, 0).data(Qt.UserRole)
        entradas = self.repo.get_entradas_mes(self.spin_ano.value(), self.spin_mes.value())
        entrada = next((item for item in entradas if item[0] == entrada_id), None)
        if not entrada:
            return

        self.entrada_selecionada_id = entrada[0]
        self.data_entrada.setDate(self._data_qdate(entrada[1]))
        self.combo_tipo.blockSignals(True)
        self.combo_tipo.setCurrentIndex(self.combo_tipo.findData(entrada[7] or "ENTRADA"))
        self.combo_tipo.blockSignals(False)
        self._recarregar_categorias(entrada[7] or "ENTRADA", entrada[3])
        self.txt_descricao.setText(entrada[2] or "")
        self.spin_valor.setValue(entrada[4] or 0)
        index_status = self.combo_status.findData(entrada[5] or "PREVISTO")
        self.combo_status.setCurrentIndex(index_status if index_status >= 0 else 0)
        self.txt_observacoes.setText(entrada[6] or "")
        self.btn_recebido.setText("Marcar pago" if entrada[7] == "SAIDA" else "Marcar recebido")

    def limpar_form(self):
        self.entrada_selecionada_id = None
        self.data_entrada.setDate(QDate.currentDate())
        self.combo_tipo.setCurrentIndex(0)
        self._recarregar_categorias("ENTRADA")
        self.txt_descricao.clear()
        self.combo_status.setCurrentIndex(0)
        self.spin_valor.setValue(0)
        self.txt_observacoes.clear()
        self.tbl_entradas.clearSelection()
        self.btn_recebido.setText("Marcar recebido")

    def limpar_campos_ao_trocar_categoria(self):
        categoria = self.combo_categoria.currentText()
        self.entrada_selecionada_id = None
        self.data_entrada.setDate(QDate.currentDate())
        self.txt_descricao.clear()
        self.combo_status.setCurrentIndex(0)
        self.spin_valor.setValue(0)
        self.txt_observacoes.clear()
        self.tbl_entradas.clearSelection()
        self.combo_categoria.setCurrentText(categoria)

    def atualizar_tipo_movimento(self):
        tipo = self.combo_tipo.currentData()
        self._recarregar_categorias(tipo)
        self.limpar_campos_ao_trocar_categoria()
        self.btn_recebido.setText("Marcar pago" if tipo == "SAIDA" else "Marcar recebido")

    def _recarregar_categorias(self, tipo, categoria_atual=None):
        categorias = self.CATEGORIAS_SAIDA if tipo == "SAIDA" else self.CATEGORIAS_ENTRADA
        self.combo_categoria.blockSignals(True)
        self.combo_categoria.clear()
        self.combo_categoria.addItems(categorias)
        if categoria_atual and categoria_atual in categorias:
            self.combo_categoria.setCurrentText(categoria_atual)
        self.combo_categoria.blockSignals(False)

    def _dados_form(self):
        descricao = self.txt_descricao.text().strip()
        if not descricao:
            QMessageBox.warning(self, "Caixa", "Informe uma descricao.")
            return None
        valor = self.spin_valor.value()
        if valor <= 0:
            QMessageBox.warning(self, "Caixa", "Informe um valor maior que zero.")
            return None
        return (
            self.data_entrada.date().toString("yyyy-MM-dd"),
            descricao,
            self.combo_categoria.currentText(),
            valor,
            self.combo_status.currentData(),
            self.txt_observacoes.text().strip(),
            self.combo_tipo.currentData(),
        )

    def _atualizar_totais(self, entradas):
        entradas_total = sum(row[4] or 0 for row in entradas if row[7] == "ENTRADA")
        recebido = sum(row[4] or 0 for row in entradas if row[7] == "ENTRADA" and row[5] == "RECEBIDO")
        saidas = sum(row[4] or 0 for row in entradas if row[7] == "SAIDA" and row[5] == "RECEBIDO")
        saldo = recebido - saidas
        self.card_previsto.findChild(QLabel, "valor").setText(self._formatar_moeda(entradas_total))
        self.card_recebido.findChild(QLabel, "valor").setText(self._formatar_moeda(recebido))
        self.card_saidas.findChild(QLabel, "valor").setText(self._formatar_moeda(saidas))
        self.card_saldo.findChild(QLabel, "valor").setText(self._formatar_moeda(saldo))

    def exportar_csv(self):
        destino, _ = QFileDialog.getSaveFileName(
            self, "Exportar caixa", f"caixa_{self.spin_ano.value()}_{self.spin_mes.value():02d}.csv", "CSV (*.csv)"
        )
        if not destino:
            return
        with open(destino, "w", newline="", encoding="utf-8-sig") as arquivo:
            writer = csv.writer(arquivo, delimiter=";")
            writer.writerow(["Data", "Tipo", "Descricao", "Categoria", "Valor", "Status", "Observacoes"])
            for row in range(self.tbl_entradas.rowCount()):
                writer.writerow([
                    self.tbl_entradas.item(row, col).text() if self.tbl_entradas.item(row, col) else ""
                    for col in range(self.tbl_entradas.columnCount())
                ])
        QMessageBox.information(self, "Caixa", f"Relatorio exportado:\n{destino}")

    def _data_qdate(self, texto):
        try:
            data = datetime.strptime(texto or "", "%Y-%m-%d")
            return QDate(data.year, data.month, data.day)
        except ValueError:
            return QDate.currentDate()

    def _data_para_tela(self, texto):
        try:
            return datetime.strptime(texto or "", "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return texto or ""

    def _texto_status(self, status, tipo="ENTRADA"):
        if status == "RECEBIDO":
            return "Pago" if tipo == "SAIDA" else "Recebido"
        return "Previsto"

    def _texto_tipo(self, tipo):
        return "Saida" if tipo == "SAIDA" else "Entrada"

    def _formatar_moeda(self, valor):
        return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _card_total(self, titulo, valor):
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
        numero.setStyleSheet("color: #0f172a; font-size: 26px; font-weight: 900; border: none;")
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
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                padding: 7px 10px;
                font-size: 20px;
                font-weight: 600;
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
            QPushButton:hover { background-color: #1d4ed8; }
        """

    def _success_button_style(self):
        return """
            QPushButton {
                background-color: #16a34a;
                color: white;
                border: none;
                border-radius: 11px;
                padding: 10px 12px;
                font-size: 20px;
                font-weight: 800;
            }
            QPushButton:hover { background-color: #15803d; }
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
            QPushButton:hover { background-color: #cbd5e1; }
        """

    def _danger_button_style(self):
        return """
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 11px;
                padding: 10px 12px;
                font-size: 20px;
                font-weight: 800;
            }
            QPushButton:hover { background-color: #b91c1c; }
        """
