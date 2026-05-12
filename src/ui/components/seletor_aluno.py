from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QListWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class SeletorAlunoDialog(QDialog):
    def __init__(self, alunos_turma, todos_alunos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Aluno")
        self.setFixedSize(400, 500)
        self.aluno_selecionado = None

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # Aba 1: Alunos da Turma (Filtrados)
        self.lista_turma = QListWidget()
        self.lista_turma.addItems([a.nome for a in alunos_turma])
        self.tabs.addTab(self.lista_turma, "Alunos da Turma")

        # Aba 2: Todos os Alunos (Base completa)
        self.lista_todos = QListWidget()
        self.lista_todos.addItems([a.nome for a in todos_alunos])
        self.tabs.addTab(self.lista_todos, "Todos os Alunos")

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