import csv
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QLineEdit,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QListWidget, QListWidgetItem,
)
from PyQt5.QtCore import Qt

from src.database.repositories import AlunoRepository, FinanceiroRepository, ReposicaoRepository


class HistoricoWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.repo_aluno = AlunoRepository(db)
        self.repo_financeiro = FinanceiroRepository(db)
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

        titulo = QLabel("Historico")
        titulo.setStyleSheet("color: #0f172a; font-size: 42px; font-weight: 900;")
        layout.addWidget(titulo)

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)
        body.addWidget(self._criar_painel_aluno())
        body.addWidget(self._criar_painel_historico())
        body.setStretchFactor(0, 3)
        body.setStretchFactor(1, 8)
        layout.addWidget(body, 1)

    def _criar_painel_aluno(self):
        painel = self._painel_base("Aluno")
        layout = painel.layout()
        self.txt_busca = self._line_edit("Buscar pelas iniciais")
        self.txt_busca.textChanged.connect(self.filtrar_alunos)
        self.lista_alunos = QListWidget()
        self.lista_alunos.itemClicked.connect(self.selecionar_aluno)
        self._preparar_lista(self.lista_alunos)
        self.btn_exportar = QPushButton("Exportar historico")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        self.btn_exportar.setStyleSheet(self._primary_button_style())
        layout.addWidget(self.txt_busca)
        layout.addWidget(self.lista_alunos)
        layout.addWidget(self.btn_exportar)
        layout.addStretch()
        return painel

    def _criar_painel_historico(self):
        painel = self._painel_base("Ficha do aluno")
        layout = painel.layout()
        self.lbl_resumo = QLabel("Selecione um aluno.")
        self.lbl_resumo.setWordWrap(True)
        self.lbl_resumo.setStyleSheet("color: #0f172a; font-size: 18px; font-weight: 700; border: none;")
        self.tbl_historico = QTableWidget(0, 4)
        self.tbl_historico.setHorizontalHeaderLabels(["Data", "Tipo", "Descricao", "Status"])
        self._preparar_tabela(self.tbl_historico)
        layout.addWidget(self.lbl_resumo)
        layout.addWidget(self.tbl_historico, 1)
        return painel

    def carregar_dados(self):
        self.alunos = self.repo_aluno.get_all()
        self.alunos_filtrados = []
        self.aluno_selecionado_id = None
        self._popular_lista()
        self._limpar()

    def filtrar_alunos(self):
        termo = self.txt_busca.text().strip().lower()
        self.aluno_selecionado_id = None
        self.alunos_filtrados = [
            aluno for aluno in self.alunos
            if termo and (aluno.nome or "").strip().lower().startswith(termo)
        ]
        self._popular_lista()
        self._limpar()

    def _popular_lista(self):
        self.lista_alunos.clear()
        for aluno in self.alunos_filtrados:
            item = QListWidgetItem(aluno.nome or "")
            item.setData(Qt.UserRole, aluno.id)
            self.lista_alunos.addItem(item)

    def selecionar_aluno(self, item):
        self.aluno_selecionado_id = item.data(Qt.UserRole)
        self.carregar_historico()

    def aluno_atual(self):
        return next((aluno for aluno in self.alunos if aluno.id == self.aluno_selecionado_id), None)

    def carregar_historico(self):
        aluno = self.aluno_atual()
        if not aluno:
            self._limpar()
            return

        config = self.repo_financeiro.get_config(aluno.id)
        linhas = []
        if config["data_primeiro_pagamento"]:
            linhas.append((config["data_primeiro_pagamento"], "Financeiro", f"Parcelas pagas: {config['parcelas_pagas']}/14", "Ativo"))

        with self.db.connection() as conn:
            for data_hora, maquina, obs in conn.execute(
                "SELECT data_hora, maquina_tag, observacao FROM presencas WHERE aluno_id = ? ORDER BY data_hora DESC",
                (aluno.id,),
            ).fetchall():
                linhas.append((self._data_hora_para_tela(data_hora), "Frequencia", f"Maquina {maquina or '-'}", obs or "Presente"))

        for _rid, data_falta, data_reposicao, status, obs in self.repo_reposicao.get_aluno(aluno.id):
            linhas.append((self._data_para_tela(data_falta), "Reposicao", f"Reposicao em {self._data_para_tela(data_reposicao)}", status))

        self.lbl_resumo.setText(
            f"Aluno: {aluno.nome}\nCPF: {aluno.cpf or '-'}\nModulo atual: {aluno.modulo_atual or '-'}\nObservacoes: {aluno.observacoes or '-'}"
        )
        self.tbl_historico.setRowCount(0)
        for row, (data, tipo, descricao, status) in enumerate(linhas):
            self.tbl_historico.insertRow(row)
            self.tbl_historico.setItem(row, 0, QTableWidgetItem(data or ""))
            self.tbl_historico.setItem(row, 1, QTableWidgetItem(tipo or ""))
            self.tbl_historico.setItem(row, 2, QTableWidgetItem(descricao or ""))
            self.tbl_historico.setItem(row, 3, QTableWidgetItem(status or ""))

    def exportar_csv(self):
        aluno = self.aluno_atual()
        if not aluno:
            QMessageBox.warning(self, "Historico", "Selecione um aluno.")
            return
        destino, _ = QFileDialog.getSaveFileName(self, "Exportar historico", f"historico_{aluno.nome}.csv", "CSV (*.csv)")
        if not destino:
            return
        with open(destino, "w", newline="", encoding="utf-8-sig") as arquivo:
            writer = csv.writer(arquivo, delimiter=";")
            writer.writerow(["Aluno", aluno.nome])
            writer.writerow(["Data", "Tipo", "Descricao", "Status"])
            for row in range(self.tbl_historico.rowCount()):
                writer.writerow([
                    self.tbl_historico.item(row, col).text() if self.tbl_historico.item(row, col) else ""
                    for col in range(self.tbl_historico.columnCount())
                ])
        QMessageBox.information(self, "Historico", f"Historico exportado:\n{destino}")

    def _limpar(self):
        self.lbl_resumo.setText("Selecione um aluno.")
        self.tbl_historico.setRowCount(0)

    def _data_para_tela(self, texto):
        try:
            return datetime.strptime(texto or "", "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return texto or ""

    def _data_hora_para_tela(self, texto):
        try:
            return datetime.strptime(texto or "", "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
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
        edit.setStyleSheet(self._input_style())
        return edit

    def _preparar_lista(self, lista):
        lista.setMinimumHeight(160)
        lista.setStyleSheet("QListWidget { background-color: #f8fafc; color: #0f172a; border: 1px solid #dbe3ef; border-radius: 10px; font-size: 20px; font-weight: 600; } QListWidget::item { padding: 8px 10px; } QListWidget::item:selected { background-color: #dbeafe; color: #1e3a8a; }")

    def _preparar_tabela(self, tabela):
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.verticalHeader().setVisible(False)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabela.setStyleSheet("QTableWidget { border: none; color: #0f172a; font-size: 18px; } QHeaderView::section { background-color: #f1f5f9; padding: 8px; font-weight: 800; }")

    def _input_style(self):
        return "QLineEdit { background-color: #f8fafc; color: #0f172a; border: 1px solid #dbe3ef; border-radius: 10px; padding: 7px 10px; font-size: 20px; font-weight: 600; }"

    def _primary_button_style(self):
        return "QPushButton { background-color: #2563eb; color: white; border: none; border-radius: 11px; padding: 10px 12px; font-size: 20px; font-weight: 800; } QPushButton:hover { background-color: #1d4ed8; }"
