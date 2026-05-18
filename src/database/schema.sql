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
    observacoes TEXT,
    turma_id INTEGER,
    FOREIGN KEY (turma_id) REFERENCES turmas(id)
);

CREATE TABLE IF NOT EXISTS cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    duracao_meses INTEGER DEFAULT 14,
    valor_base REAL DEFAULT 135.00
);

CREATE TABLE IF NOT EXISTS modulos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_curso INTEGER,
    nome TEXT NOT NULL,
    ordem INTEGER,
    carga_meses INTEGER DEFAULT 1,
    permite_flexibilidade INTEGER DEFAULT 0,
    pre_requisito_id INTEGER,
    FOREIGN KEY (id_curso) REFERENCES cursos(id),
    FOREIGN KEY (pre_requisito_id) REFERENCES modulos(id)
);

CREATE TABLE IF NOT EXISTS aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_modulo INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    ordem INTEGER,
    observacoes TEXT,
    FOREIGN KEY (id_modulo) REFERENCES modulos(id)
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
    segundo_dia_semana TEXT,
    segundo_horario TEXT,
    duracao_aula_minutos INTEGER DEFAULT 60,
    aulas_por_semana INTEGER DEFAULT 2,
    capacidade_manual INTEGER 
);

CREATE TABLE IF NOT EXISTS aluno_modulos (
    aluno_id INTEGER NOT NULL,
    modulo_id INTEGER NOT NULL,
    PRIMARY KEY (aluno_id, modulo_id),
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (modulo_id) REFERENCES modulos(id)
);

CREATE TABLE IF NOT EXISTS presencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    maquina_tag TEXT,
    data_hora TEXT NOT NULL,
    observacao TEXT,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);

CREATE TABLE IF NOT EXISTS mensagens_responsavel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    telefone TEXT,
    mensagem TEXT NOT NULL,
    data_hora TEXT NOT NULL,
    status TEXT DEFAULT 'GERADA',
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);

CREATE TABLE IF NOT EXISTS caixa_entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    valor REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'PREVISTO',
    tipo TEXT NOT NULL DEFAULT 'ENTRADA',
    observacoes TEXT
);

CREATE TABLE IF NOT EXISTS calendario_excecoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT 'FERIADO'
);

CREATE TABLE IF NOT EXISTS reposicoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    data_falta TEXT NOT NULL,
    data_reposicao TEXT,
    status TEXT NOT NULL DEFAULT 'PENDENTE',
    observacoes TEXT,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);
