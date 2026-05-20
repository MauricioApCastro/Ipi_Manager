from datetime import datetime
from pathlib import Path
import shutil
import sqlite3
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
    QApplication,
    QFileDialog,
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QCursor, QDesktopServices

from src.database.repositories import MaquinaRepository, AlunoRepository, CursoRepository
from src.services.app_config import definir_config, obter_config
from src.ui.components.maquina_card import MaquinaCard
from src.ui.components.seletor_aluno import SeletorAlunoDialog
from src.ui.windows.aluno_window import AlunoWindow
from src.ui.windows.caixa_window import CaixaWindow
from src.ui.windows.config_window import ConfigWindow
from src.ui.windows.curso_window import CursoWindow
from src.ui.windows.financeiro_window import FinanceiroWindow
from src.ui.windows.frequencia_window import FrequenciaWindow
from src.ui.windows.turma_window import TurmaWindow


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.repo_maquina = MaquinaRepository(self.db)
        self.repo_aluno = AlunoRepository(self.db)
        self.repo_curso = CursoRepository(self.db)
        self.menu_buttons = {}
        self.maquina_cards = []
        self.setWindowTitle("IPI PRO - Gestão de Sala")
        self.monitor_disponivel = self._monitor_disponivel()
        self.compacto_monitor = self.monitor_disponivel.height() <= 760
        self.setMinimumSize(640, 480)
        self.resize(self.monitor_disponivel.size())
        self.setup_ui()
        self._configurar_backup_meio_dia()
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

        self.stack = QStackedWidget()

        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f4f7fb;")
        self.content_layout = QVBoxLayout(self.content_area)
        margem = 10 if self.compacto_monitor else 18
        self.content_layout.setContentsMargins(margem, margem, margem, margem)
        self.content_layout.setSpacing(8 if self.compacto_monitor else 12)

        self._criar_header()
        self._criar_grid_maquinas()

        self.aluno_window = AlunoWindow(self.db)
        self.turma_window = TurmaWindow(self.db)
        self.curso_window = CursoWindow(self.db)
        self.financeiro_window = FinanceiroWindow(self.db)
        self.caixa_window = CaixaWindow(self.db)
        self.frequencia_window = FrequenciaWindow(self.db)
        self.config_window = ConfigWindow(self.db)

        self.stack.addWidget(self.content_area)
        self.stack.addWidget(self.aluno_window)
        self.stack.addWidget(self.turma_window)
        self.stack.addWidget(self.curso_window)
        self.stack.addWidget(self.financeiro_window)
        self.stack.addWidget(self.caixa_window)
        self.stack.addWidget(self.frequencia_window)
        self.stack.addWidget(self.config_window)
        self.main_layout.addWidget(self.stack)

        self.sidebar = self._criar_sidebar()
        self.sidebar.setParent(self.central_widget)
        self._posicionar_sidebar()

        self.menu_buttons["Visão geral"].clicked.connect(lambda: self._trocar_tela(0, "Visão geral"))
        self.menu_buttons["Alunos"].clicked.connect(lambda: self._trocar_tela(1, "Alunos"))
        self.menu_buttons["Turmas"].clicked.connect(lambda: self._trocar_tela(2, "Turmas"))
        self.menu_buttons["Cursos"].clicked.connect(lambda: self._trocar_tela(3, "Cursos"))
        self.menu_buttons["Financeiro"].clicked.connect(lambda: self._trocar_tela(4, "Financeiro"))
        self.menu_buttons["Caixa"].clicked.connect(lambda: self._trocar_tela(5, "Caixa"))
        self.menu_buttons["Frequência"].clicked.connect(lambda: self._trocar_tela(6, "Frequência"))
        self.menu_buttons["Configuracoes"].clicked.connect(lambda: self._trocar_tela(7, "Configuracoes"))
        self.btn_backup.clicked.connect(self.fazer_backup)
        self._configurar_sidebar_retratil()

    def _configurar_backup_meio_dia(self):
        self.backup_diario_timer = QTimer(self)
        self.backup_diario_timer.setInterval(60_000)
        self.backup_diario_timer.timeout.connect(self._verificar_backup_meio_dia)
        self.backup_diario_timer.start()
        QTimer.singleShot(1000, self._verificar_backup_meio_dia)

    def _configurar_sidebar_retratil(self):
        self.sidebar_trigger_width = 12
        self.sidebar_hide_margin = 36
        self.sidebar.hide()

        self.sidebar_timer = QTimer(self)
        self.sidebar_timer.setInterval(90)
        self.sidebar_timer.timeout.connect(self._atualizar_sidebar_retratil)
        self.sidebar_timer.start()

    def _monitor_disponivel(self):
        tela = QApplication.primaryScreen()
        if tela:
            return tela.availableGeometry()
        return self.geometry()

    def _atualizar_sidebar_retratil(self):
        pos = self.mapFromGlobal(QCursor.pos())
        dentro_janela = self.rect().contains(pos)

        if not dentro_janela:
            self._ocultar_sidebar()
            return

        if pos.x() <= self.sidebar_trigger_width:
            self._mostrar_sidebar()
            return

        limite_sidebar = self.sidebar.width() + self.sidebar_hide_margin
        if self.sidebar.isVisible() and pos.x() > limite_sidebar:
            self._ocultar_sidebar()

    def _mostrar_sidebar(self):
        if not self.sidebar.isVisible():
            self._posicionar_sidebar()
            self.sidebar.show()
            self.sidebar.raise_()

    def _ocultar_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()

    def _posicionar_sidebar(self):
        self.sidebar.setGeometry(0, 0, self.sidebar.width(), self.central_widget.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "sidebar"):
            self._posicionar_sidebar()
        if hasattr(self, "maquina_cards") and self.stack.currentIndex() == 0:
            self._reposicionar_maquinas()

    def closeEvent(self, event):
        try:
            self._backup_automatico()
        except Exception:
            pass
        super().closeEvent(event)

    def _criar_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
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
        layout.setContentsMargins(22, 28, 22, 28)
        layout.setSpacing(10)

        logo = QLabel("IPI PRO")
        logo.setStyleSheet("""
            color: #f8fafc;
            font-size: 33px;
            font-weight: 900;
            padding: 0 6px 2px 6px;
        """)
        layout.addWidget(logo)

        subtitle = QLabel("Gestão de Sala")
        subtitle.setStyleSheet("""
            color: #94a3b8;
            font-size: 20px;
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
            ("Caixa", False),
            ("Frequência", False),
        ]

        for nome, ativo in menus:
            btn = QPushButton(nome)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._sidebar_active_style() if ativo else self._sidebar_button_style())
            self.menu_buttons[nome] = btn
            layout.addWidget(btn)

        for nome in ("Configuracoes",):
            btn = QPushButton(nome)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._sidebar_button_style())
            self.menu_buttons[nome] = btn
            layout.addWidget(btn)

        layout.addStretch()

        self.btn_backup = QPushButton("Backup")
        self.btn_backup.setCursor(Qt.PointingHandCursor)
        self.btn_backup.setStyleSheet(self._sidebar_backup_style())
        layout.addWidget(self.btn_backup)

        footer = QLabel("Sistema IPI")
        footer.setStyleSheet("""
            color: #64748b;
            font-size: 20px;
            font-weight: 600;
            padding: 12px 6px 0 6px;
        """)
        layout.addWidget(footer)

        return sidebar

    def fazer_backup(self):
        destino_base = QFileDialog.getExistingDirectory(
            self,
            "Escolher pasta para o backup",
            str(Path.home()),
        )
        if not destino_base:
            return

        try:
            pasta_backup = self._criar_backup(Path(destino_base))
        except Exception as exc:
            QMessageBox.critical(self, "Backup", f"NÃ£o foi possÃ­vel fazer o backup:\n{exc}")
            return

        QMessageBox.information(
            self,
            "Backup",
            f"Backup concluÃ­do com sucesso:\n{pasta_backup}",
        )

    def _criar_backup(self, destino_base):
        db_path = Path(getattr(self.db, "db_path", "data/escola.db")).resolve()
        if not db_path.exists():
            raise FileNotFoundError(f"Banco de dados nÃ£o encontrado: {db_path}")

        pasta_backup = destino_base / f"backup_ipi_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pasta_backup.mkdir(parents=True, exist_ok=False)

        self._backup_sqlite(db_path, pasta_backup / "escola.db")

        recibos_origem = db_path.parent.parent / "recibos"
        if recibos_origem.exists():
            shutil.copytree(recibos_origem, pasta_backup / "recibos")

        return pasta_backup

    def _backup_sqlite(self, origem, destino):
        with sqlite3.connect(str(origem)) as conn_origem:
            with sqlite3.connect(str(destino)) as conn_destino:
                conn_origem.backup(conn_destino)

    def _backup_automatico(self):
        db_path = Path(getattr(self.db, "db_path", "data/escola.db")).resolve()
        destino = db_path.parent.parent / "backups"
        destino.mkdir(parents=True, exist_ok=True)
        self._criar_backup(destino)
        backups = sorted(destino.glob("backup_ipi_manager_*"), key=lambda item: item.stat().st_mtime, reverse=True)
        for antigo in backups[7:]:
            if antigo.is_dir():
                shutil.rmtree(antigo)

    def _verificar_backup_meio_dia(self):
        agora = datetime.now()
        if agora.hour != 12:
            return

        hoje = agora.strftime("%Y-%m-%d")
        if obter_config(self.db, "ultimo_backup_meio_dia", "") == hoje:
            return

        try:
            self._executar_backup_meio_dia()
            definir_config(self.db, "ultimo_backup_meio_dia", hoje)
        except Exception as exc:
            definir_config(self.db, "ultimo_erro_backup_meio_dia", f"{agora:%d/%m/%Y %H:%M}: {exc}")

    def _executar_backup_meio_dia(self):
        db_path = Path(getattr(self.db, "db_path", "data/escola.db")).resolve()
        destino_pc = db_path.parent.parent / "backups"
        destino_pc.mkdir(parents=True, exist_ok=True)
        self._criar_backup(destino_pc)
        self._limpar_backups_antigos(destino_pc)

        pasta_nuvem = obter_config(self.db, "backup_nuvem_path", "").strip()
        if pasta_nuvem:
            destino_nuvem = Path(pasta_nuvem)
            destino_nuvem.mkdir(parents=True, exist_ok=True)
            self._criar_backup(destino_nuvem)
            self._limpar_backups_antigos(destino_nuvem)

    def _limpar_backups_antigos(self, destino):
        backups = sorted(destino.glob("backup_ipi_manager_*"), key=lambda item: item.stat().st_mtime, reverse=True)
        for antigo in backups[7:]:
            if antigo.is_dir():
                shutil.rmtree(antigo)

    def _sidebar_button_style(self):
        return """
            QPushButton {
                color: #cbd5e1;
                text-align: left;
                padding: 16px 18px;
                border: none;
                border-radius: 12px;
                background: transparent;
                font-size: 20px;
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

    def _sidebar_backup_style(self):
        return """
            QPushButton {
                color: #f8fafc;
                text-align: left;
                padding: 14px 18px;
                border: 1px solid rgba(34, 197, 94, 0.35);
                border-radius: 12px;
                background-color: rgba(22, 163, 74, 0.18);
                font-size: 20px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: rgba(22, 163, 74, 0.32);
            }
        """

    def _trocar_tela(self, index, menu_ativo):
        if menu_ativo == "Alunos":
            self.aluno_window.carregar_dados()
        if menu_ativo == "Turmas":
            self.turma_window.carregar_dados()
        if menu_ativo == "Financeiro":
            self.financeiro_window.carregar_dados()
        if menu_ativo == "Caixa":
            self.caixa_window.carregar_dados()
        if menu_ativo == "Configuracoes":
            self.config_window.carregar_dados()
        if menu_ativo == "Frequência":
            self.frequencia_window.carregar_dados()
        self.stack.setCurrentIndex(index)
        for nome, botao in self.menu_buttons.items():
            botao.setStyleSheet(
                self._sidebar_active_style()
                if nome == menu_ativo
                else self._sidebar_button_style()
            )

    def _criar_header(self):
        header = QHBoxLayout()
        header.setSpacing(10 if self.compacto_monitor else 14)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        self.lbl_titulo = QLabel("Painel de Máquinas")
        self.lbl_titulo.setStyleSheet("""
            color: #0f172a;
            font-size: 34px;
            font-weight: 900;
        """)

        title_box.addWidget(self.lbl_titulo)
        header.addLayout(title_box)
        header.addStretch()

        self.content_layout.addLayout(header)

    def _criar_grid_maquinas(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        self.grid_maquinas.setHorizontalSpacing(18)
        self.grid_maquinas.setVerticalSpacing(18)
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

        self.maquina_cards = []
        maquinas = self.repo_maquina.get_all()

        for maq in maquinas:
            card = MaquinaCard(maq)
            card.solicitar_alocacao.connect(self.abrir_gerenciamento)

            if maq.status == "OCUPADO":
                if maq.ocupante:
                    aluno = self.repo_aluno.get_by_name(maq.ocupante)
                    if aluno:
                        info = self._texto_aula_card(aluno)
                        card.atualizar_status("OCUPADO", maq.ocupante, info)
                        card.txt_obs.setText(aluno.observacoes or "")
                        self._conectar_salvar_obs(card)

            self.maquina_cards.append(card)

        self._reposicionar_maquinas()

    def _layout_maquinas(self):
        largura = self.scroll_area.viewport().width()
        altura = self.scroll_area.viewport().height()
        total = max(len(self.maquina_cards), 1)
        espacamento = self.grid_maquinas.horizontalSpacing()
        margem_horizontal = 8
        margem_vertical = 26
        candidatos = []

        for colunas in range(min(4, total), 0, -1):
            largura_card = (largura - margem_horizontal - (colunas - 1) * espacamento) / colunas
            if largura_card < 200:
                continue

            linhas = (total + colunas - 1) // colunas
            altura_card = (altura - margem_vertical - (linhas - 1) * espacamento) / linhas
            candidatos.append((colunas, int(altura_card)))

        if candidatos:
            colunas, altura_card = candidatos[0]
        else:
            colunas = 1
            altura_card = int((altura - margem_vertical - (total - 1) * espacamento) / total)

        altura_card = max(180, min(330, altura_card))
        compacto = altura_card < 270 or self.monitor_disponivel.height() < 760
        return colunas, altura_card, compacto

    def _reposicionar_maquinas(self):
        while self.grid_maquinas.count():
            item = self.grid_maquinas.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        colunas, altura_card, compacto = self._layout_maquinas()
        for coluna in range(4):
            self.grid_maquinas.setColumnStretch(coluna, 1 if coluna < colunas else 0)

        for idx, card in enumerate(self.maquina_cards):
            card.ajustar_para_monitor(altura_card, compacto)
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
            dialogo = QMessageBox(self)
            dialogo.setWindowTitle("Finalizar Aula")
            dialogo.setText(f"O aluno {card_que_pediu.maquina.ocupante} concluiu a lição de hoje?")
            dialogo.setIcon(QMessageBox.Question)
            botao_sim = dialogo.addButton("Sim", QMessageBox.YesRole)
            dialogo.addButton("Não", QMessageBox.NoRole)
            botao_cancelar = dialogo.addButton("Cancelar", QMessageBox.RejectRole)
            dialogo.setDefaultButton(botao_sim)
            dialogo.exec_()
            resposta = dialogo.clickedButton()

            if resposta == botao_cancelar:
                return

            if card_que_pediu.txt_obs.text():
                self.repo_aluno.salvar_observacao_aluno(
                    card_que_pediu.maquina.ocupante,
                    card_que_pediu.txt_obs.text(),
                )

            if resposta == botao_sim:
                aluno_obj = self.repo_aluno.get_by_name(card_que_pediu.maquina.ocupante)
                if aluno_obj:
                    nova_licao, novo_modulo, curso_concluido = self._proximo_passo_aluno(aluno_obj)
                    if curso_concluido:
                        self.repo_aluno.concluir_curso(aluno_obj.id)
                        QMessageBox.information(self, "Curso", f"{aluno_obj.nome} concluiu o curso.")
                    else:
                        self.repo_aluno.atualizar_progresso(aluno_obj.id, nova_licao, novo_modulo)

            self.repo_maquina.finalizar_alocacao(card_que_pediu.maquina.tag)
            card_que_pediu.atualizar_status("VAGO")
            self.carregar_maquinas()
            return

        alunos_horario = self.repo_aluno.get_alunos_do_horario_atual()
        alunos_horario = [aluno for aluno in alunos_horario if not self._curso_concluido(aluno)]
        todos_alunos = [
            aluno for aluno in self.repo_aluno.get_all()
            if not self._curso_concluido(aluno)
        ]
        turmas_hoje = self._turmas_hoje_para_seletor()
        seletor = SeletorAlunoDialog(
            alunos_horario,
            todos_alunos,
            self,
            titulo_turma="Horário atual",
            turmas_hoje=turmas_hoje,
        )

        if seletor.exec_():
            nome_sel = seletor.aluno_selecionado
            aluno = self.repo_aluno.get_by_name(nome_sel)

            if aluno:
                if self._curso_concluido(aluno):
                    QMessageBox.warning(
                        self,
                        "Curso concluído",
                        f"{aluno.nome} já concluiu o curso e não pode ocupar uma máquina.",
                    )
                    return

                for i in range(self.grid_maquinas.count()):
                    w = self.grid_maquinas.itemAt(i).widget()
                    if isinstance(w, MaquinaCard) and w.maquina.ocupante == nome_sel:
                        QMessageBox.warning(self, "Aviso", f"O aluno {nome_sel} já está alocado!")
                        return

                self.repo_maquina.salvar_alocacao(card_que_pediu.maquina.tag, nome_sel)
                self._registrar_presenca_e_notificar(aluno, card_que_pediu.maquina.tag)
                info_aula = self._texto_aula_card(aluno)
                card_que_pediu.atualizar_status("OCUPADO", nome_sel, info_aula)
                card_que_pediu.txt_obs.setText(aluno.observacoes or "")
                self._conectar_salvar_obs(card_que_pediu)
                self.carregar_maquinas()

    def _turmas_hoje_para_seletor(self):
        turmas_hoje = []
        for horario, turma, alunos in self.repo_aluno.get_turmas_do_dia_com_alunos():
            alunos_ativos = [
                aluno for aluno in alunos
                if not self._curso_concluido(aluno)
            ]
            turmas_hoje.append((horario, turma, alunos_ativos))
        return turmas_hoje

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

    def _texto_aula_card(self, aluno):
        if self._curso_concluido(aluno):
            return "Curso concluído"

        modulo = (aluno.modulo_atual or "").split(",")[0].strip() or "Módulo"
        licao = self._licao_visivel(aluno, modulo)
        abreviacoes = {
            "windows": "Win",
            "word": "Word",
            "excel": "Excel",
            "powerpoint": "Ppt",
            "internet": "Net",
        }
        chave = modulo.lower()
        aula_nome = abreviacoes.get(chave, modulo[:3].title())
        return f"{modulo}, Aula {aula_nome} {licao}"

    def _curso_concluido(self, aluno):
        return (aluno.modulo_atual or "").strip().lower() == "curso concluído"

    def _proximo_passo_aluno(self, aluno):
        modulo_atual = (aluno.modulo_atual or "").split(",")[0].strip()
        modulos_ids = aluno.modulos_ids or []

        if not modulo_atual or not modulos_ids:
            return aluno.licao_atual or 1, None, True

        modulos = self._modulos_do_aluno_ordenados(modulos_ids)

        indice_atual = next(
            (idx for idx, modulo in enumerate(modulos) if modulo[2] == modulo_atual),
            -1,
        )
        if indice_atual < 0:
            return aluno.licao_atual or 1, None, True

        modulo_id = modulos[indice_atual][0]
        total_aulas = len(self.repo_curso.get_aulas_modulo(modulo_id))
        licao_atual = aluno.licao_atual or 1

        if total_aulas and licao_atual < total_aulas:
            return licao_atual + 1, modulo_atual, False

        for proximo_modulo in modulos[indice_atual + 1:]:
            if self.repo_curso.get_aulas_modulo(proximo_modulo[0]):
                return 1, proximo_modulo[2], False

        return licao_atual, modulo_atual, True

    def _modulos_do_aluno_ordenados(self, modulos_ids):
        modulos = [
            modulo for modulo in self.repo_curso.get_all_modulos()
            if modulo[0] in modulos_ids
        ]
        modulos.sort(key=lambda modulo: (modulo[3] or 0, modulo[0]))
        return modulos

    def _licao_visivel(self, aluno, modulo_nome):
        licao = aluno.licao_atual or 1
        for modulo in self._modulos_do_aluno_ordenados(aluno.modulos_ids or []):
            if modulo[2] != modulo_nome:
                continue
            total_aulas = len(self.repo_curso.get_aulas_modulo(modulo[0]))
            if total_aulas:
                return min(licao, total_aulas)
        return licao

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
