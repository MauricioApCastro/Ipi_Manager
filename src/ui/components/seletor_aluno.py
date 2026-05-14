from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QListWidget, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

class SeletorAlunoDialog(QDialog):
    def __init__(self, alunos_turma, todos_alunos, parent=None, titulo_turma="Alunos do horário"):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Aluno")
        self.resize(620, 720)
        self.setMinimumSize(360, 420)
        self.aluno_selecionado = None

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # Aba 1: Alunos da Turma (Filtrados)
        self.lista_turma = QListWidget()
        if alunos_turma:
            self.lista_turma.addItems([a.nome for a in alunos_turma])
        else:
            self.lista_turma.addItem("Nenhum aluno no horário atual")
            self.lista_turma.item(0).setFlags(Qt.NoItemFlags)
        self.tabs.addTab(self.lista_turma, titulo_turma)

        # Aba 2: Todos os Alunos (Base completa)
        self.lista_todos = QListWidget()
        self.lista_todos.addItems([a.nome for a in todos_alunos])
        self.tabs.addTab(self.lista_todos, "Todos / exceção")

        aviso = QLabel("Use a segunda aba somente para inclusão por exceção.")
        aviso.setStyleSheet("color: #64748b; font-size: 20px; font-weight: 600;")
        layout.addWidget(aviso)
        layout.addWidget(self.tabs)

        # Botões Inferiores
        btn_layout = QHBoxLayout()
        self.btn_confirmar = QPushButton("Confirmar")
        self.btn_confirmar.clicked.connect(self.confirmar)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_confirmar)
        layout.addLayout(btn_layout)

    def confirmar(self):
        # Verifica qual aba está ativa para pegar o item selecionado
        widget_atual = self.tabs.currentWidget()
        item = widget_atual.currentItem()

        if item:
            self.aluno_selecionado = item.text()
            self.accept()
