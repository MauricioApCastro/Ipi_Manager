from datetime import datetime
from urllib.parse import quote

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QGridLayout,
    QMessageBox,
    QScrollArea,
    QStackedWidget,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

from src.database.repositories import MaquinaRepository, AlunoRepository
from src.ui.components.maquina_card import MaquinaCard
from src.ui.components.seletor_aluno import SeletorAlunoDialog
from src.ui.windows.aluno_window import AlunoWindow
from src.ui.windows.curso_window import CursoWindow
from src.ui.windows.financeiro_window import FinanceiroWindow
from src.ui.windows.turma_window import TurmaWindow


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.repo_maquina = MaquinaRepository(self.db)
        self.repo_aluno = AlunoRepository(self.db)
        self.menu_buttons = {}
        self.setWindowTitle("IPI PRO - Gestão de Sala")
        self.resize(1280, 850)
        self.setMinimumSize(980, 680)
        self.setup_ui()
        self.carregar_maquinas()

    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f7fb;
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = self._criar_sidebar()
        self.main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()

        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f4f7fb;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(34, 30, 34, 28)
        self.content_layout.setSpacing(18)

        self._criar_header()
        self._criar_grid_maquinas()

        self.aluno_window = AlunoWindow(self.db)
        self.turma_window = TurmaWindow(self.db)
        self.curso_window = CursoWindow(self.db)
        self.financeiro_window = FinanceiroWindow(self.db)

        self.stack.addWidget(self.content_area)
        self.stack.addWidget(self.aluno_window)
        self.stack.addWidget(self.turma_window)
        self.stack.addWidget(self.curso_window)
        self.stack.addWidget(self.financeiro_window)
        self.main_layout.addWidget(self.stack)

        self.menu_buttons["Visão geral"].clicked.connect(lambda: self._trocar_tela(0, "Visão geral"))
        self.menu_buttons["Alunos"].clicked.connect(lambda: self._trocar_tela(1, "Alunos"))
        self.menu_buttons["Turmas"].clicked.connect(lambda: self._trocar_tela(2, "Turmas"))
        self.menu_buttons["Cursos"].clicked.connect(lambda: self._trocar_tela(3, "Cursos"))
        self.menu_buttons["Financeiro"].clicked.connect(lambda: self._trocar_tela(4, "Financeiro"))

    def _criar_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(248)
        sidebar.setObjectName("Sidebar")
        sidebar.setStyleSheet("""
            #Sidebar {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 1, y2: 1,
                    stop: 0 #0f172a,
                    stop: 1 #111827
                );
                border-right: 1px solid rgba(255, 255, 255, 0.07);
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 28, 20, 28)
        layout.setSpacing(8)

        logo = QLabel("IPI PRO")
        logo.setStyleSheet("""
            color: #f8fafc;
            font-size: 25px;
            font-weight: 900;
            padding: 0 6px 2px 6px;
        """)
        layout.addWidget(logo)

        subtitle = QLabel("Gestão de Sala")
        subtitle.setStyleSheet("""
            color: #94a3b8;
            font-size: 12px;
            font-weight: 600;
            padding: 0 6px 24px 6px;
        """)
        layout.addWidget(subtitle)

        menus = [
            ("Visão geral", True),
            ("Alunos", False),
            ("Turmas", False),
            ("Cursos", False),
            ("Financeiro", False),
            ("Relatórios", False),
        ]

        for nome, ativo in menus:
            btn = QPushButton(nome)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._sidebar_active_style() if ativo else self._sidebar_button_style())
            self.menu_buttons[nome] = btn
            layout.addWidget(btn)

        layout.addStretch()

        footer = QLabel("Sistema IPI")
        footer.setStyleSheet("""
            color: #64748b;
            font-size: 11px;
            font-weight: 600;
            padding: 12px 6px 0 6px;
        """)
        layout.addWidget(footer)

        return sidebar

    def _sidebar_button_style(self):
        return """
            QPushButton {
                color: #cbd5e1;
                text-align: left;
                padding: 13px 16px;
                border: none;
                border-radius: 12px;
                background: transparent;
                font-size: 14px;
                font-weight: 700;
            }

            QPushButton:hover {
                background-color: rgba(148, 163, 184, 0.12);
                color: #ffffff;
            }
        """

    def _sidebar_active_style(self):
        return self._sidebar_button_style() + """
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
            }
        """

    def _trocar_tela(self, index, menu_ativo):
        if menu_ativo == "Alunos":
            self.aluno_window.carregar_dados()
        if menu_ativo == "Turmas":
            self.turma_window.carregar_dados()
        if menu_ativo == "Financeiro":
            self.financeiro_window.carregar_dados()
        self.stack.setCurrentIndex(index)
        for nome, botao in self.menu_buttons.items():
            botao.setStyleSheet(
                self._sidebar_active_style()
                if nome == menu_ativo
                else self._sidebar_button_style()
            )

    def _criar_header(self):
        header = QHBoxLayout()
        header.setSpacing(18)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        self.lbl_titulo = QLabel("Painel de Máquinas")
        self.lbl_titulo.setStyleSheet("""
            color: #0f172a;
            font-size: 38px;
            font-weight: 900;
        """)

        title_box.addWidget(self.lbl_titulo)
        header.addLayout(title_box)
        header.addStretch()

        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.setCursor(Qt.PointingHandCursor)
        self.btn_atualizar.clicked.connect(self.carregar_maquinas)
        self.btn_atualizar.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 14px;
                padding: 12px 18px;
                font-size: 13px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #bfdbfe;
                color: #1d4ed8;
            }
        """)
        header.addWidget(self.btn_atualizar)

        self.content_layout.addLayout(header)

    def _criar_grid_maquinas(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")

        self.grid_maquinas = QGridLayout(self.grid_container)
        self.grid_maquinas.setContentsMargins(0, 8, 8, 18)
        self.grid_maquinas.setHorizontalSpacing(22)
        self.grid_maquinas.setVerticalSpacing(22)
        for coluna in range(4):
            self.grid_maquinas.setColumnStretch(coluna, 1)

        self.scroll_area.setWidget(self.grid_container)
        self.content_layout.addWidget(self.scroll_area)

    def carregar_maquinas(self):
        for i in reversed(range(self.grid_maquinas.count())):
            item = self.grid_maquinas.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        maquinas = self.repo_maquina.get_all()
        colunas = 4

        for idx, maq in enumerate(maquinas):
            card = MaquinaCard(maq)
            card.solicitar_alocacao.connect(self.abrir_gerenciamento)

            if maq.status == "OCUPADO":
                if maq.ocupante:
                    aluno = self.repo_aluno.get_by_name(maq.ocupante)
                    if aluno:
                        info = f"{aluno.modulo_atual} - Aula {aluno.licao_atual}"
                        card.atualizar_status("OCUPADO", maq.ocupante, info)
                        card.txt_obs.setText(aluno.observacoes or "")
                        self._conectar_salvar_obs(card)

            self.grid_maquinas.addWidget(card, idx // colunas, idx % colunas)

    def _conectar_salvar_obs(self, card):
        card.txt_obs.editingFinished.connect(
            lambda c=card: self.repo_aluno.salvar_observacao_aluno(
                c.maquina.ocupante,
                c.txt_obs.text(),
            )
        )

    def abrir_gerenciamento(self, card_que_pediu):
        if card_que_pediu.maquina.status == "OCUPADO":
            resposta = QMessageBox.question(
                self,
                "Finalizar Aula",
                f"O aluno {card_que_pediu.maquina.ocupante} concluiu a lição de hoje?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )

            if resposta == QMessageBox.Cancel:
                return

            if card_que_pediu.txt_obs.text():
                self.repo_aluno.salvar_observacao_aluno(
                    card_que_pediu.maquina.ocupante,
                    card_que_pediu.txt_obs.text(),
                )

            if resposta == QMessageBox.Yes:
                aluno_obj = self.repo_aluno.get_by_name(card_que_pediu.maquina.ocupante)
                if aluno_obj:
                    nova_licao = (aluno_obj.licao_atual or 1) + 1
                    self.repo_aluno.atualizar_progresso(aluno_obj.id, nova_licao)

            self.repo_maquina.finalizar_alocacao(card_que_pediu.maquina.tag)
            card_que_pediu.atualizar_status("VAGO")
            self.carregar_maquinas()
            return

        alunos_horario = self.repo_aluno.get_alunos_do_horario_atual()
        todos_alunos = self.repo_aluno.get_all()
        seletor = SeletorAlunoDialog(
            alunos_horario,
            todos_alunos,
            self,
            titulo_turma="Horário atual",
        )

        if seletor.exec_():
            nome_sel = seletor.aluno_selecionado
            aluno = self.repo_aluno.get_by_name(nome_sel)

            if aluno:
                for i in range(self.grid_maquinas.count()):
                    w = self.grid_maquinas.itemAt(i).widget()
                    if isinstance(w, MaquinaCard) and w.maquina.ocupante == nome_sel:
                        QMessageBox.warning(self, "Aviso", f"O aluno {nome_sel} já está alocado!")
                        return

                self.repo_maquina.salvar_alocacao(card_que_pediu.maquina.tag, nome_sel)
                self._registrar_presenca_e_notificar(aluno, card_que_pediu.maquina.tag)
                info_aula = f"{aluno.modulo_atual} - Aula {aluno.licao_atual}"
                card_que_pediu.atualizar_status("OCUPADO", nome_sel, info_aula)
                card_que_pediu.txt_obs.setText(aluno.observacoes or "")
                self._conectar_salvar_obs(card_que_pediu)
                self.carregar_maquinas()

    def _registrar_presenca_e_notificar(self, aluno, maquina_tag):
        data_hora = self.repo_aluno.registrar_presenca(aluno.id, maquina_tag)

        if not self._aluno_menor_de_idade(aluno):
            return

        telefone = self._normalizar_telefone(aluno.whatsapp_resp)
        if not telefone:
            QMessageBox.warning(
                self,
                "Responsável",
                f"{aluno.nome} é menor de idade, mas não possui WhatsApp do responsável cadastrado.",
            )
            return

        horario = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y às %H:%M")
        mensagem = (
            f"Olá! Informamos que {aluno.nome} registrou presença na aula da IPI Informática "
            f"em {horario}. Máquina: {maquina_tag}."
        )
        self.repo_aluno.registrar_mensagem_responsavel(aluno.id, telefone, mensagem)
        url = f"https://wa.me/55{telefone}?text={quote(mensagem)}"
        QDesktopServices.openUrl(QUrl(url))

    def _aluno_menor_de_idade(self, aluno):
        if not aluno.nascimento:
            return False
        try:
            nascimento = datetime.strptime(aluno.nascimento, "%d/%m/%Y").date()
        except ValueError:
            return False

        hoje = datetime.now().date()
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        return idade < 18

    def _normalizar_telefone(self, telefone):
        digitos = "".join(char for char in (telefone or "") if char.isdigit())
        if len(digitos) < 10:
            return ""
        return digitos[-11:]
