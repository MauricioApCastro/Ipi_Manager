from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[1]
DATABASES = [
    ROOT / "data" / "escola.db",
    ROOT / "dist" / "data" / "escola.db",
    ROOT / "dist" / "IPI_Manager_Portable" / "data" / "escola.db",
    ROOT / "escola.db",
]

TABLES = [
    "financeiro_alunos",
    "mensagens_responsavel",
    "presencas",
    "aluno_modulos",
    "aulas",
    "modulos",
    "cursos",
    "alunos",
    "turmas",
    "maquinas",
]


def reset_database(path):
    if not path.exists():
        return False

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = OFF")
        existing = {
            row[0]
            for row in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }

        for table in TABLES:
            if table in existing:
                cur.execute(f"DELETE FROM {table}")

        if "maquinas" in existing:
            for index in range(1, 9):
                cur.execute(
                    "INSERT INTO maquinas (tag, status, ocupante) VALUES (?, ?, NULL)",
                    (f"PC-{index:02d}", "VAGO"),
                )

        if "sqlite_sequence" in existing:
            cur.execute("DELETE FROM sqlite_sequence")

        conn.commit()

    return True


if __name__ == "__main__":
    for database in DATABASES:
        if reset_database(database):
            print(database)
