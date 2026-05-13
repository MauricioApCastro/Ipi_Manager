class Maquina:
    def __init__(self, id, tag, status, ocupante=None):
        self.id = id
        self.tag = tag
        self.status = status
        self.ocupante = ocupante

    def __repr__(self):
        return f"<Maquina {self.tag} - {self.status} ({self.ocupante})>"