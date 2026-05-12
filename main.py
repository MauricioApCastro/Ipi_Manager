import sys
from PyQt5.QtWidgets import QApplication
from src.database.db_handler import Database
from src.database.repositories import MaquinaRepository
from src.ui.windows.main_window import MainWindow
import os

from src.database.repositories import MaquinaRepository, AlunoRepository # Adicione o AlunoRepository aqui

def inicializar_sistema():
    db = Database()
    schema_path = os.path.join("src", "database", "schema.sql")
    try:
        db.execute_script(schema_path)
        
        # Semeia máquinas
        repo_maq = MaquinaRepository(db)
        repo_maq.seed_maquinas(8)
        
        # Semeia alunos de teste
        repo_aluno = AlunoRepository(db)
        repo_aluno.seed_alunos_teste()
        
        return db
    except Exception as e:
        print(f"Erro: {e}")
        return None
    db = Database()
    schema_path = os.path.join("src", "database", "schema.sql")
    try:
        db.execute_script(schema_path)
        repo_maq = MaquinaRepository(db)
        repo_maq.seed_maquinas(8)
        return db
    except Exception as e:
        print(f"Erro: {e}")
        return None

if __name__ == "__main__":
    # 1. Inicia a Aplicação Qt
    app = QApplication(sys.argv)
    
    # 2. Inicia o Banco
    banco = inicializar_sistema()
    
    if banco:
        # 3. Abre a Janela Principal passando o banco
        window = MainWindow(banco)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(1)