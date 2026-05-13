from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt

class MaquinaCard(QFrame):
    solicitar_alocacao = pyqtSignal(object)

    def __init__(self, maquina):
        super().__init__()
        self.maquina = maquina
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(220, 200)
        self.setObjectName("MaquinaCard")
        self.layout = QVBoxLayout(self)

        # Tag da Máquina (ex: PC-01)
        self.lbl_tag = QLabel(self.maquina.tag)
        self.lbl_tag.setStyleSheet("font-weight: bold; font-size: 16px; color: #1e293b;")
        self.layout.addWidget(self.lbl_tag)

        # Status / Nome do Aluno
        self.lbl_status = QLabel(self.maquina.status)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
        self.layout.addWidget(self.lbl_status)

        # Informações Acadêmicas (Módulo e Aula)
        self.lbl_info_academica = QLabel("")
        self.lbl_info_academica.setStyleSheet("color: #475569; font-size: 12px;")
        self.lbl_info_academica.setAlignment(Qt.AlignCenter)
        self.lbl_info_academica.hide() 
        self.layout.addWidget(self.lbl_info_academica)

        # Campo de Observações
        self.txt_obs = QLineEdit()
        self.txt_obs.setPlaceholderText("Obs...")
        self.txt_obs.setStyleSheet("font-size: 11px; border: 1px solid #cbd5e1;")
        self.txt_obs.hide()
        self.layout.addWidget(self.txt_obs)

        # Botão de Ação
        self.btn_acao = QPushButton("Gerenciar")
        self.btn_acao.clicked.connect(lambda: self.solicitar_alocacao.emit(self))
        self.layout.addWidget(self.btn_acao)

        self.atualizar_estilo()

    def atualizar_status(self, novo_status, nome_aluno=None, info_aula=""):
        """
        Recebe o novo status, o nome e a string de Módulo/Aula.
        Agora aceita os 3 argumentos que a MainWindow está enviando.
        """
        self.maquina.status = novo_status
        self.maquina.ocupante = nome_aluno
        
        if novo_status == "OCUPADO":
            self.lbl_status.setText(nome_aluno)
            self.lbl_info_academica.setText(info_aula)
            self.lbl_info_academica.show()
            self.txt_obs.show()
        else:
            self.lbl_status.setText("VAGO")
            self.lbl_info_academica.hide()
            self.txt_obs.hide()
            self.txt_obs.clear()

        self.atualizar_estilo()

    def atualizar_estilo(self):
        if self.maquina.status == "OCUPADO":
            self.setStyleSheet("""
                #MaquinaCard { 
                    background-color: #dcfce7; 
                    border: 2px solid #22c55e; 
                    border-radius: 10px; 
                }
            """)
        else:
            self.setStyleSheet("""
                #MaquinaCard { 
                    background-color: white; 
                    border: 1px solid #cbd5e1; 
                    border-radius: 10px; 
                }
            """)