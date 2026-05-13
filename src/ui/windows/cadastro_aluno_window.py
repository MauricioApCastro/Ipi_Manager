from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QDateEdit, QFormLayout)
from PyQt5.QtCore import QDate, Qt

class CadastroAlunoWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Novo Aluno")
        self.setFixedSize(680, 760)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(38, 38, 38, 38)

        titulo = QLabel("Novo Aluno")
        titulo.setStyleSheet("font-size: 32px; font-weight: 800; color: #0f172a; margin-bottom: 20px;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(20)

        # Campos de Texto Estilizados
        self.txt_nome = self._criar_input("Nome Completo")
        self.txt_cpf = self._criar_input("000.000.000-00")
        self.txt_whatsapp = self._criar_input("(11) 90000-0000")
        self.txt_whatsapp_resp = self._criar_input("(11) 90000-0000 (Obrigatório para menores)")
        
        # Campo de Data (Essencial para a lógica de menor de idade)
        self.date_nascimento = QDateEdit()
        self.date_nascimento.setCalendarPopup(True)
        self.date_nascimento.setDate(QDate.currentDate().addYears(-10))
        self.date_nascimento.setStyleSheet("""
            QDateEdit { font-size: 20px; padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; background: white; }
        """)

        form.addRow("Nome:", self.txt_nome)
        form.addRow("Nascimento:", self.date_nascimento)
        form.addRow("CPF:", self.txt_cpf)
        form.addRow("WhatsApp Aluno:", self.txt_whatsapp)
        form.addRow("WhatsApp Resp.:", self.txt_whatsapp_resp)

        layout.addLayout(form)
        layout.addStretch()

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_salvar = QPushButton("Salvar Cadastro")
        
        self.btn_salvar.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; font-size: 20px; font-weight: bold; padding: 16px; border-radius: 6px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        self.btn_cancelar.setStyleSheet("font-size: 20px; padding: 16px; border: none; color: #64748b;")

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_salvar)
        layout.addLayout(btn_layout)

        # Conexões
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_salvar.clicked.connect(self.accept)

    def _criar_input(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setStyleSheet("""
            QLineEdit { font-size: 20px; padding: 14px; border: 1px solid #e2e8f0; border-radius: 6px; background: white; }
            QLineEdit:focus { border: 1px solid #3b82f6; }
        """)
        return edit

    def get_dados(self):
        """Retorna um dicionário com os dados prontos para o banco."""
        return {
            "nome": self.txt_nome.text(),
            "nascimento": self.date_nascimento.date().toString("dd/MM/yyyy"),
            "cpf": self.txt_cpf.text(),
            "whatsapp_aluno": self.txt_whatsapp.text(),
            "whatsapp_resp": self.txt_whatsapp_resp.text(),
            "modulo_atual": "Introdução" # Padrão inicial
        }
