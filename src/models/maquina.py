from dataclasses import dataclass

@dataclass
class Maquina:
    id: int
    tag: str  # ex: PC-01
    status: str = "ATIVO"  # ATIVO, MANUTENCAO, DEFEITO

    def pode_receber_aluno(self) -> bool:
        """Regra de negócio: só aloca se o status for ATIVO."""
        return self.status.upper() == "ATIVO"