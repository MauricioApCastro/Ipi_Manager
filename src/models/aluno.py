from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Aluno:
    id: Optional[int] = None
    nome: str = ""
    whatsapp_aluno: str = ""
    whatsapp_resp: str = ""
    cpf: str = ""
    nascimento: str = ""

    def get_idade(self) -> int:
        """Calcula a idade do aluno baseada na string de nascimento."""
        if not self.nascimento:
            return 0
        try:
            # Tenta converter a string para objeto de data
            data_nascto = datetime.strptime(self.nascimento, "%d/%m/%Y")
            hoje = datetime.now()
            # Lógica matemática para idade
            return hoje.year - data_nascto.year - (
                (hoje.month, hoje.day) < (data_nascto.month, data_nascto.day)
            )
        except ValueError:
            return 0

    def e_menor_de_idade(self) -> bool:
        """Útil para decidir se envia WhatsApp para o responsável ou para o aluno."""
        return self.get_idade() < 18