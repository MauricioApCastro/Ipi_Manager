from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

class SeletorAlunoDialog(QDialog):
    def __init__(self, alunos_turma, todos_alunos, parent=None, titulo_turma="Alunos do horário", turmas_hoje=None):
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
            for aluno in alunos_turma:
                self._adicionar_aluno(self.lista_turma, aluno.nome)
        else:
            self._adicionar_item_desativado(self.lista_turma, "Nenhum aluno no horário atual")
        self.tabs.addTab(self.lista_turma, titulo_turma)

        # Aba 2: Turmas do dia por horário
        self.lista_turmas_hoje = QListWidget()
        self._preencher_turmas_hoje(turmas_hoje or [])
        self.tabs.addTab(self.lista_turmas_hoje, "Turmas de hoje")

        # Aba 3: Todos os Alunos (Base completa)
        self.lista_todos = QListWidget()
        for aluno in todos_alunos:
            self._adicionar_aluno(self.lista_todos, aluno.nome)
        self.tabs.addTab(self.lista_todos, "Todos / exceção")

        aviso = QLabel("Use a aba Todos / exceção somente para inclusão por exceção.")
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
            self.aluno_selecionado = item.data(Qt.UserRole) or item.text()
            self.accept()

    def _preencher_turmas_hoje(self, turmas_hoje):
        if not turmas_hoje:
            self._adicionar_item_desativado(self.lista_turmas_hoje, "Nenhuma turma cadastrada para hoje")
            return

        for horario, turma, alunos in turmas_hoje:
            self._adicionar_item_desativado(self.lista_turmas_hoje, f"{horario} - {turma}")
            if alunos:
                for aluno in alunos:
                    self._adicionar_aluno(self.lista_turmas_hoje, f"   {aluno.nome}", aluno.nome)
            else:
                self._adicionar_item_desativado(self.lista_turmas_hoje, "   Nenhum aluno matriculado")

    def _adicionar_aluno(self, lista, texto, nome=None):
        item = QListWidgetItem(texto)
        item.setData(Qt.UserRole, nome or texto.strip())
        lista.addItem(item)

    def _adicionar_item_desativado(self, lista, texto):
        item = QListWidgetItem(texto)
        item.setFlags(Qt.NoItemFlags)
        lista.addItem(item)
