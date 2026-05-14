from pathlib import Path
from datetime import datetime

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
    QDoubleSpinBox,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
)
from PyQt5.QtCore import Qt

from src.database.repositories import AlunoRepository, FinanceiroRepository
from src.services.recibo_service import gerar_recibo_pagamento_pdf


class FinanceiroWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.repo_aluno = AlunoRepository(db)
        self.repo_financeiro = FinanceiroRepository(db)
        self.alunos = []
        self.alunos_filtrados = []
        self.carregando_config = False
        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        titulo = QLabel("Financeiro")
        titulo.setStyleSheet("color: #0f172a; font-size: 42px; font-weight: 900;")
        subtitulo = QLabel("Gere recibos em planilha para enviar ao aluno.")
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet("color: #64748b; font-size: 20px; font-weight: 600;")
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)

        lado_direito_widget = QWidget()
        lado_direito = QVBoxLayout(lado_direito_widget)
        lado_direito.setContentsMargins(0, 0, 0, 0)
        lado_direito.setSpacing(14)
        lado_direito.addWidget(self._criar_painel_preview(), 2)
        lado_direito.addWidget(self._criar_painel_pendentes_mes(), 5)
        body.addWidget(self._criar_painel_recibo())
        body.addWidget(lado_direito_widget)
        body.setStretchFactor(0, 5)
        body.setStretchFactor(1, 7)
        body.setSizes([420, 720])
        layout.addWidget(body, 1)

    def _criar_painel_recibo(self):
        painel = self._painel_base("Recibo do aluno")
        layout = painel.layout()

        self.combo_aluno = QComboBox()
        self.combo_aluno.currentIndexChanged.connect(self.carregar_financeiro_aluno)
        self._preparar_campo(self.combo_aluno)

        self.txt_busca = self._line_edit("Buscar aluno")
        self.txt_busca.textChanged.connect(self.filtrar_alunos)

        linha_data = QHBoxLayout()
        self.txt_primeiro_pagamento = self._line_edit("dd/mm/aaaa")
        self.txt_primeiro_pagamento.setInputMask("00/00/0000;_")

        self.spin_vencimento = QSpinBox()
        self.spin_vencimento.setRange(1, 31)
        self.spin_vencimento.setPrefix("Vence dia ")
        self.spin_vencimento.setValue(10)
        self._preparar_campo(self.spin_vencimento)

        linha_data.addWidget(self.txt_primeiro_pagamento)
        linha_data.addWidget(self.spin_vencimento)

        linha_valores = QHBoxLayout()
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(0, 9999)
        self.spin_valor.setValue(135.00)
        self.spin_valor.setPrefix("R$ ")
        self._preparar_campo(self.spin_valor)

        self.spin_valor_atraso = QDoubleSpinBox()
        self.spin_valor_atraso.setRange(0, 9999)
        self.spin_valor_atraso.setValue(155.00)
        self.spin_valor_atraso.setPrefix("Após venc. R$ ")
        self._preparar_campo(self.spin_valor_atraso)

        linha_valores.addWidget(self.spin_valor)
        linha_valores.addWidget(self.spin_valor_atraso)

        self.spin_pagas = QSpinBox()
        self.spin_pagas.setRange(0, 14)
        self.spin_pagas.setPrefix("Parcelas pagas ")
        self.spin_pagas.valueChanged.connect(self.atualizar_preview)
        self._preparar_campo(self.spin_pagas)

        self.txt_pix = self._line_edit("PIX")
        self.txt_pix.setText("1196321-6999")

        self.lbl_pendentes = QLabel("")
        self.lbl_pendentes.setWordWrap(True)
        self.lbl_pendentes.setStyleSheet("""
            color: #9a3412;
            background-color: #fff7ed;
            border: 1px solid #fed7aa;
            border-radius: 10px;
            padding: 10px;
            font-size: 20px;
            font-weight: 800;
        """)

        self.btn_registrar = QPushButton("Registrar pagamento")
        self.btn_registrar.clicked.connect(self.registrar_pagamento)
        self.btn_registrar.setMinimumHeight(42)
        self.btn_registrar.setStyleSheet(self._success_button_style())

        self.btn_gerar = QPushButton("Gerar recibo em PDF")
        self.btn_gerar.clicked.connect(self.gerar_recibo)
        self.btn_gerar.setMinimumHeight(42)
        self.btn_gerar.setStyleSheet(self._primary_button_style())

        layout.addWidget(self.txt_busca)
        layout.addWidget(self.combo_aluno)
        layout.addLayout(linha_data)
        layout.addLayout(linha_valores)
        layout.addWidget(self.spin_pagas)
        layout.addWidget(self.txt_pix)
        layout.addWidget(self.lbl_pendentes)
        layout.addWidget(self.btn_registrar)
        layout.addWidget(self.btn_gerar)
        layout.addStretch()
        return painel

    def _criar_painel_preview(self):
        painel = self._painel_base("Como ficará")
        layout = painel.layout()

        self.lbl_preview = QLabel("")
        self.lbl_preview.setWordWrap(True)
        self.lbl_preview.setStyleSheet("""
            color: #0f172a;
            font-size: 20px;
            font-weight: 700;
            line-height: 1.4;
            border: none;
        """)
        layout.addWidget(self.lbl_preview)
        layout.addStretch()
        return painel

    def _criar_painel_pendentes_mes(self):
        painel = self._painel_base("Pendentes do mês")
        layout = painel.layout()

        self.lbl_pendentes_mes = QLabel("")
        self.lbl_pendentes_mes.setStyleSheet("""
            color: #9a3412;
            font-size: 20px;
            font-weight: 800;
            border: none;
        """)

        self.tbl_pendentes_mes = QTableWidget(0, 4)
        self.tbl_pendentes_mes.setHorizontalHeaderLabels(["Aluno", "Parcela", "Pagas", "Telefone"])
        self._preparar_tabela(self.tbl_pendentes_mes)

        layout.addWidget(self.lbl_pendentes_mes)
        layout.addWidget(self.tbl_pendentes_mes)
        return painel

    def carregar_dados(self):
        self.alunos = self.repo_aluno.get_all()
        self.alunos_filtrados = self.alunos[:]
        self._popular_combo_alunos()
        self.carregar_financeiro_aluno()
        self.atualizar_pendentes_mes()

    def _popular_combo_alunos(self):
        atual = self.combo_aluno.currentData()
        self.combo_aluno.blockSignals(True)
        self.combo_aluno.clear()
        for aluno in self.alunos_filtrados:
            self.combo_aluno.addItem(aluno.nome, aluno.id)
        index = self.combo_aluno.findData(atual)
        if index >= 0:
            self.combo_aluno.setCurrentIndex(index)
        self.combo_aluno.blockSignals(False)

    def filtrar_alunos(self):
        termo = self.txt_busca.text().strip().lower()
        if not termo:
            self.alunos_filtrados = self.alunos[:]
        else:
            self.alunos_filtrados = [
                aluno for aluno in self.alunos
                if termo in (aluno.nome or "").lower()
                or termo in (aluno.cpf or "").lower()
            ]
        self._popular_combo_alunos()
        self.carregar_financeiro_aluno()

    def aluno_atual(self):
        aluno_id = self.combo_aluno.currentData()
        if not aluno_id:
            return None
        return next((aluno for aluno in self.alunos if aluno.id == aluno_id), None)

    def carregar_financeiro_aluno(self):
        aluno = self.aluno_atual()
        if not aluno:
            self.atualizar_preview()
            return

        config = self.repo_financeiro.get_config(aluno.id)
        self.carregando_config = True
        self.txt_primeiro_pagamento.setText(config["data_primeiro_pagamento"])
        self.spin_pagas.setValue(config["parcelas_pagas"])
        self.spin_valor.setValue(config["valor_mensalidade"])
        self.spin_valor_atraso.setValue(config["valor_atraso"])
        self.spin_vencimento.setValue(config["dia_vencimento"])
        self.txt_pix.setText(config["pix"])
        self.carregando_config = False
        self.atualizar_preview()

    def atualizar_preview(self):
        aluno = self.aluno_atual()
        if not aluno:
            self.lbl_preview.setText("Cadastre um aluno antes de gerar recibos.")
            self.lbl_pendentes.setText("Nenhum aluno selecionado.")
            return

        turma = self._texto_turma(aluno.turma_id)
        pagas = self.spin_pagas.value()
        pendentes = max(14 - pagas, 0)
        self.lbl_pendentes.setText(f"Pendentes: {pendentes} de 14 parcelas")
        self.lbl_preview.setText(
            f"Aluno: {aluno.nome}\n"
            f"Turma: {turma}\n"
            f"Curso: 14 parcelas\n"
            f"Pagas: {pagas}\n"
            f"Pendentes: {pendentes}\n"
            f"Arquivo gerado em PDF moderno, pronto para enviar ao aluno."
        )

    def salvar_config_atual(self):
        aluno = self.aluno_atual()
        if not aluno:
            return False
        self.repo_financeiro.salvar_config(
            aluno.id,
            self.txt_primeiro_pagamento.text().strip(),
            self.spin_pagas.value(),
            self.spin_valor.value(),
            self.spin_valor_atraso.value(),
            self.spin_vencimento.value(),
            self.txt_pix.text().strip(),
        )
        return True

    def registrar_pagamento(self):
        aluno = self.aluno_atual()
        if not aluno:
            QMessageBox.warning(self, "Pagamento", "Selecione um aluno.")
            return

        data = self.txt_primeiro_pagamento.text().strip()
        if "_" in data or len(data) != 10:
            QMessageBox.warning(self, "Pagamento", "Informe a data do primeiro pagamento antes de registrar.")
            return

        self.salvar_config_atual()
        novas_pagas = self.repo_financeiro.registrar_pagamento(aluno.id)
        self.spin_pagas.setValue(novas_pagas)
        self.atualizar_preview()
        self.atualizar_pendentes_mes()
        QMessageBox.information(self, "Pagamento", f"Pagamento registrado. Parcelas pagas: {novas_pagas}/14.")

    def gerar_recibo(self):
        aluno = self.aluno_atual()
        if not aluno:
            QMessageBox.warning(self, "Recibo", "Selecione um aluno.")
            return

        data = self.txt_primeiro_pagamento.text().strip()
        if "_" in data or len(data) != 10:
            QMessageBox.warning(self, "Recibo", "Informe a data do primeiro pagamento.")
            return

        self.salvar_config_atual()

        nome_limpo = "".join(char for char in aluno.nome if char.isalnum() or char in (" ", "_")).strip()
        destino_padrao = Path("recibos") / f"RECIBO_{nome_limpo.replace(' ', '_')}.pdf"
        destino, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar recibo",
            str(destino_padrao),
            "PDF (*.pdf)",
        )
        if not destino:
            return

        arquivo = gerar_recibo_pagamento_pdf(
            aluno=aluno,
            turma_texto=self._texto_turma(aluno.turma_id),
            data_primeiro_pagamento=data,
            parcelas_pagas=self.spin_pagas.value(),
            valor_mensalidade=self.spin_valor.value(),
            valor_atraso=self.spin_valor_atraso.value(),
            dia_vencimento=self.spin_vencimento.value(),
            pix=self.txt_pix.text().strip(),
            destino=destino,
        )
        QMessageBox.information(self, "Recibo", f"Recibo gerado:\n{arquivo}")

    def atualizar_pendentes_mes(self):
        hoje = datetime.now()
        pendentes = []

        for aluno in self.alunos:
            config = self.repo_financeiro.get_config(aluno.id)
            data_inicio = config["data_primeiro_pagamento"]
            if not data_inicio:
                continue

            try:
                inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
            except ValueError:
                continue

            parcela_atual = ((hoje.year - inicio.year) * 12) + (hoje.month - inicio.month) + 1
            parcela_atual = max(1, min(parcela_atual, 14))
            pagas = config["parcelas_pagas"] or 0

            if pagas < parcela_atual:
                pendentes.append((aluno, parcela_atual, pagas))

        self.tbl_pendentes_mes.setRowCount(0)
        for row, (aluno, parcela_atual, pagas) in enumerate(pendentes):
            self.tbl_pendentes_mes.insertRow(row)
            self.tbl_pendentes_mes.setItem(row, 0, QTableWidgetItem(aluno.nome or ""))
            self.tbl_pendentes_mes.setItem(row, 1, QTableWidgetItem(f"{parcela_atual}/14"))
            self.tbl_pendentes_mes.setItem(row, 2, QTableWidgetItem(f"{pagas}/14"))
            self.tbl_pendentes_mes.setItem(row, 3, QTableWidgetItem(aluno.whatsapp_aluno or aluno.whatsapp_resp or ""))

        self.lbl_pendentes_mes.setText(f"{len(pendentes)} aluno(s) pendente(s) neste mês")

    def _texto_turma(self, turma_id):
        if not turma_id:
            return "-"
        for turma in self.repo_aluno.get_turmas_com_vagas():
            (
                tid,
                nome,
                dia,
                horario,
                segundo_dia,
                segundo_horario,
                duracao,
                aulas_semana,
                _capacidade,
                _ocupadas,
            ) = turma
            if tid == turma_id:
                return f"{nome} - {dia} {horario} + {segundo_dia} {segundo_horario} ({aulas_semana}x {duracao}min)"
        return "-"

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

            QPushButton:hover {
                background-color: #15803d;
            }
        """
