import os
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from src.database.db_handler import Database
from src.database.repositories import MaquinaRepository, AlunoRepository
from src.ui.windows.main_window import MainWindow


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def inicializar_sistema():
    db = Database()
    schema_path = resource_path(os.path.join("src", "database", "schema.sql"))

    try:
        db.execute_script(schema_path)

        repo_maq = MaquinaRepository(db)
        repo_maq.seed_maquinas(8)

        repo_aluno = AlunoRepository(db)
        repo_aluno.seed_alunos_teste()

        return db
    except Exception as e:
        print(f"Erro: {e}")
        return None


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    tela = app.primaryScreen()
    altura_monitor = tela.availableGeometry().height() if tela else 900
    tamanho_fonte = 17 if altura_monitor <= 720 else 18 if altura_monitor <= 900 else 20
    app.setFont(QFont("Segoe UI", tamanho_fonte))

    banco = inicializar_sistema()

    if banco:
        window = MainWindow(banco)
        window.showMaximized()
        sys.exit(app.exec_())

    sys.exit(1)
