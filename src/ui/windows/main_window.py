from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QGridLayout, QMessageBox
from src.database.repositories import MaquinaRepository, AlunoRepository
from src.ui.components.maquina_card import MaquinaCard
from src.ui.components.seletor_aluno import SeletorAlunoDialog

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.repo_maquina = MaquinaRepository(self.db)
        self.repo_aluno = AlunoRepository(self.db)
        self.setWindowTitle("IPI PRO - Gestão de Sala")
        self.resize(1200, 800)
        self.setup_ui()
        self.carregar_maquinas()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #1e293b;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        logo = QLabel("IPI PRO")
        logo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin: 20px;")
        sidebar_layout.addWidget(logo)
        
        for nome in ["VISÃO GERAL", "ALUNOS", "CURSOS", "FINANCEIRO"]:
            btn = QPushButton(nome)
            btn.setStyleSheet("""
                QPushButton { color: #cbd5e1; text-align: left; padding: 15px; border: none; font-weight: bold; }
                QPushButton:hover { background-color: #334155; color: white; }
            """)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar)

        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.lbl_titulo = QLabel("Painel de Máquinas")
        self.lbl_titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b; margin: 20px;")
        self.content_layout.addWidget(self.lbl_titulo)

        self.grid_maquinas = QGridLayout()
        self.grid_maquinas.setSpacing(20)
        self.content_layout.addLayout(self.grid_maquinas)
        self.content_layout.addStretch()
        self.main_layout.addWidget(self.content_area)

    def carregar_maquinas(self):
        """Reconstrói o painel e recupera o estado dos alunos alocados."""
        maquinas = self.repo_maquina.get_all()
        for i in reversed(range(self.grid_maquinas.count())): 
            self.grid_maquinas.itemAt(i).widget().setParent(None)

        for index, maq in enumerate(maquinas):
            card = MaquinaCard(maq)
            
            if maq.status == "OCUPADO" and maq.ocupante:
                aluno = self.repo_aluno.get_by_name(maq.ocupante)
                if aluno:
                    info_aula = f"{aluno.modulo_atual} - Aula {aluno.licao_atual}"
                    card.atualizar_status("OCUPADO", aluno.nome, info_aula)
                    card.txt_obs.setText(aluno.observacoes or "")
                    
                    # Salva obs automaticamente quando a professora muda de campo
                    card.txt_obs.editingFinished.connect(
                        lambda c=card: self.repo_aluno.salvar_observacao_aluno(c.maquina.ocupante, c.txt_obs.text())
                    )

            card.solicitar_alocacao.connect(self.processar_alocacao)
            self.grid_maquinas.addWidget(card, index // 4, index % 4)

    def processar_alocacao(self, card_que_pediu):
        status_texto = card_que_pediu.lbl_status.text().strip().upper()

        if status_texto != "VAGO":
            # FLUXO DE SAÍDA
            resposta = QMessageBox.question(
                self, "Finalizar Aula",
                f"O aluno {status_texto} concluiu a lição de hoje?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if resposta == QMessageBox.Cancel:
                return

            if resposta == QMessageBox.Yes:
                aluno_obj = self.repo_aluno.get_by_name(status_texto)
                if aluno_obj:
                    nova_licao = (aluno_obj.licao_atual or 1) + 1
                    self.repo_aluno.atualizar_progresso(aluno_obj.id, nova_licao)

            self.repo_maquina.finalizar_alocacao(card_que_pediu.maquina.tag)
            card_que_pediu.atualizar_status("VAGO")
            return

        # FLUXO DE ENTRADA
        todos_alunos = self.repo_aluno.get_all()
        alunos_turma = todos_alunos[:5] # Simulação de turma por enquanto

        seletor = SeletorAlunoDialog(alunos_turma, todos_alunos, self)
        
        if seletor.exec_():
            nome_sel = seletor.aluno_selecionado
            aluno = self.repo_aluno.get_by_name(nome_sel)
            
            if aluno:
                # Trava de duplicidade
                for i in range(self.grid_maquinas.count()):
                    w = self.grid_maquinas.itemAt(i).widget()
                    if isinstance(w, MaquinaCard) and w.lbl_status.text().strip().upper() == nome_sel.upper():
                        QMessageBox.warning(self, "Bloqueio", f"{nome_sel} já está alocado!")
                        return

                self.repo_maquina.salvar_alocacao(card_que_pediu.maquina.tag, nome_sel)
                info_aula = f"{aluno.modulo_atual} - Aula {aluno.licao_atual}"
                card_que_pediu.atualizar_status("OCUPADO", nome_sel, info_aula)
                card_que_pediu.txt_obs.setText(aluno.observacoes or "")
                
                # Ativa o salvamento automático para o novo aluno
                card_que_pediu.txt_obs.editingFinished.connect(
                    lambda c=card_que_pediu: self.repo_aluno.salvar_observacao_aluno(c.maquina.ocupante, c.txt_obs.text())
                )