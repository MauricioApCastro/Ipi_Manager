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
        self.compacto = False
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumSize(200, 260)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setObjectName("MaquinaCard")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 14, 16, 14)
        self.layout.setSpacing(9)

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
        self._aplicar_estilo_tag()

        self.lbl_badge = QLabel("LIVRE")
        self.lbl_badge.setAlignment(Qt.AlignCenter)

        header.addWidget(self.lbl_tag)
        header.addStretch()
        header.addWidget(self.lbl_badge)
        self.layout.addLayout(header)

        self.lbl_status = QLabel(self.maquina.status)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_status.setMinimumHeight(72)
        self.lbl_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._aplicar_estilo_status()
        self.layout.addWidget(self.lbl_status)

        self.lbl_info_academica = QLabel("")
        self.lbl_info_academica.setWordWrap(True)
        self.lbl_info_academica.setMinimumHeight(58)
        self.lbl_info_academica.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._aplicar_estilo_info_academica()
        self.lbl_info_academica.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_info_academica.hide()
        self.layout.addWidget(self.lbl_info_academica)

        self.txt_obs = QLineEdit()
        self.txt_obs.setPlaceholderText("Anotacoes da aula...")
        self.txt_obs.setMinimumHeight(38)
        self._aplicar_estilo_observacao()
        self.txt_obs.hide()
        self.layout.addWidget(self.txt_obs)

        self.layout.addStretch()

        self.btn_acao = QPushButton("Ocupar")
        self.btn_acao.setCursor(Qt.PointingHandCursor)
        self._aplicar_estilo_botao()
        self.btn_acao.clicked.connect(lambda: self.solicitar_alocacao.emit(self))
        self.layout.addWidget(self.btn_acao)

        self.atualizar_estilo()

    def atualizar_status(self, novo_status, nome_aluno=None, info_aula=""):
        self.maquina.status = novo_status
        self.maquina.ocupante = nome_aluno

        if novo_status == "OCUPADO":
            self.lbl_status.setText(nome_aluno)
            self.lbl_status.setToolTip(nome_aluno or "")
            self.lbl_badge.setText("OCUPADA")
            self.lbl_info_academica.setText(info_aula)
            self.lbl_info_academica.show()
            self.txt_obs.show()
        else:
            self.lbl_status.setText("VAGO")
            self.lbl_status.setToolTip("")
            self.lbl_badge.setText("LIVRE")
            self.lbl_info_academica.hide()
            self.txt_obs.hide()
            self.txt_obs.clear()

        self._aplicar_estilo_status()
        self.atualizar_estilo()

    def ajustar_para_monitor(self, altura, compacto=False):
        self.compacto = compacto
        self.setMinimumHeight(max(180, altura))
        self.setMaximumHeight(max(180, altura))
        margens = (10, 8, 10, 8) if compacto else (16, 14, 16, 14)
        self.layout.setContentsMargins(*margens)
        self.layout.setSpacing(5 if compacto else 9)
        self.lbl_status.setMinimumHeight(34 if compacto else 72)
        self.lbl_info_academica.setMinimumHeight(58 if compacto else 58)
        self.lbl_info_academica.setMaximumHeight(66 if compacto else 92)
        self.txt_obs.setMinimumHeight(34 if compacto else 44)
        self.btn_acao.setMinimumHeight(38 if compacto else 52)
        self._aplicar_estilo_tag()
        self._aplicar_estilo_status()
        self._aplicar_estilo_info_academica()
        self._aplicar_estilo_observacao()
        self._aplicar_estilo_botao()
        self.atualizar_estilo()

    def _aplicar_estilo_status(self):
        texto = self.lbl_status.text() or ""
        if self.maquina.status == "OCUPADO":
            if len(texto) > 32:
                fonte = 18 if self.compacto else 23
            elif len(texto) > 24:
                fonte = 20 if self.compacto else 26
            else:
                fonte = 23 if self.compacto else 30
        else:
            fonte = 28 if self.compacto else 34

        self.lbl_status.setStyleSheet(f"""
            font-size: {fonte}px;
            font-weight: 800;
            color: #0f172a;
            margin-top: 6px;
            line-height: 1.05;
        """)

    def _aplicar_estilo_tag(self):
        fonte = 16 if self.compacto else 20
        padding = "5px 10px" if self.compacto else "8px 14px"
        self.lbl_tag.setStyleSheet(f"""
            background-color: #eff6ff;
            color: #2563eb;
            padding: {padding};
            border-radius: 12px;
            font-size: {fonte}px;
            font-weight: 800;
        """)

    def _aplicar_estilo_info_academica(self):
        fonte = 14 if self.compacto else 20
        padding = "5px 8px" if self.compacto else "10px 12px"
        self.lbl_info_academica.setStyleSheet(f"""
            color: #2563eb;
            font-size: {fonte}px;
            font-weight: 700;
            background: #eff6ff;
            border-radius: 10px;
            padding: {padding};
        """)

    def _aplicar_estilo_observacao(self):
        fonte = 15 if self.compacto else 20
        padding = "6px 9px" if self.compacto else "12px 14px"
        self.txt_obs.setStyleSheet(f"""
            QLineEdit {{
                font-size: {fonte}px;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 12px;
                padding: {padding};
                background: #f8fafc;
            }}

            QLineEdit:focus {{
                border: 1px solid #3b82f6;
                background: white;
            }}
        """)

    def _aplicar_estilo_botao(self):
        fonte = 16 if self.compacto else 20
        padding = "8px" if self.compacto else "16px"
        self.btn_acao.setStyleSheet(f"""
            QPushButton {{
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 14px;
                padding: {padding};
                font-weight: 800;
                font-size: {fonte}px;
            }}

            QPushButton:hover {{
                background-color: #1d4ed8;
            }}
        """)

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
                padding: %s;
                border-radius: 12px;
                font-size: %dpx;
                font-weight: 800;
            """ % ("5px 9px" if self.compacto else "6px 10px", 16 if self.compacto else 20))
            self.btn_acao.setText("Desocupar")
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
                padding: %s;
                border-radius: 12px;
                font-size: %dpx;
                font-weight: 800;
            """ % ("5px 9px" if self.compacto else "6px 10px", 16 if self.compacto else 20))
            self.btn_acao.setText("Ocupar")
