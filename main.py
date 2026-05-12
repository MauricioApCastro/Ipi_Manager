import sys
import os
from src.database.db_handler import Database

def inicializar_sistema():
    # 1. Instancia o gerenciador do banco
    db = Database()
    
    # 2. Define o caminho do script SQL
    # Usamos o os.path para evitar problemas de caminho no Windows
    schema_path = os.path.join("src", "database", "schema.sql")
    
    # 3. Executa o script para criar as tabelas
    print("Verificando banco de dados...")
    try:
        db.execute_script(schema_path)
        print("Banco de Dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar o banco: {e}")
        return None
    
    return db

if __name__ == "__main__":
    # Inicia o motor do sistema
    banco = inicializar_sistema()
    
    if banco:
        print("Sistema pronto para operação.")
        # Por enquanto, como não temos a UI pronta, o programa apenas termina aqui.
    else:
        print("Falha crítica na inicialização.")
        sys.exit(1)