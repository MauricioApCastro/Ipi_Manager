from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal # Adicionamos pyqtSignal

class MaquinaCard(QFrame):
    # O Sinal que vai avisar a MainWindow
    solicitar_alocacao = pyqtSignal(object) 

    def __init__(self, maquina_model, parent=None):
        super().__init__(parent)
        self.maquina = maquina_model
        self.setup_ui()
        
        # Conecta o botão para emitir o sinal, não para abrir pop-up
        self.btn_acao.clicked.connect(self.emitir_sinal)

    def setup_ui(self):
        self.setFixedSize(220, 280)
        self.setObjectName("CardMaquina")
        self.setStyleSheet("#CardMaquina { background-color: white; border-radius: 15px; border: 2px solid #e2e8f0; }")
        
        layout = QVBoxLayout(self)
        self.lbl_tag = QLabel(self.maquina.tag)
        self.lbl_tag.setStyleSheet("font-weight: bold; color: #64748b;")
        layout.addWidget(self.lbl_tag)
        
        layout.addStretch()
        self.lbl_status = QLabel("VAGO")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 24px; font-weight: 900; color: #1e293b;")
        layout.addWidget(self.lbl_status)
        
        layout.addStretch()
        self.btn_acao = QPushButton("Alocar Aluno")
        self.btn_acao.setCursor(Qt.PointingHandCursor)
        self.btn_acao.setStyleSheet("""
            QPushButton { background-color: #0f172a; color: white; border-radius: 8px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #334155; }
        """)
        layout.addWidget(self.btn_acao)

    def emitir_sinal(self):
        # Apenas avisa: "Ei, alguém clicou em mim!"
        self.solicitar_alocacao.emit(self)

    def atualizar_status(self, novo_status, aluno_nome=None):
        if novo_status == "OCUPADO":
            self.lbl_status.setText(aluno_nome.upper())
            self.setStyleSheet("#CardMaquina { background-color: #dcfce7; border: 2px solid #22c55e; }")
            self.btn_acao.setText("Finalizar Aula")
        else:
            self.lbl_status.setText("VAGO")
            self.setStyleSheet("#CardMaquina { background-color: white; border: 2px solid #e2e8f0; }")
            self.btn_acao.setText("Alocar Aluno")