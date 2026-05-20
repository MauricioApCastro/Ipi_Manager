from pathlib import Path
from datetime import datetime
import csv
from urllib.parse import quote

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
    QTextEdit,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

from src.database.repositories import AlunoRepository, CaixaRepository, FinanceiroRepository
from src.services.recibo_service import gerar_recibo_pagamento_pdf


class FinanceiroWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.repo_aluno = AlunoRepository(db)
        self.repo_financeiro = FinanceiroRepository(db)
        self.repo_caixa = CaixaRepository(db)
        self.alunos = []
        self.alunos_filtrados = []
        self.aluno_selecionado_id = None
        self.carregando_config = False
        self.ultimo_recibo_gerado = None
        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        titulo = QLabel("Financeiro")
        titulo.setStyleSheet("color: #0f172a; font-size: 42px; font-weight: 900;")
        subtitulo = QLabel("Gere recibos e envie pelo WhatsApp do responsavel.")
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

        self.txt_busca = self._line_edit("Buscar pelas iniciais")
        self.txt_busca.textChanged.connect(self.filtrar_alunos)

        self.lista_alunos = QListWidget()
        self.lista_alunos.itemClicked.connect(self.selecionar_aluno_lista)
        self._preparar_lista(self.lista_alunos)

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

        self.chk_aplicar_multa = QCheckBox("Aplicar multa")
        self.chk_aplicar_multa.stateChanged.connect(self.atualizar_preview)
        self.chk_aplicar_multa.setStyleSheet(self._checkbox_style())

        self.spin_pagas = QSpinBox()
        self.spin_pagas.setRange(0, 14)
        self.spin_pagas.setPrefix("Parcelas pagas ")
        self.spin_pagas.valueChanged.connect(self.atualizar_preview)
        self._preparar_campo(self.spin_pagas)

        self.txt_pix = self._line_edit("PIX")
        self.txt_pix.setText("1196321-6999")

        self.txt_observacoes_recibo = QTextEdit()
        self.txt_observacoes_recibo.setPlaceholderText("Observacoes do recibo")
        self.txt_observacoes_recibo.setFixedHeight(78)
        self.txt_observacoes_recibo.setStyleSheet(self._text_edit_style())

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

        self.btn_gerar = QPushButton("Gerar recibo e abrir WhatsApp")
        self.btn_gerar.clicked.connect(self.gerar_recibo)
        self.btn_gerar.setMinimumHeight(42)
        self.btn_gerar.setStyleSheet(self._primary_button_style())

        layout.addWidget(self.txt_busca)
        layout.addWidget(self.lista_alunos)
        layout.addLayout(linha_data)
        layout.addLayout(linha_valores)
        layout.addWidget(self.chk_aplicar_multa)
        layout.addWidget(self.spin_pagas)
        layout.addWidget(self.txt_pix)
        layout.addWidget(self.txt_observacoes_recibo)
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
        self.tbl_pendentes_mes.cellClicked.connect(self.selecionar_aluno_pendente)

        self.btn_aviso_pendente = QPushButton("Enviar aviso WhatsApp")
        self.btn_aviso_pendente.clicked.connect(self.enviar_aviso_pendente)
        self.btn_aviso_pendente.setMinimumHeight(42)
        self.btn_aviso_pendente.setStyleSheet(self._secondary_button_style())

        self.btn_exportar_pendentes = QPushButton("Exportar pendentes CSV")
        self.btn_exportar_pendentes.clicked.connect(self.exportar_pendentes_csv)
        self.btn_exportar_pendentes.setMinimumHeight(42)
        self.btn_exportar_pendentes.setStyleSheet(self._secondary_button_style())

        layout.addWidget(self.lbl_pendentes_mes)
        layout.addWidget(self.tbl_pendentes_mes)
        layout.addWidget(self.btn_aviso_pendente)
        layout.addWidget(self.btn_exportar_pendentes)
        return painel

    def carregar_dados(self):
        self.alunos = self.repo_aluno.get_all()
        self.alunos_filtrados = []
        self.aluno_selecionado_id = None
        self._popular_lista_alunos()
        self.carregar_financeiro_aluno()
        self.atualizar_pendentes_mes()

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
        self.carregar_financeiro_aluno()

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
        self.carregar_financeiro_aluno()

    def selecionar_aluno_pendente(self, row, _column):
        item = self.tbl_pendentes_mes.item(row, 0)
        if not item:
            return

        aluno_id = item.data(Qt.UserRole)
        if not aluno_id:
            return

        aluno = next((item for item in self.alunos if item.id == aluno_id), None)
        if not aluno:
            return

        self.aluno_selecionado_id = aluno_id
        self.txt_busca.blockSignals(True)
        self.txt_busca.setText(aluno.nome or "")
        self.txt_busca.blockSignals(False)
        self.alunos_filtrados = [
            item for item in self.alunos
            if (item.nome or "").strip().lower().startswith((aluno.nome or "").strip().lower())
        ]
        self._popular_lista_alunos()
        self.carregar_financeiro_aluno()

    def carregar_financeiro_aluno(self):
        aluno = self.aluno_atual()
        if not aluno:
            self.limpar_financeiro_aluno()
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
        self.txt_observacoes_recibo.clear()
        self.chk_aplicar_multa.setChecked(False)
        self.carregando_config = False
        self.atualizar_preview()

    def limpar_financeiro_aluno(self):
        self.carregando_config = True
        self.txt_primeiro_pagamento.clear()
        self.spin_pagas.setValue(0)
        self.spin_valor.setValue(135.00)
        self.spin_valor_atraso.setValue(155.00)
        self.spin_vencimento.setValue(10)
        self.txt_pix.setText("1196321-6999")
        self.txt_observacoes_recibo.clear()
        self.chk_aplicar_multa.setChecked(False)
        self.carregando_config = False

    def atualizar_preview(self):
        aluno = self.aluno_atual()
        if not aluno:
            self.lbl_preview.setText("Cadastre um aluno antes de gerar recibos.")
            self.lbl_pendentes.setText("Nenhum aluno selecionado.")
            return

        turma = self._texto_turma(aluno.turma_id)
        pagas = self.spin_pagas.value()
        pendentes = max(14 - pagas, 0)
        valor_pagamento = self._valor_pagamento_atual()
        multa = "Sim" if self.chk_aplicar_multa.isChecked() else "Nao"
        self.lbl_pendentes.setText(f"Pendentes: {pendentes} de 14 parcelas")
        self.lbl_preview.setText(
            f"Aluno: {aluno.nome}\n"
            f"Turma: {turma}\n"
            f"Curso: 14 parcelas\n"
            f"Pagas: {pagas}\n"
            f"Pendentes: {pendentes}\n"
            f"Multa aplicada: {multa}\n"
            f"Valor a registrar: R$ {valor_pagamento:.2f}\n"
            f"Arquivo gerado em PDF moderno, pronto para enviar ao responsavel."
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

        if self.spin_pagas.value() >= 14:
            QMessageBox.information(self, "Pagamento", "Todas as parcelas deste aluno já foram pagas.")
            return

        self.salvar_config_atual()
        novas_pagas = self.repo_financeiro.registrar_pagamento(aluno.id)
        self.repo_caixa.add_entrada(
            datetime.now().strftime("%Y-%m-%d"),
            f"Mensalidade - {aluno.nome} - parcela {novas_pagas}/14",
            "Mensalidade",
            self._valor_pagamento_atual(),
            "RECEBIDO",
            "Registrado pelo financeiro com multa" if self.chk_aplicar_multa.isChecked() else "Registrado pelo financeiro",
        )
        self.spin_pagas.setValue(novas_pagas)
        self.atualizar_preview()
        self.atualizar_pendentes_mes()
        whatsapp_aberto = self._gerar_recibo_e_abrir_whatsapp(aluno)
        detalhe_whatsapp = (
            f"O WhatsApp do responsavel foi aberto com a mensagem do recibo.\nPDF: {self.ultimo_recibo_gerado}"
            if whatsapp_aberto
            else "O recibo nao foi enviado porque falta WhatsApp do responsavel."
        )
        QMessageBox.information(
            self,
            "Pagamento",
            f"Pagamento registrado. Parcelas pagas: {novas_pagas}/14.\n"
            f"{detalhe_whatsapp}",
        )

    def gerar_recibo(self):
        aluno = self.aluno_atual()
        if not aluno:
            QMessageBox.warning(self, "Recibo", "Selecione um aluno.")
            return

        data = self.txt_primeiro_pagamento.text().strip()
        if "_" in data or len(data) != 10:
            QMessageBox.warning(self, "Recibo", "Informe a data do primeiro pagamento.")
            return

        if not self._gerar_recibo_e_abrir_whatsapp(aluno):
            return
        QMessageBox.information(
            self,
            "Recibo",
            f"Recibo gerado e WhatsApp do responsavel aberto.\nPDF: {self.ultimo_recibo_gerado}",
        )

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
            item_aluno = QTableWidgetItem(aluno.nome or "")
            item_aluno.setData(Qt.UserRole, aluno.id)
            self.tbl_pendentes_mes.setItem(row, 0, item_aluno)
            self.tbl_pendentes_mes.setItem(row, 1, QTableWidgetItem(f"{parcela_atual}/14"))
            self.tbl_pendentes_mes.setItem(row, 2, QTableWidgetItem(f"{pagas}/14"))
            self.tbl_pendentes_mes.setItem(row, 3, QTableWidgetItem(aluno.whatsapp_resp or ""))

        self.lbl_pendentes_mes.setText(f"{len(pendentes)} aluno(s) pendente(s) neste mês")

    def enviar_aviso_pendente(self):
        itens = self.tbl_pendentes_mes.selectedItems()
        if not itens:
            QMessageBox.warning(self, "Financeiro", "Selecione um aluno pendente.")
            return

        row = itens[0].row()
        item_aluno = self.tbl_pendentes_mes.item(row, 0)
        aluno_id = item_aluno.data(Qt.UserRole) if item_aluno else None
        aluno = next((item for item in self.alunos if item.id == aluno_id), None)
        if not aluno:
            return

        telefone = self._telefone_responsavel(aluno)
        if not telefone:
            QMessageBox.warning(self, "Financeiro", "Aluno sem WhatsApp do responsavel cadastrado.")
            return

        parcela = self.tbl_pendentes_mes.item(row, 1).text()
        mensagem = (
            f"Ola! Identificamos uma pendencia financeira de {aluno.nome}, parcela {parcela}, "
            "na IPI Informatica. Por favor, entre em contato para regularizar."
        )
        QDesktopServices.openUrl(QUrl(f"https://wa.me/55{telefone}?text={quote(mensagem)}"))

    def _gerar_recibo_e_abrir_whatsapp(self, aluno):
        if not self._validar_recibo(aluno):
            return False

        self.salvar_config_atual()
        arquivo = self._gerar_arquivo_recibo(aluno)
        self.ultimo_recibo_gerado = arquivo.resolve()
        telefone = self._telefone_responsavel(aluno)
        mensagem = (
            f"Ola! Segue o recibo de pagamento de {aluno.nome} da IPI Informatica."
        )
        QDesktopServices.openUrl(QUrl(f"https://wa.me/55{telefone}?text={quote(mensagem)}"))
        return True

    def _validar_recibo(self, aluno):
        if not aluno:
            QMessageBox.warning(self, "Recibo", "Selecione um aluno.")
            return False

        data = self.txt_primeiro_pagamento.text().strip()
        if "_" in data or len(data) != 10:
            QMessageBox.warning(self, "Recibo", "Informe a data do primeiro pagamento.")
            return False

        if not self._telefone_responsavel(aluno):
            QMessageBox.warning(
                self,
                "Responsavel",
                "Cadastre o WhatsApp do responsavel. Recibos financeiros nao sao enviados para o telefone do aluno.",
            )
            return False

        return True

    def _gerar_arquivo_recibo(self, aluno):
        nome_limpo = "".join(char for char in aluno.nome if char.isalnum() or char in (" ", "_")).strip()
        data_arquivo = datetime.now().strftime("%Y%m%d_%H%M")
        destino = Path("recibos") / f"RECIBO_{nome_limpo.replace(' ', '_')}_{data_arquivo}.pdf"
        return gerar_recibo_pagamento_pdf(
            aluno=aluno,
            turma_texto=self._texto_turma(aluno.turma_id),
            data_primeiro_pagamento=self.txt_primeiro_pagamento.text().strip(),
            parcelas_pagas=self.spin_pagas.value(),
            valor_mensalidade=self.spin_valor.value(),
            valor_atraso=self.spin_valor_atraso.value(),
            dia_vencimento=self.spin_vencimento.value(),
            pix=self.txt_pix.text().strip(),
            observacoes=self._observacoes_recibo_atual(),
            destino=destino,
        )

    def _valor_pagamento_atual(self):
        if self.chk_aplicar_multa.isChecked():
            return self.spin_valor_atraso.value()
        return self.spin_valor.value()

    def _observacoes_recibo_atual(self):
        observacoes = self.txt_observacoes_recibo.toPlainText().strip()
        if not self.chk_aplicar_multa.isChecked():
            return observacoes

        texto_multa = f"Multa aplicada. Valor recebido: R$ {self.spin_valor_atraso.value():.2f}."
        if observacoes:
            return f"{texto_multa}\n{observacoes}"
        return texto_multa

    def _telefone_responsavel(self, aluno):
        return self._normalizar_telefone(aluno.whatsapp_resp if aluno else "")

    def _normalizar_telefone(self, telefone):
        digitos = "".join(char for char in (telefone or "") if char.isdigit())
        if len(digitos) < 10:
            return ""
        return digitos[-11:]

    def exportar_pendentes_csv(self):
        destino, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar pendentes",
            f"pendentes_{datetime.now().strftime('%Y_%m')}.csv",
            "CSV (*.csv)",
        )
        if not destino:
            return
        with open(destino, "w", newline="", encoding="utf-8-sig") as arquivo:
            writer = csv.writer(arquivo, delimiter=";")
            writer.writerow(["Aluno", "Parcela", "Pagas", "Telefone"])
            for row in range(self.tbl_pendentes_mes.rowCount()):
                writer.writerow([
                    self.tbl_pendentes_mes.item(row, col).text() if self.tbl_pendentes_mes.item(row, col) else ""
                    for col in range(self.tbl_pendentes_mes.columnCount())
                ])
        QMessageBox.information(self, "Financeiro", f"Pendentes exportados:\n{destino}")

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
                _duracao,
                _aulas_semana,
                _capacidade,
                _ocupadas,
            ) = turma
            if tid == turma_id:
                return f"{nome} - {dia} {horario} + {segundo_dia} {segundo_horario}"
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
                background-color: #dbeafe;
                color: #1e3a8a;
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

    def _checkbox_style(self):
        return "color: #334155; font-size: 20px; font-weight: 700;"

    def _text_edit_style(self):
        return """
            QTextEdit {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                padding: 7px 10px;
                font-size: 20px;
                font-weight: 600;
            }
            QTextEdit:focus {
                background-color: white;
                border-color: #3b82f6;
            }
        """
