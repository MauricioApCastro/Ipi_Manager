from calendar import monthrange
from datetime import datetime, date

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QSplitter,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor

from src.database.repositories import AlunoRepository, CursoRepository, FinanceiroRepository
from src.models.aluno import Aluno


class AlunoWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.repo = AlunoRepository(db)
        self.repo_curso = CursoRepository(db)
        self.repo_financeiro = FinanceiroRepository(db)
        self.alunos = []
        self.modulo_checks = []
        self.botoes_dia_pagamento = []
        self.aluno_em_edicao_id = None
        hoje = date.today()
        self.mes_pagamento = hoje.month
        self.ano_pagamento = hoje.year
        self.data_pagamento_selecionada = None

        self.setup_ui()
        self.carregar_dados()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "painel_pagamento_flutuante"):
            self._posicionar_calendario()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        titulo = QLabel("Alunos")
        titulo.setStyleSheet("color: #0f172a; font-size: 42px; font-weight: 900;")
        title_box.addWidget(titulo)
        header.addLayout(title_box)
        header.addStretch()

        self.txt_busca = QLineEdit()
        self.txt_busca.setPlaceholderText("Buscar aluno")
        self.txt_busca.setMinimumWidth(180)
        self.txt_busca.textChanged.connect(self.filtrar_tabela)
        self._preparar_campo(self.txt_busca)
        header.addWidget(self.txt_busca)
        layout.addLayout(header)

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)

        coluna_alunos_widget = QWidget()
        coluna_alunos = QVBoxLayout(coluna_alunos_widget)
        coluna_alunos.setContentsMargins(0, 0, 0, 0)
        coluna_alunos.setSpacing(14)
        coluna_alunos.addWidget(self._criar_painel_academico(), 3)
        coluna_alunos.addWidget(self._criar_painel_tabela(), 5)

        body.addWidget(self._criar_coluna_cadastro())
        body.addWidget(coluna_alunos_widget)
        body.setStretchFactor(0, 4)
        body.setStretchFactor(1, 7)
        body.setSizes([360, 720])
        layout.addWidget(body, 1)

        self.painel_pagamento_flutuante = self._criar_painel_pagamento()
        self.painel_pagamento_flutuante.setParent(self)
        self.painel_pagamento_flutuante.hide()
        self._posicionar_calendario()
        self._configurar_calendario_retratil()

    def _criar_coluna_cadastro(self):
        coluna = QWidget()
        layout = QVBoxLayout(coluna)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(self._criar_painel_dados(), 1)
        return coluna

    def _configurar_calendario_retratil(self):
        self.calendario_hide_margin = 24
        self.calendario_timer = QTimer(self)
        self.calendario_timer.setInterval(120)
        self.calendario_timer.timeout.connect(self._atualizar_calendario_retratil)
        self.calendario_timer.start()

    def _alternar_calendario(self):
        if self.painel_pagamento_flutuante.isVisible():
            self._ocultar_calendario()
            return
        self._mostrar_calendario()

    def _mostrar_calendario(self):
        self._posicionar_calendario()
        self.painel_pagamento_flutuante.show()
        self.painel_pagamento_flutuante.raise_()

    def _ocultar_calendario(self):
        self.painel_pagamento_flutuante.hide()

    def _posicionar_calendario(self):
        largura = min(430, max(340, int(self.width() * 0.34)))
        altura = min(350, max(300, self.height() - 70))
        x = 28
        y = max(48, self.height() - altura - 24)
        self.painel_pagamento_flutuante.setGeometry(x, y, largura, altura)

    def _atualizar_calendario_retratil(self):
        if not self.painel_pagamento_flutuante.isVisible():
            return

        pos = self.mapFromGlobal(QCursor.pos())
        margem = self.calendario_hide_margin
        area = self.painel_pagamento_flutuante.geometry().adjusted(-margem, -margem, margem, margem)
        botao_area = self.btn_abrir_calendario.rect()
        botao_area.moveTopLeft(self.btn_abrir_calendario.mapTo(self, botao_area.topLeft()))

        if not area.contains(pos) and not botao_area.adjusted(-margem, -margem, margem, margem).contains(pos):
            self._ocultar_calendario()

    def _criar_painel_dados(self):
        painel = self._painel_base("Dados do aluno", "#2563eb", "#eff6ff")
        layout = painel.layout()

        self.txt_nome = self._line_edit("Nome completo")

        self.txt_nascimento = self._line_edit("dd/mm/aaaa")
        self.txt_nascimento.setInputMask("00/00/0000;_")

        self.txt_whatsapp = self._line_edit("(00) 00000-0000")
        self.txt_whatsapp.setInputMask("(00) 00000-0000;_")

        self.txt_whatsapp_resp = self._line_edit("(00) 00000-0000")
        self.txt_whatsapp_resp.setInputMask("(00) 00000-0000;_")

        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Observações rápidas")
        self.txt_obs.setFixedHeight(58)
        self.txt_obs.setStyleSheet(self._text_edit_style())

        linha_pagamento = QHBoxLayout()
        linha_pagamento.setSpacing(8)
        self.lbl_pagamento_resumo = QLabel("Pagamento: selecione a data")
        self.lbl_pagamento_resumo.setStyleSheet(
            "color: #475569; font-size: 16px; font-weight: 800; border: none;"
        )
        self.btn_abrir_calendario = QPushButton("Calendario")
        self.btn_abrir_calendario.clicked.connect(self._alternar_calendario)
        self.btn_abrir_calendario.setStyleSheet(self._calendar_open_button_style())
        self.btn_abrir_calendario.setMinimumHeight(34)
        linha_pagamento.addWidget(self.lbl_pagamento_resumo, 1)
        linha_pagamento.addWidget(self.btn_abrir_calendario)

        botoes = QHBoxLayout()
        botoes.setSpacing(10)

        self.btn_adicionar = QPushButton("Matricular")
        self.btn_adicionar.clicked.connect(self.salvar_aluno)
        self.btn_adicionar.setStyleSheet(self._primary_button_style())

        self.btn_atualizar = QPushButton("Editar")
        self.btn_atualizar.clicked.connect(self.atualizar_aluno)
        self.btn_atualizar.setStyleSheet(self._secondary_button_style())

        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.clicked.connect(self.excluir_aluno)
        self.btn_excluir.setStyleSheet(self._danger_button_style())

        for botao in (self.btn_adicionar, self.btn_atualizar, self.btn_excluir):
            botao.setMinimumHeight(38)
            botao.setMinimumWidth(0)

        botoes.addWidget(self.btn_adicionar, 1)
        botoes.addWidget(self.btn_atualizar, 1)
        botoes.addWidget(self.btn_excluir, 1)

        layout.addWidget(self.txt_nome)
        layout.addWidget(self._label_campo("Data de nascimento"))
        layout.addWidget(self.txt_nascimento)
        layout.addWidget(self._label_campo("Telefone do aluno"))
        layout.addWidget(self.txt_whatsapp)
        layout.addWidget(self._label_campo("Telefone do responsavel"))
        layout.addWidget(self.txt_whatsapp_resp)
        layout.addWidget(self.txt_obs)
        layout.addLayout(linha_pagamento)
        layout.addLayout(botoes)
        layout.addStretch()
        return painel

    def _criar_painel_pagamento(self):
        painel = self._painel_base("Pagamento", "#0f766e", "#f0fdfa")
        layout = painel.layout()

        linha_mes = QHBoxLayout()
        linha_mes.setSpacing(8)

        self.btn_mes_anterior = QPushButton("<")
        self.btn_mes_anterior.setToolTip("Mes anterior")
        self.btn_mes_anterior.clicked.connect(lambda: self._mudar_mes_pagamento(-1))
        self.btn_mes_anterior.setStyleSheet(self._calendar_nav_button_style())

        self.lbl_mes_pagamento = QLabel("")
        self.lbl_mes_pagamento.setAlignment(Qt.AlignCenter)
        self.lbl_mes_pagamento.setStyleSheet(
            "color: #0f172a; font-size: 18px; font-weight: 900; border: none;"
        )

        self.btn_proximo_mes = QPushButton(">")
        self.btn_proximo_mes.setToolTip("Proximo mes")
        self.btn_proximo_mes.clicked.connect(lambda: self._mudar_mes_pagamento(1))
        self.btn_proximo_mes.setStyleSheet(self._calendar_nav_button_style())

        linha_mes.addWidget(self.btn_mes_anterior)
        linha_mes.addWidget(self.lbl_mes_pagamento, 1)
        linha_mes.addWidget(self.btn_proximo_mes)

        self.lbl_pagamento_escolhido = QLabel("Selecione o dia do primeiro pagamento")
        self.lbl_pagamento_escolhido.setWordWrap(True)
        self.lbl_pagamento_escolhido.setStyleSheet(
            "color: #475569; font-size: 16px; font-weight: 800; border: none;"
        )

        self.grid_pagamento = QGridLayout()
        self.grid_pagamento.setHorizontalSpacing(5)
        self.grid_pagamento.setVerticalSpacing(5)

        for coluna, texto in enumerate(("Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom")):
            label = QLabel(texto)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 900; border: none;")
            self.grid_pagamento.addWidget(label, 0, coluna)

        for indice in range(42):
            botao = QPushButton("")
            botao.setFixedSize(38, 32)
            botao.clicked.connect(lambda _checked=False, b=botao: self._selecionar_dia_pagamento(b.property("dia")))
            self.botoes_dia_pagamento.append(botao)
            self.grid_pagamento.addWidget(botao, (indice // 7) + 1, indice % 7)

        layout.addLayout(linha_mes)
        layout.addLayout(self.grid_pagamento)
        layout.addWidget(self.lbl_pagamento_escolhido)
        layout.addStretch()
        self._atualizar_calendario_pagamento()
        return painel

    def _criar_painel_academico(self):
        painel = self._painel_base("Turma e módulos", "#16a34a", "#f0fdf4")
        layout = painel.layout()

        self.combo_turma = QComboBox()
        self._preparar_campo(self.combo_turma)

        self.chk_todos_modulos = QCheckBox("Selecionar todos os módulos")
        self.chk_todos_modulos.stateChanged.connect(self.marcar_todos_modulos)
        self.chk_todos_modulos.setStyleSheet(self._checkbox_style())

        self.modulos_grid = QGridLayout()
        self.modulos_grid.setHorizontalSpacing(10)
        self.modulos_grid.setVerticalSpacing(6)

        layout.addWidget(self.combo_turma)
        layout.addWidget(self.chk_todos_modulos)
        layout.addLayout(self.modulos_grid)
        layout.addStretch()
        return painel

    def _criar_painel_tabela(self):
        painel = self._painel_base("Lista de alunos", "#7c3aed", "#f5f3ff")
        layout = painel.layout()

        self.tbl_alunos = QTableWidget(0, 9)
        self.tbl_alunos.setHorizontalHeaderLabels([
            "Nome",
            "Turma",
            "Pagamento",
            "Tel. aluno",
            "Status",
            "Nasc.",
            "Tel. resp.",
            "Módulo",
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
            texto_vagas = "vaga" if vagas == 1 else "vagas"
            texto = (
                f"{nome} - {dia} {horario} + {segundo_dia} {segundo_horario} "
                f"({vagas} {texto_vagas})"
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
            label.setStyleSheet("color: #64748b; font-size: 20px; font-weight: 700;")
            self.modulos_grid.addWidget(label, 0, 0)
            return

        for idx, modulo in enumerate(modulos):
            chk = QCheckBox(modulo[2])
            chk.setProperty("modulo_id", modulo[0])
            chk.setStyleSheet(self._checkbox_style())
            self.modulo_checks.append(chk)
            self.modulos_grid.addWidget(chk, idx // 2, idx % 2)

    def preencher_tabela(self, alunos):
        self.alunos_tabela = list(alunos)
        self.tbl_alunos.blockSignals(True)
        self.tbl_alunos.setRowCount(0)

        for row, aluno in enumerate(self.alunos_tabela):
            turma_txt = self._texto_turma(aluno.turma_id)
            status = self._status_aluno(aluno)
            data_pagamento = self._data_pagamento_texto(aluno.id)
            self.tbl_alunos.insertRow(row)
            self.tbl_alunos.setItem(row, 0, QTableWidgetItem(aluno.nome or ""))
            self.tbl_alunos.setItem(row, 1, QTableWidgetItem(turma_txt))
            self.tbl_alunos.setItem(row, 2, QTableWidgetItem(data_pagamento))
            self.tbl_alunos.setItem(row, 3, QTableWidgetItem(aluno.whatsapp_aluno or ""))
            self.tbl_alunos.setItem(row, 4, QTableWidgetItem(status))
            self.tbl_alunos.setItem(row, 5, QTableWidgetItem(aluno.nascimento or ""))
            self.tbl_alunos.setItem(row, 6, QTableWidgetItem(aluno.whatsapp_resp or ""))
            self.tbl_alunos.setItem(row, 7, QTableWidgetItem(aluno.modulo_atual or ""))
            self.tbl_alunos.setItem(row, 8, QTableWidgetItem(str(aluno.licao_atual or 1)))

        self.tbl_alunos.blockSignals(False)

    def filtrar_tabela(self):
        termo = self.txt_busca.text().strip().lower()
        if not termo:
            self.preencher_tabela(self.alunos)
            return

        filtrados = [
            aluno for aluno in self.alunos
            if termo in (aluno.nome or "").lower()
            or termo in (aluno.modulo_atual or "").lower()
        ]
        self.preencher_tabela(filtrados)

    def carregar_aluno_selecionado(self):
        row = self.tbl_alunos.currentRow()
        if row < 0 or row >= len(getattr(self, "alunos_tabela", [])):
            return

        aluno = self.alunos_tabela[row]

        self.aluno_em_edicao_id = aluno.id
        self.txt_nome.setText(aluno.nome or "")
        self.txt_nascimento.setText(aluno.nascimento or "")
        self._definir_data_pagamento(self.repo_financeiro.get_config(aluno.id)["data_primeiro_pagamento"])
        self.txt_whatsapp.setText(aluno.whatsapp_aluno or "")
        self.txt_whatsapp_resp.setText(aluno.whatsapp_resp or "")
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

        if self.aluno_em_edicao_id:
            aluno.id = self.aluno_em_edicao_id
            if not self._turma_tem_vaga_para_aluno(aluno):
                return
            self.repo.update(aluno)
            self._salvar_data_pagamento(aluno.id)
        else:
            if not self._turma_tem_vaga_para_aluno(aluno):
                return
            self.repo.add(aluno)
            self._salvar_data_pagamento(aluno.id)
        self.carregar_dados()

    def atualizar_aluno(self):
        if not self.aluno_em_edicao_id:
            QMessageBox.warning(self, "Aluno", "Selecione um aluno na tabela para editar.")
            return

        aluno = self._aluno_from_form()
        if not aluno:
            return
        aluno.id = self.aluno_em_edicao_id
        if not self._turma_tem_vaga_para_aluno(aluno):
            return
        self.repo.update(aluno)
        self._salvar_data_pagamento(aluno.id)
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
        self.txt_nascimento.clear()
        self._limpar_data_pagamento()
        self.txt_whatsapp.clear()
        self.txt_whatsapp_resp.clear()
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

        nascimento = self.txt_nascimento.text().strip()
        if "_" in nascimento or len(nascimento) != 10:
            QMessageBox.warning(self, "Nascimento", "Informe a data de nascimento no formato dd/mm/aaaa.")
            return None

        if not self._data_pagamento_atual():
            QMessageBox.warning(self, "Pagamento", "Selecione o dia do primeiro pagamento no calendario.")
            return None

        modulos_ids = [
            chk.property("modulo_id")
            for chk in self.modulo_checks
            if chk.isChecked()
        ]
        if not modulos_ids:
            QMessageBox.warning(self, "Módulos", "Escolha pelo menos um módulo para matricular o aluno.")
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
            "",
            nascimento,
        )
        aluno.licao_atual = 1
        aluno.modulo_atual = ", ".join(nomes_modulos)
        aluno.modulos_ids = modulos_ids
        aluno.turma_id = self.combo_turma.currentData()
        aluno.observacoes = self.txt_obs.toPlainText().strip()
        return aluno

    def _data_pagamento_texto(self, aluno_id):
        if not aluno_id:
            return "-"
        data = self.repo_financeiro.get_config(aluno_id)["data_primeiro_pagamento"]
        return data or "-"

    def _data_pagamento_atual(self):
        if not self.data_pagamento_selecionada:
            return ""
        return self.data_pagamento_selecionada.strftime("%d/%m/%Y")

    def _definir_data_pagamento(self, texto_data):
        try:
            data_pagamento = datetime.strptime(texto_data or "", "%d/%m/%Y").date()
        except ValueError:
            self._limpar_data_pagamento()
            return

        self.data_pagamento_selecionada = data_pagamento
        self.mes_pagamento = data_pagamento.month
        self.ano_pagamento = data_pagamento.year
        self._atualizar_calendario_pagamento()

    def _limpar_data_pagamento(self):
        hoje = date.today()
        self.data_pagamento_selecionada = None
        self.mes_pagamento = hoje.month
        self.ano_pagamento = hoje.year
        self._atualizar_calendario_pagamento()

    def _mudar_mes_pagamento(self, direcao):
        novo_mes = self.mes_pagamento + direcao
        if novo_mes < 1:
            self.mes_pagamento = 12
            self.ano_pagamento -= 1
        elif novo_mes > 12:
            self.mes_pagamento = 1
            self.ano_pagamento += 1
        else:
            self.mes_pagamento = novo_mes
        self._atualizar_calendario_pagamento()

    def _selecionar_dia_pagamento(self, dia):
        if not dia:
            return
        self.data_pagamento_selecionada = date(self.ano_pagamento, self.mes_pagamento, int(dia))
        self._atualizar_calendario_pagamento()

    def _atualizar_calendario_pagamento(self):
        if not hasattr(self, "lbl_mes_pagamento"):
            return

        nomes_meses = (
            "Janeiro",
            "Fevereiro",
            "Marco",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        )
        self.lbl_mes_pagamento.setText(f"{nomes_meses[self.mes_pagamento - 1]} {self.ano_pagamento}")

        primeiro_dia_semana, total_dias = monthrange(self.ano_pagamento, self.mes_pagamento)
        for indice, botao in enumerate(self.botoes_dia_pagamento):
            dia = indice - primeiro_dia_semana + 1
            if 1 <= dia <= total_dias:
                botao.setText(str(dia))
                botao.setProperty("dia", dia)
                botao.setEnabled(True)
                selecionado = (
                    self.data_pagamento_selecionada
                    and self.data_pagamento_selecionada.year == self.ano_pagamento
                    and self.data_pagamento_selecionada.month == self.mes_pagamento
                    and self.data_pagamento_selecionada.day == dia
                )
                botao.setStyleSheet(self._calendar_day_button_style(selecionado))
            else:
                botao.setText("")
                botao.setProperty("dia", None)
                botao.setEnabled(False)
                botao.setStyleSheet(self._calendar_empty_button_style())

        data_texto = self._data_pagamento_atual()
        if data_texto:
            self.lbl_pagamento_escolhido.setText(f"Primeiro pagamento: {data_texto}")
            if hasattr(self, "lbl_pagamento_resumo"):
                self.lbl_pagamento_resumo.setText(f"Pagamento: {data_texto}")
        else:
            self.lbl_pagamento_escolhido.setText("Selecione o dia do primeiro pagamento")
            if hasattr(self, "lbl_pagamento_resumo"):
                self.lbl_pagamento_resumo.setText("Pagamento: selecione a data")

    def _salvar_data_pagamento(self, aluno_id):
        config = self.repo_financeiro.get_config(aluno_id)
        data_pagamento = self._data_pagamento_atual()
        dia_vencimento = datetime.strptime(data_pagamento, "%d/%m/%Y").day
        self.repo_financeiro.salvar_config(
            aluno_id,
            data_pagamento,
            config["parcelas_pagas"],
            config["valor_mensalidade"],
            config["valor_atraso"],
            dia_vencimento,
            config["pix"],
        )

    def _turma_tem_vaga_para_aluno(self, aluno):
        if not aluno.turma_id:
            return True

        for turma in self.repo.get_turmas_com_vagas():
            turma_id = turma[0]
            nome = turma[1]
            capacidade = turma[8] or 8
            ocupadas = turma[9] or 0
            if turma_id != aluno.turma_id:
                continue

            if ocupadas < capacidade:
                return True

            if aluno.id:
                aluno_atual = next((item for item in self.repo.get_all() if item.id == aluno.id), None)
                if aluno_atual and aluno_atual.turma_id == aluno.turma_id:
                    return True

            QMessageBox.warning(
                self,
                "Turma sem vagas",
                f"A turma {nome} não possui vagas disponíveis.",
            )
            return False

        QMessageBox.warning(self, "Turma", "Selecione uma turma válida.")
        return False

    def _texto_turma(self, turma_id):
        if not turma_id:
            return "-"
        index = self.combo_turma.findData(turma_id)
        if index < 0:
            return "-"
        return self.combo_turma.itemText(index).split(" (")[0]

    def _status_aluno(self, aluno):
        modulo = (aluno.modulo_atual or "").strip().lower()
        if modulo == "curso concluído":
            return "Formado"
        if modulo == "trancado":
            return "Trancado"
        if self._aluno_inadimplente(aluno):
            return "Pendente"
        return "Matriculado"

    def _aluno_inadimplente(self, aluno):
        config = self.repo_financeiro.get_config(aluno.id)
        data_inicio = config["data_primeiro_pagamento"]
        if not data_inicio:
            return False

        try:
            inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        except ValueError:
            return False

        hoje = datetime.now()
        parcela_atual = ((hoje.year - inicio.year) * 12) + (hoje.month - inicio.month) + 1
        parcela_atual = max(1, min(parcela_atual, 14))
        return (config["parcelas_pagas"] or 0) < parcela_atual

    def _limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _painel_base(self, titulo, cor="#64748b", fundo_titulo="#f8fafc"):
        painel = QFrame()
        painel.setObjectName("painelBase")
        painel.setMinimumWidth(240)
        painel.setStyleSheet(f"""
            QFrame#painelBase {{
                background-color: white;
                border: 1px solid {cor};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(9)

        label = QLabel(titulo)
        label.setStyleSheet(f"""
            color: {cor};
            background-color: {fundo_titulo};
            border: none;
            border-left: 5px solid {cor};
            border-radius: 8px;
            padding: 7px 10px;
            font-size: 20px;
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

    def _label_campo(self, texto):
        label = QLabel(texto)
        label.setStyleSheet("color: #475569; font-size: 17px; font-weight: 800; border: none;")
        return label

    def _preparar_campo(self, campo):
        campo.setMinimumHeight(36)
        campo.setStyleSheet(self._input_style())

    def _preparar_tabela(self, tabela):
        tabela.setAlternatingRowColors(True)
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.verticalHeader().setVisible(False)
        tabela.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tabela.horizontalHeader().setStretchLastSection(False)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tabela.horizontalHeader().setMinimumSectionSize(72)
        larguras = (170, 285, 112, 120, 100, 88, 120, 145, 72)
        for coluna, largura in enumerate(larguras):
            tabela.setColumnWidth(coluna, largura)
        tabela.setColumnWidth(1, 290)
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
                padding: 8px 10px;
                font-weight: 800;
                font-size: 17px;
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

    def _checkbox_style(self):
        return "color: #334155; font-size: 20px; font-weight: 700;"

    def _text_edit_style(self):
        return """
            QTextEdit {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                padding: 8px 10px;
                font-size: 20px;
                font-weight: 600;
            }

            QTextEdit:focus {
                background-color: white;
                border-color: #3b82f6;
            }
        """

    def _calendar_nav_button_style(self):
        return """
            QPushButton {
                background-color: white;
                color: #0f766e;
                border: 1px solid #99f6e4;
                border-radius: 8px;
                font-size: 18px;
                font-weight: 900;
            }

            QPushButton:hover {
                background-color: #ccfbf1;
            }
        """

    def _calendar_open_button_style(self):
        return """
            QPushButton {
                background-color: #f0fdfa;
                color: #0f766e;
                border: 1px solid #99f6e4;
                border-radius: 9px;
                padding: 6px 10px;
                font-size: 16px;
                font-weight: 900;
            }

            QPushButton:hover {
                background-color: #ccfbf1;
            }
        """

    def _calendar_day_button_style(self, selecionado=False):
        if selecionado:
            return """
                QPushButton {
                    background-color: #0f766e;
                    color: white;
                    border: 1px solid #0f766e;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: 900;
                }
            """
        return """
            QPushButton {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: #ccfbf1;
                border-color: #5eead4;
            }
        """

    def _calendar_empty_button_style(self):
        return """
            QPushButton {
                background-color: transparent;
                color: transparent;
                border: none;
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
