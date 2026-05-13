class Aluno:
    def __init__(self, id, nome, whatsapp_aluno, whatsapp_resp, cpf, nascimento, licao_atual=1, modulo_atual='Introdução', observacoes=None):
        self.id = id
        self.nome = nome
        self.whatsapp_aluno = whatsapp_aluno
        self.whatsapp_resp = whatsapp_resp
        self.cpf = cpf
        self.nascimento = nascimento
        self.licao_atual = licao_atual
        self.modulo_atual = modulo_atual
        self.observacoes = observacoes
        self.turma_id = None
        self.modulos_ids = []
