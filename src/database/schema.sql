-- Habilita chaves estrangeiras
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    whatsapp_aluno TEXT,
    whatsapp_resp TEXT,
    cpf TEXT,
    nascimento TEXT,
    licao_atual INTEGER DEFAULT 1,
    modulo_atual TEXT DEFAULT 'Introdução',
    observacoes TEXT 
);

CREATE TABLE IF NOT EXISTS cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    valor_base REAL DEFAULT 135.00
);

CREATE TABLE IF NOT EXISTS modulos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_curso INTEGER,
    nome TEXT NOT NULL,
    ordem INTEGER,
    pre_requisito_id INTEGER,
    FOREIGN KEY (id_curso) REFERENCES cursos(id),
    FOREIGN KEY (pre_requisito_id) REFERENCES modulos(id)
);

CREATE TABLE IF NOT EXISTS maquinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'VAGO',
    ocupante TEXT 
);

CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    dia_semana TEXT,
    horario TEXT,
    capacidade_manual INTEGER 
);