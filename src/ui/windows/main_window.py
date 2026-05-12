from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QGridLayout,QMessageBox,QInputDialog
from src.database.repositories import MaquinaRepository,AlunoRepository
from src.ui.components.maquina_card import MaquinaCard
from src.ui.components.seletor_aluno import SeletorAlunoDialog

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.repo_maquina = MaquinaRepository(self.db)
        
        self.setWindowTitle("IPI PRO - Gestão de Sala")
        self.resize(1200, 800)
        
        self.setup_ui()
        self.carregar_maquinas()

    def setup_ui(self):
        # Widget Central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout Principal
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Sidebar (Menu Lateral)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #1e293b;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        logo = QLabel("IPI PRO")
        logo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin: 20px;")
        sidebar_layout.addWidget(logo)
        
        botoes = ["VISÃO GERAL", "ALUNOS", "CURSOS", "FINANCEIRO"]
        for nome in botoes:
            btn = QPushButton(nome)
            btn.setStyleSheet("""
                QPushButton { color: #cbd5e1; text-align: left; padding: 15px; border: none; font-weight: bold; }
                QPushButton:hover { background-color: #334155; color: white; }
            """)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar)

        # 2. Área de Conteúdo (Dashboard de Máquinas)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        
        self.lbl_titulo = QLabel("Painel de Máquinas")
        self.lbl_titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b; margin: 20px;")
        self.content_layout.addWidget(self.lbl_titulo)

        # Grid onde os cards ficarão
        self.grid_maquinas = QGridLayout()
        self.grid_maquinas.setSpacing(20)
        self.content_layout.addLayout(self.grid_maquinas)
        self.content_layout.addStretch()
        
        self.main_layout.addWidget(self.content_area)

    def carregar_maquinas(self):
        """Busca as máquinas no banco e as desenha na tela."""
        maquinas = self.repo_maquina.get_all()
        
        for i in reversed(range(self.grid_maquinas.count())): 
            self.grid_maquinas.itemAt(i).widget().setParent(None)

        for index, maq in enumerate(maquinas):
            card = MaquinaCard(maq)
            
            # CONEXÃO CRUCIAL: Aqui dizemos para o card usar a trava da MainWindow
            card.solicitar_alocacao.connect(self.processar_alocacao)
            
            self.grid_maquinas.addWidget(card, index // 4, index % 4)
            
    def processar_alocacao(self, card_que_pediu):
        """Lógica que roda quando o botão do card é clicado."""
        repo_aluno = AlunoRepository(self.db)
        alunos = repo_aluno.get_all()
        nomes = [aluno.nome for aluno in alunos]
        
        if not nomes:
            QMessageBox.warning(self, "Aviso", "Nenhum aluno no banco.")
            return

        nome_sel, ok = QInputDialog.getItem(
            self, "Alocação", 
            f"Aluno para {card_que_pediu.maquina.tag}:", 
            nomes, 0, False
        )

        if ok and nome_sel:
            nome_normalizado = nome_sel.strip().upper()
            
            # Trava de segurança visual
            ja_alocado = False
            for i in range(self.grid_maquinas.count()):
                widget = self.grid_maquinas.itemAt(i).widget()
                if isinstance(widget, MaquinaCard):
                    if widget.lbl_status.text().strip().upper() == nome_normalizado:
                        ja_alocado = True
                        break
            
            if ja_alocado:
                QMessageBox.warning(self, "Aviso", f"O aluno {nome_sel} já está ocupando uma máquina!")
                return 

            # --- PARTE NOVA: PERSISTÊNCIA NO BANCO ---
            # Aqui chamamos o repositório para gravar o ocupante
            self.repo_maquina.salvar_alocacao(card_que_pediu.maquina.tag, nome_sel)

            # Atualiza o visual
            card_que_pediu.atualizar_status("OCUPADO", nome_sel)
    
    def processar_alocacao(self, card_que_pediu):
        """Lógica com Seletor de Abas (Turma e Todos)."""
        repo_aluno = AlunoRepository(self.db)
        todos_alunos = repo_aluno.get_all()
        
        # Lógica de ADS: Por agora, simulamos a turma com os 5 primeiros.
        # No futuro, filtraremos pelo horário atual.
        alunos_turma = todos_alunos[:5] 

        # Abre a nossa nova janela customizada
        seletor = SeletorAlunoDialog(alunos_turma, todos_alunos, self)
        
        if seletor.exec_():
            nome_sel = seletor.aluno_selecionado
            nome_normalizado = nome_sel.strip().upper()
            
            # Trava de Duplicidade
            for i in range(self.grid_maquinas.count()):
                widget = self.grid_maquinas.itemAt(i).widget()
                if isinstance(widget, MaquinaCard):
                    if widget.lbl_status.text().strip().upper() == nome_normalizado:
                        QMessageBox.warning(self, "Bloqueio", f"{nome_sel} já está alocado!")
                        return

            # Se passar na trava, salva e atualiza o visual
            self.repo_maquina.salvar_alocacao(card_que_pediu.maquina.tag, nome_sel)
            card_que_pediu.atualizar_status("OCUPADO", nome_sel)