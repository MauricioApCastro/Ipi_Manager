# Instalacao no computador do cliente

Este pacote instala o IPI Manager em um computador Windows sem precisar instalar Python.

## Arquivos do pacote

- `IPI_Manager.exe`: programa principal.
- `MANUAL_PROFESSORA.md`: manual de uso.
- `INSTALACAO_CLIENTE.md`: este guia.
- `INSTALAR_CLIENTE.bat`: instalador simples.

## Como instalar

### Opcao mais simples

1. Extraia o `.zip` em qualquer pasta.
2. Clique duas vezes em `INSTALAR_CLIENTE.bat`.
3. Aguarde a mensagem `Instalacao concluida`.
4. Abra pelo atalho `IPI Manager` criado na Area de Trabalho.

### Opcao manual

1. Crie uma pasta no computador do cliente, por exemplo:
   `C:\IPI_Manager`
2. Copie `IPI_Manager.exe` para essa pasta.
3. Abra o programa com dois cliques em `IPI_Manager.exe`.
4. Se o Windows mostrar aviso de seguranca, clique em `Mais informacoes` e depois em `Executar assim mesmo`.

Na primeira abertura, o sistema cria automaticamente:

- `data`: banco de dados.
- `recibos`: recibos e diplomas gerados.
- `backups`: backups automaticos locais.

## Backup automatico

O sistema faz backup automatico todo dia ao meio-dia, desde que esteja aberto.

Ele salva:

1. No proprio computador, na pasta `backups`.
2. Em uma pasta da nuvem configurada em `Configuracoes > Backup automatico`.

Para configurar a nuvem:

1. Instale ou abra o OneDrive, Google Drive ou Dropbox no computador do cliente.
2. Crie uma pasta sincronizada, por exemplo:
   `C:\Users\Cliente\OneDrive\Backup IPI`
3. No sistema, abra `Configuracoes`.
4. Em `Backup automatico`, clique em `Escolher pasta`.
5. Selecione a pasta da nuvem e salve.

O sistema mantem os 7 backups mais recentes em cada destino.

## Backup manual

No menu lateral, clique em `Backup` e escolha uma pasta.

## Migrar dados de outro computador

Para levar dados existentes:

1. Feche o sistema nos dois computadores.
2. Copie a pasta `data` do computador antigo.
3. Cole ao lado de `IPI_Manager.exe` no computador novo.
4. Se quiser levar recibos e diplomas, copie tambem a pasta `recibos`.

## Teste rapido apos instalar

1. Abra o sistema.
2. Entre em `Alunos` e cadastre um aluno.
3. Entre em `Financeiro`, registre um pagamento e gere o recibo.
4. Confira se a entrada apareceu em `Caixa`.
5. Entre em `Configuracoes` e configure a pasta de backup da nuvem.
6. Clique em `Backup` para testar o backup manual.

## Observacoes

- Nao apague as pastas `data`, `recibos` e `backups`.
- O recibo abre o WhatsApp do responsavel com a mensagem pronta, mas o PDF precisa ser anexado manualmente.
- Se a pasta da nuvem nao estiver sincronizando, verifique o OneDrive/Google Drive/Dropbox do Windows.
