from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor


class MaquinaCard(QFrame):
    solicitar_alocacao = pyqtSignal(object)

    def __init__(self, maquina):
        super().__init__()
        self.maquina = maquina
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumSize(220, 235)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setObjectName("MaquinaCard")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 18, 18, 18)
        self.layout.setSpacing(12)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(28)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(12)
        self.shadow.setColor(QColor(15, 23, 42, 24))
        self.setGraphicsEffect(self.shadow)

        header = QHBoxLayout()
        header.setSpacing(8)

        self.lbl_tag = QLabel(self.maquina.tag)
        self.lbl_tag.setAlignment(Qt.AlignCenter)
        self.lbl_tag.setStyleSheet("""
            background-color: #eff6ff;
            color: #2563eb;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 800;
        """)

        self.lbl_badge = QLabel("LIVRE")
        self.lbl_badge.setAlignment(Qt.AlignCenter)

        header.addWidget(self.lbl_tag)
        header.addStretch()
        header.addWidget(self.lbl_badge)
        self.layout.addLayout(header)

        self.lbl_status = QLabel(self.maquina.status)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_status.setStyleSheet("""
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
            margin-top: 6px;
        """)
        self.layout.addWidget(self.lbl_status)

        self.lbl_info_academica = QLabel("")
        self.lbl_info_academica.setStyleSheet("""
            color: #2563eb;
            font-size: 12px;
            font-weight: 700;
            background: #eff6ff;
            border-radius: 10px;
            padding: 7px 10px;
        """)
        self.lbl_info_academica.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_info_academica.hide()
        self.layout.addWidget(self.lbl_info_academica)

        self.txt_obs = QLineEdit()
        self.txt_obs.setPlaceholderText("Anotacoes da aula...")
        self.txt_obs.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 12px;
                padding: 10px 12px;
                background: #f8fafc;
            }

            QLineEdit:focus {
                border: 1px solid #3b82f6;
                background: white;
            }
        """)
        self.txt_obs.hide()
        self.layout.addWidget(self.txt_obs)

        self.layout.addStretch()

        self.btn_acao = QPushButton("Alocar aluno")
        self.btn_acao.setCursor(Qt.PointingHandCursor)
        self.btn_acao.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 13px;
                font-weight: 800;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_acao.clicked.connect(lambda: self.solicitar_alocacao.emit(self))
        self.layout.addWidget(self.btn_acao)

        self.atualizar_estilo()

    def atualizar_status(self, novo_status, nome_aluno=None, info_aula=""):
        self.maquina.status = novo_status
        self.maquina.ocupante = nome_aluno

        if novo_status == "OCUPADO":
            self.lbl_status.setText(nome_aluno)
            self.lbl_badge.setText("OCUPADA")
            self.lbl_info_academica.setText(info_aula)
            self.lbl_info_academica.show()
            self.txt_obs.show()
        else:
            self.lbl_status.setText("VAGO")
            self.lbl_badge.setText("LIVRE")
            self.lbl_info_academica.hide()
            self.txt_obs.hide()
            self.txt_obs.clear()

        self.atualizar_estilo()

    def atualizar_estilo(self):
        if self.maquina.status == "OCUPADO":
            self.setStyleSheet("""
                #MaquinaCard {
                    background-color: white;
                    border: 1px solid #bfdbfe;
                    border-radius: 20px;
                }
            """)
            self.lbl_badge.setStyleSheet("""
                background-color: #dbeafe;
                color: #1d4ed8;
                padding: 6px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 800;
            """)
            self.btn_acao.setText("Liberar / editar")
        else:
            self.setStyleSheet("""
                #MaquinaCard {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 20px;
                }
            """)
            self.lbl_badge.setStyleSheet("""
                background-color: #dcfce7;
                color: #15803d;
                padding: 6px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 800;
            """)
            self.btn_acao.setText("Alocar aluno")
