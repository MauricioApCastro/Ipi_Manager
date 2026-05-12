from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class MaquinaCard(QFrame):
    def __init__(self, maquina_model, parent=None):
        super().__init__(parent)
        self.maquina = maquina_model # Aqui recebemos o Model Maquina
        self.setup_ui()

    def setup_ui(self):
        # Configuração visual do Frame (O Card)
        self.setFixedSize(220, 280)
        self.setObjectName("CardMaquina")
        self.setStyleSheet("""
            #CardMaquina {
                background-color: white; 
                border-radius: 15px; 
                border: 2px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Identificação (PC-01, etc)
        self.lbl_tag = QLabel(self.maquina.tag)
        self.lbl_tag.setStyleSheet("font-weight: bold; color: #64748b;")
        layout.addWidget(self.lbl_tag)
        
        layout.addStretch()
        
        # Status Central
        self.lbl_status = QLabel("VAGO")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 24px; font-weight: 900; color: #1e293b;")
        layout.addWidget(self.lbl_status)
        
        layout.addStretch()
        
        # Botão de Ação
        self.btn_acao = QPushButton("Alocar Aluno")
        self.btn_acao.setCursor(Qt.PointingHandCursor)
        self.btn_acao.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; 
                color: white; 
                border-radius: 8px; 
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        layout.addWidget(self.btn_acao)

    def atualizar_status(self, novo_status, aluno_nome=None):
        """Método para mudar a aparência se o PC for ocupado ou quebrar."""
        if novo_status == "OCUPADO":
            self.lbl_status.setText(aluno_nome.upper())
            self.setStyleSheet("#CardMaquina { background-color: #dcfce7; border: 2px solid #22c55e; }")
        elif novo_status == "DEFEITO":
            self.lbl_status.setText("MANUTENÇÃO")
            self.setStyleSheet("#CardMaquina { background-color: #fee2e2; border: 2px solid #ef4444; }")