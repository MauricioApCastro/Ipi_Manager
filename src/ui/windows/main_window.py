from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QGridLayout
from src.database.repositories import MaquinaRepository
from src.ui.components.maquina_card import MaquinaCard

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
        
        # Limpa o grid se houver algo (bom para atualizações)
        for i in reversed(range(self.grid_maquinas.count())): 
            self.grid_maquinas.itemAt(i).widget().setParent(None)

        # Adiciona os cards no grid (2 linhas de 4)
        for index, maq in enumerate(maquinas):
            card = MaquinaCard(maq)
            self.grid_maquinas.addWidget(card, index // 4, index % 4)