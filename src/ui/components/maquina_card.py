from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
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
        self.lbl_info_academica.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.lbl_info_academica.hide()
        self.layout.addWidget(self.lbl_info_academica)

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
        else:
            self.lbl_status.setText("VAGO")
            self.lbl_status.setToolTip("")
            self.lbl_badge.setText("LIVRE")
            self.lbl_info_academica.hide()

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
        self.btn_acao.setMinimumHeight(38 if compacto else 52)
        self._aplicar_estilo_tag()
        self._aplicar_estilo_status()
        self._aplicar_estilo_info_academica()
        self._aplicar_estilo_botao()
        self.atualizar_estilo()

    def _aplicar_estilo_status(self):
        texto = self.lbl_status.text() or ""
        if self.maquina.status == "OCUPADO":
            cor = "#0f172a"
            if len(texto) > 32:
                fonte = 18 if self.compacto else 23
            elif len(texto) > 24:
                fonte = 20 if self.compacto else 26
            else:
                fonte = 23 if self.compacto else 30
        else:
            cor = "#0f172a"
            fonte = 28 if self.compacto else 34

        self.lbl_status.setStyleSheet(f"""
            font-size: {fonte}px;
            font-weight: 800;
            color: {cor};
            margin-top: 6px;
            line-height: 1.05;
        """)

    def _aplicar_estilo_tag(self):
        fonte = 16 if self.compacto else 20
        padding = "5px 10px" if self.compacto else "8px 14px"
        fundo = "#fef2f2" if self.maquina.status == "OCUPADO" else "#f8fafc"
        cor = "#b91c1c" if self.maquina.status == "OCUPADO" else "#15803d"
        self.lbl_tag.setStyleSheet(f"""
            background-color: {fundo};
            color: {cor};
            padding: {padding};
            border-radius: 12px;
            font-size: {fonte}px;
            font-weight: 800;
        """)

    def _aplicar_estilo_info_academica(self):
        fonte = 14 if self.compacto else 18
        padding = "6px 8px" if self.compacto else "10px 12px"
        self.lbl_info_academica.setStyleSheet(f"""
            color: #b91c1c;
            font-size: {fonte}px;
            font-weight: 700;
            background: #fef2f2;
            border-radius: 10px;
            padding: {padding};
            line-height: 1.2;
        """)

    def _aplicar_estilo_botao(self):
        fonte = 16 if self.compacto else 20
        padding = "8px" if self.compacto else "16px"
        fundo = "#dc2626" if self.maquina.status == "OCUPADO" else "#2563eb"
        hover = "#b91c1c" if self.maquina.status == "OCUPADO" else "#1d4ed8"
        self.btn_acao.setStyleSheet(f"""
            QPushButton {{
                background-color: {fundo};
                color: white;
                border: none;
                border-radius: 14px;
                padding: {padding};
                font-weight: 800;
                font-size: {fonte}px;
            }}

            QPushButton:hover {{
                background-color: {hover};
            }}
        """)

    def atualizar_estilo(self):
        if self.maquina.status == "OCUPADO":
            self.shadow.setColor(QColor(220, 38, 38, 28))
            self.setStyleSheet("""
                #MaquinaCard {
                    background-color: white;
                    border: 1px solid #fecaca;
                    border-left: 6px solid #ef4444;
                    border-radius: 20px;
                }
            """)
            self.lbl_badge.setStyleSheet("""
                background-color: #fee2e2;
                color: #b91c1c;
                padding: %s;
                border-radius: 12px;
                font-size: %dpx;
                font-weight: 800;
            """ % ("5px 9px" if self.compacto else "6px 10px", 16 if self.compacto else 20))
            self.btn_acao.setText("Desocupar")
        else:
            self.shadow.setColor(QColor(15, 23, 42, 20))
            self.setStyleSheet("""
                #MaquinaCard {
                    background-color: #fbfefc;
                    border: 1px solid #d1fae5;
                    border-left: 6px solid #86efac;
                    border-radius: 20px;
                }
            """)
            self.lbl_badge.setStyleSheet("""
                background-color: #dcfce7;
                color: #047857;
                padding: %s;
                border-radius: 12px;
                font-size: %dpx;
                font-weight: 800;
            """ % ("5px 9px" if self.compacto else "6px 10px", 16 if self.compacto else 20))
            self.btn_acao.setText("Ocupar")

        self._aplicar_estilo_botao()
