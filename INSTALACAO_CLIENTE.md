# Instalacao e teste em outra maquina

Este guia mostra como preparar uma maquina Windows para testar o IPI Manager.

## Opcao recomendada: levar o executavel

Se voce gerar o executavel antes, a maquina da cliente nao precisa instalar Python nem dependencias.

Na sua maquina de desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\pyinstaller.exe IPI_Manager.spec
```

Depois copie para a maquina cliente:

- `dist\IPI_Manager.exe`
- pasta `data`, se quiser levar um banco ja preenchido
- pasta `recibos`, se quiser levar recibos/diplomas ja gerados

Se quiser comecar vazio, leve somente o executavel. O sistema cria a pasta `data` automaticamente.

## Opcao para rodar pelo codigo-fonte

Instale na maquina cliente:

1. Python 3.10 ou superior.
2. Git, se for baixar pelo GitHub.
3. Dependencias do projeto.

Comandos no PowerShell:

```powershell
git clone https://github.com/MauricioApCastro/Ipi_Manager
cd Ipi_Manager
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Dependencias do sistema

Para rodar pelo codigo-fonte:

- Python 3.10+
- PyQt5
- PyQt5-Qt5
- PyQt5_sip

Para gerar executavel:

- PyInstaller

Os pacotes Python estao em:

- `requirements.txt`
- `requirements-build.txt`

## Pastas importantes

O sistema usa estas pastas:

- `data`: banco de dados SQLite.
- `recibos`: recibos e diplomas em PDF.
- `backups`: backups automaticos.

## Antes de testar com a professora

1. Abra o sistema.
2. Cadastre uma turma.
3. Cadastre um curso ou gere o cronograma principal.
4. Cadastre um aluno.
5. Aloque o aluno em uma maquina.
6. Registre pagamento no Financeiro.
7. Confira se a entrada apareceu no Caixa.
8. Gere um backup manual.

## Observacoes

- O backup manual fica no local escolhido.
- O backup automatico e feito ao fechar o sistema.
- Para levar dados reais para outro computador, copie tambem a pasta `data`.
- Para levar recibos e diplomas ja gerados, copie tambem a pasta `recibos`.
