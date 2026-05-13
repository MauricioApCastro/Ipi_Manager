import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.database.db_handler import Database
from src.database.repositories import AlunoRepository, CursoRepository, FinanceiroRepository, TurmaRepository
from src.models.aluno import Aluno


def criar_turma_se_nao_existir(repo, nome, dia1, horario1, dia2, horario2, capacidade=8):
    for turma in repo.get_all():
        if turma[1] == nome:
            return turma[0]
    return repo.add(nome, dia1, horario1, dia2, horario2, capacidade)


def criar_aluno_se_nao_existir(repo, nome, whatsapp, resp, cpf, nascimento, turma_id, modulos_ids, licao, obs=""):
    existente = repo.get_by_name(nome)
    if existente:
        existente.whatsapp_aluno = whatsapp
        existente.whatsapp_resp = resp
        existente.cpf = cpf
        existente.nascimento = nascimento
        existente.turma_id = turma_id
        existente.modulos_ids = modulos_ids
        existente.licao_atual = licao
        existente.modulo_atual = ", ".join(obs_modulos(modulos_ids)) if modulos_ids else "Introducao"
        existente.observacoes = obs
        repo.update(existente)
        return existente.id

    aluno = Aluno(None, nome, whatsapp, resp, cpf, nascimento)
    aluno.turma_id = turma_id
    aluno.modulos_ids = modulos_ids
    aluno.licao_atual = licao
    aluno.modulo_atual = ", ".join(obs_modulos(modulos_ids)) if modulos_ids else "Introducao"
    aluno.observacoes = obs
    repo.add(aluno)
    return aluno.id


def obs_modulos(modulos_ids):
    return [f"Modulo {idx:02d}" for idx, _modulo_id in enumerate(modulos_ids, start=1)]


def criar_curso_demo_completo(repo):
    curso_id = None
    for curso in repo.get_cursos():
        if curso[1] == "Curso Completo IPI Demo":
            curso_id = curso[0]
            break

    if not curso_id:
        curso_id = repo.add_curso("Curso Completo IPI Demo", 14, 135.0)

    existentes = {modulo[3]: modulo for modulo in repo.get_modulos(curso_id)}
    for mes in range(1, 15):
        if mes in existentes:
            modulo_id = existentes[mes][0]
        else:
            modulo_id = repo.add_modulo(
                curso_id,
                f"Modulo {mes:02d}",
                mes,
                carga_meses=1,
                permite_flexibilidade=mes > 1,
            )

        aulas_existentes = [aula for aula in repo.get_aulas(curso_id) if aula[1] == modulo_id]
        if not aulas_existentes:
            for aula in range(1, 5):
                ordem = ((mes - 1) * 4) + aula
                repo.add_aula(modulo_id, f"Aula {aula:02d}", ordem)

    return curso_id


def main():
    db = Database()
    db.execute_script(os.path.join(ROOT, "src", "database", "schema.sql"))

    repo_aluno = AlunoRepository(db)
    repo_curso = CursoRepository(db)
    repo_turma = TurmaRepository(db)
    repo_financeiro = FinanceiroRepository(db)

    curso_id = criar_curso_demo_completo(repo_curso)
    modulos = repo_curso.get_modulos(curso_id)
    modulos_ids = [modulo[0] for modulo in modulos]

    turmas = {
        "Manha 1": criar_turma_se_nao_existir(repo_turma, "Manha 1", "Segunda", "08:00", "Quarta", "08:00"),
        "Manha 2": criar_turma_se_nao_existir(repo_turma, "Manha 2", "Terca", "08:00", "Quinta", "08:00"),
        "Tarde 1": criar_turma_se_nao_existir(repo_turma, "Tarde 1", "Segunda", "14:00", "Quarta", "14:00"),
        "Tarde 2": criar_turma_se_nao_existir(repo_turma, "Tarde 2", "Terca", "15:30", "Quinta", "15:30"),
        "Noite 1": criar_turma_se_nao_existir(repo_turma, "Noite 1", "Terca", "19:00", "Quinta", "19:00"),
        "Sabado": criar_turma_se_nao_existir(repo_turma, "Sabado", "Sabado", "08:30", "Sabado", "09:30"),
    }

    alunos = [
        ("Ana Clara Bruno", "(11) 96321-6999", "", "529.982.247-25", "14/02/2001", "Manha 1", [0, 1], 3, 2, "Aluna antiga"),
        ("Pedro Henrique Lima", "(11) 95555-1001", "(11) 94444-1001", "390.533.447-05", "22/09/2012", "Manha 1", [0], 1, 0, "Menor - avisar responsavel"),
        ("Julia Martins Souza", "(11) 95555-1002", "", "111.444.777-35", "03/06/1998", "Manha 2", [2, 3], 8, 6, "Avancada"),
        ("Rafael Costa", "(11) 95555-1003", "(11) 94444-1003", "935.411.347-80", "19/11/2011", "Tarde 1", [0, 1], 2, 1, "Novo aluno"),
        ("Bianca Alves", "(11) 95555-1004", "", "987.654.321-00", "09/04/2005", "Tarde 1", [4, 5], 12, 10, "Aluna antiga"),
        ("Lucas Pereira", "(11) 95555-1005", "", "123.456.789-09", "28/08/2000", "Tarde 2", [1, 2], 5, 4, "Intermediario"),
        ("Mariana Oliveira", "(11) 95555-1006", "(11) 94444-1006", "153.509.460-56", "15/01/2013", "Tarde 2", [0], 1, 0, "Menor iniciante"),
        ("Gabriel Santos", "(11) 95555-1007", "", "746.971.314-01", "07/12/1996", "Noite 1", [6, 7], 16, 12, "Avancado"),
        ("Camila Rocha", "(11) 95555-1008", "", "040.072.178-32", "30/03/2003", "Noite 1", [3, 4], 9, 7, "Antiga"),
        ("Thiago Nunes", "(11) 95555-1009", "(11) 94444-1009", "009.865.860-00", "12/10/2010", "Sabado", [0, 1], 2, 1, "Menor sabado"),
        ("Fernanda Lopes", "(11) 95555-1010", "", "695.960.290-60", "21/05/1994", "Sabado", [8, 9], 21, 13, "Quase concluindo"),
        ("Daniel Moraes", "(11) 95555-1011", "", "168.995.350-09", "18/07/2002", "Manha 2", [0], 1, 0, "Novo matriculado"),
    ]

    for nome, whatsapp, resp, cpf, nascimento, turma_nome, modulo_indices, licao, parcelas, obs in alunos:
        selecionados = [modulos_ids[i] for i in modulo_indices if i < len(modulos_ids)]
        aluno_id = criar_aluno_se_nao_existir(
            repo_aluno,
            nome,
            whatsapp,
            resp,
            cpf,
            nascimento,
            turmas[turma_nome],
            selecionados,
            licao,
            obs,
        )
        repo_financeiro.salvar_config(
            aluno_id,
            "10/03/2026",
            parcelas,
            135.0,
            155.0,
            10,
            "1196321-6999",
        )

    with db.connection() as conn:
        print("Dados de demonstração criados com sucesso.")
        print("Cursos:", conn.execute("SELECT COUNT(1) FROM cursos").fetchone()[0])
        print("Módulos:", conn.execute("SELECT COUNT(1) FROM modulos").fetchone()[0])
        print("Aulas:", conn.execute("SELECT COUNT(1) FROM aulas").fetchone()[0])
        print("Turmas:", conn.execute("SELECT COUNT(1) FROM turmas").fetchone()[0])
        print("Alunos:", conn.execute("SELECT COUNT(1) FROM alunos").fetchone()[0])
        print("Financeiro:", conn.execute("SELECT COUNT(1) FROM financeiro_alunos").fetchone()[0])


if __name__ == "__main__":
    main()
