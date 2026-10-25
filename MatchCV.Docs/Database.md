# Banco de dados — MatchCV

## Tecnologia e ambientes

O MatchCV utiliza Microsoft SQL Server e o driver Python `pyodbc`. O banco principal local usa o nome `MatchCV`; a instância de testes é separada e utiliza o banco `MatchCVTest`, publicado na porta local 1435 pelo `docker-compose.test.yml`.

A configuração de conexão vem do ambiente. Nunca registre senhas nem strings de conexão completas em documentos versionados.

## Migrations

As migrations versionadas ficam em `MatchCV.Db/Migrations/`; migrations específicas do banco de teste ficam em `MatchCV.Db/Migrations/Test/`. Revise e aplique-as em ordem no banco correto. Não presuma que a API executa migrations automaticamente.

Antes de alterar o schema:
1. Identifique o banco e o ambiente de destino.
2. Leia a migration inteira.
3. Verifique compatibilidade com os repositórios.
4. Faça backup apropriado para ambientes com dados importantes.
5. Execute os testes de banco/repositório.

## Persistência funcional

O banco armazena dados de conta, descrições de vagas, estado e resultados das análises e dados de suporte ao processamento assíncrono. As tabelas concretas e os tipos de coluna são definidos pelas migrations; consulte os arquivos SQL como fonte de verdade para o schema atual.

Os repositórios devem usar consultas parametrizadas. Senhas são armazenadas como hashes, nunca em texto puro. O arquivo original do currículo não deve ser mantido permanentemente; qualquer persistência de texto extraído ou resultado deve respeitar a política de retenção.

## Fila e processamento assíncrono

O fluxo de análise usa tabelas de fila e reservas de cota criadas por migrations. A configuração da API e do worker precisa apontar para o mesmo banco. A chave de criptografia do payload, quando configurada, deve ser válida e consistente entre os componentes que escrevem e leem a fila.

A fila permite acompanhar estado e recuperar tarefas conforme a lógica implementada. Isso não elimina a necessidade de configurar e monitorar o worker.

## Banco de testes

O serviço de teste é independente do banco de desenvolvimento. Para iniciar com o arquivo local de variáveis:

```bash
docker compose --env-file .env.test -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml ps
```

O arquivo `.env.test` não deve ser versionado. A credencial configurada no contêiner precisa coincidir com a usada pelos testes. Se a senha do SQL Server for alterada em uma instância persistente, atualizar apenas o arquivo de ambiente não altera automaticamente a senha já definida dentro do banco.

Consulte [Testing.md](Testing.md) para executar a suíte.

## Privacidade e segurança

- Não use dados pessoais reais em testes automatizados.
- Não coloque currículos no Git.
- Não registre texto integral de currículos em logs.
- Separe credenciais e bases de desenvolvimento, teste e produção.
- Restrinja o acesso à instância e use HTTPS e configuração segura onde aplicável.

## Fonte de verdade

Este documento explica o uso e a operação do banco. Para tabelas, colunas, constraints e índices exatos, consulte as migrations SQL atuais.
