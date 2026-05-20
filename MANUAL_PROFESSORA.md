# Manual de uso - IPI Manager

Este manual explica como usar o sistema no dia a dia da escola.

## 1. Abrindo o sistema

Abra o programa normalmente pelo computador. A primeira tela mostra o painel de maquinas.

Para acessar outras telas, aproxime o mouse do canto esquerdo da janela. O menu lateral aparece com as opcoes:

- Visao geral
- Alunos
- Turmas
- Cursos
- Financeiro
- Caixa
- Historico
- Configuracoes
- Frequencia
- Backup

## 2. Tela Visao geral

Esta tela mostra as maquinas da sala.

### Colocar aluno em uma maquina

1. Clique em uma maquina vaga.
2. Escolha o aluno na lista.
3. O aluno fica marcado como presente automaticamente.
4. Se o aluno for menor de idade e tiver telefone do responsavel, o sistema abre uma mensagem de WhatsApp avisando a presenca.

### Finalizar aula

1. Clique na maquina ocupada.
2. Responda se o aluno concluiu a licao.
3. Se responder `Sim`, o sistema avanca a aula do aluno.
4. A maquina volta a ficar vaga.

## 3. Tela Alunos

Use esta tela para cadastrar, editar e excluir alunos.

### Cadastrar aluno

1. Preencha nome, nascimento e telefones.
2. Escolha a data do primeiro pagamento no calendario.
3. Selecione turma e modulos do aluno.
4. Clique em `Matricular`.

### Editar aluno

1. Clique no aluno na tabela.
2. Altere os dados desejados.
3. Clique em `Editar`.

### Excluir aluno

1. Clique no aluno.
2. Clique em `Excluir`.

## 4. Tela Turmas

Use para cadastrar os horarios das turmas.

1. Informe o nome da turma.
2. Escolha os dois dias de aula e os horarios.
3. Informe a capacidade de computadores.
4. Clique em `Adicionar`.

## 5. Tela Cursos

Use para montar o cronograma do curso.

- Cadastre cursos.
- Cadastre modulos.
- Cadastre aulas dentro dos modulos.
- Use `Gerar cronograma principal` para criar um cronograma padrao.

## 6. Tela Financeiro

Use para controlar mensalidades dos alunos e gerar recibos.

### Selecionar aluno

1. Digite as iniciais do nome do aluno.
2. A lista mostra somente nomes que comecam com as letras digitadas.
3. Clique no aluno desejado.

### Registrar pagamento

1. Confira a data do primeiro pagamento.
2. Confira valor, vencimento, parcelas pagas e PIX.
3. Clique em `Registrar pagamento`.

Quando registrar pagamento, o valor entra automaticamente no Caixa como `Mensalidade recebida`.

### Gerar recibo

1. Selecione o aluno.
2. Confira os dados.
3. Clique em `Gerar recibo em PDF`.
4. Escolha onde salvar.

### Pendentes do mes

A tabela mostra alunos que estao com pagamento pendente no mes.

Voce pode:

- clicar no aluno pendente para carregar os dados dele;
- enviar aviso por WhatsApp;
- exportar a lista de pendentes em CSV.

## 7. Tela Caixa

Use para controlar tudo que entra e sai no mes.

### Registrar entrada

1. Escolha a data.
2. Escolha `Entrada`.
3. Escolha o tipo: Matricula, Mensalidade, Croche, Tarot, Filhos ou Outros.
4. Informe descricao, valor e status.
5. Clique em `Salvar`.

### Registrar saida

1. Escolha a data.
2. Escolha `Saida`.
3. Escolha o tipo: Aluguel, Energia, Internet, Material, Manutencao, Retirada ou Outros.
4. Informe descricao, valor e status.
5. Clique em `Salvar`.

### Totais do mes

A tela mostra:

- Entradas
- Recebido
- Saidas
- Saldo

Tambem e possivel filtrar por tipo e exportar CSV.

## 8. Tela Frequencia

Use para consultar presencas, faltas, reposicoes e progresso.

### Selecionar aluno

1. Digite as iniciais do nome.
2. Clique no aluno.

A tela mostra:

- presencas;
- faltas;
- aulas concluidas;
- progresso;
- possibilidade de gerar diploma.

### Agendar reposicao

1. Selecione uma linha marcada como `Falta`.
2. Escolha a data da reposicao.
3. Clique em `Agendar reposicao`.

## 9. Tela Historico

Use para ver a ficha completa do aluno.

1. Digite as iniciais do aluno.
2. Clique no nome.
3. Veja pagamentos, presencas e reposicoes.
4. Se desejar, clique em `Exportar historico`.

## 10. Tela Configuracoes

Use para cadastrar dias em que nao deve haver falta.

Exemplos:

- feriado;
- recesso;
- aula cancelada.

### Cadastrar data

1. Escolha a data no calendario.
2. Escolha o tipo.
3. Escreva a descricao.
4. Clique em `Salvar data`.

Essas datas passam a ser consideradas na Frequencia.

## 11. Backup

O botao `Backup` fica no menu lateral.

### Fazer backup manual

1. Clique em `Backup`.
2. Escolha uma pasta segura.
3. O sistema cria uma pasta com data e hora.

O backup salva:

- banco de dados;
- recibos;
- diplomas gerados.

### Backup automatico

Ao fechar o sistema, ele tambem faz um backup automatico na pasta `backups`.

## 12. Cuidados importantes

- Faca backup com frequencia.
- Antes de excluir aluno, confira se e realmente o aluno correto.
- Antes de registrar pagamento, confira o aluno selecionado.
- Use a tela Caixa para registrar outras entradas da professora, como croche, tarot e filhos.
- Use Configuracoes para cadastrar feriados e dias sem aula.

## 13. Rotina sugerida

### Todo dia

1. Abrir o sistema.
2. Alocar alunos nas maquinas.
3. Finalizar aula ao terminar.
4. Verificar faltas na Frequencia.

### Toda semana

1. Conferir pendentes no Financeiro.
2. Enviar avisos de WhatsApp.
3. Registrar entradas e saidas no Caixa.

### Todo mes

1. Exportar Caixa.
2. Exportar pendentes.
3. Fazer backup manual.
4. Conferir saldo do mes.
