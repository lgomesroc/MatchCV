# Testes — MatchCV

## Objetivo

Documentar como executar os testes automatizados e distinguir testes unitários de testes de integração.

## Pré-requisitos

- Python 3.12.
- Ambiente virtual ativado.
- Dependências instaladas por `python -m pip install -r requirements.txt`.
- Para testes de banco, Docker e SQL Server acessível.
- Arquivo de configuração de teste com credenciais locais válidas; nunca versionar segredos.

## Executar testes

Na raiz do repositório, com o ambiente virtual ativo:

```bash
PYTHONPATH="$PWD" python -m pytest -q
```

O prefixo `PYTHONPATH="$PWD"` permite que o Python encontre os módulos do projeto ao executar os testes a partir da raiz. Também é possível executar subconjuntos, por exemplo:

```bash
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Unit -q
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Integration/Api -q
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Integration/Repositories -q
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Integration/TestDatabase -q
```

## SQL Server para testes

O arquivo `docker-compose.test.yml` define uma instância separada para testes, publicada na porta local 1435 e destinada ao banco `MatchCVTest`. Configure a variável `TEST_DATABASE_PASSWORD` no ambiente ou no arquivo local `.env.test`.

Como o Compose não carrega automaticamente `.env.test`, quando as variáveis não estiverem exportadas use:

```bash
docker compose --env-file .env.test -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml ps
docker logs --tail 50 matchcv-test-sqlserver
```

Confirme que o SQL Server está pronto e que as credenciais configuradas no contêiner coincidem com as usadas pelos testes antes de iniciar a suíte. Não compartilhe senhas em logs, mensagens ou commits.

As migrações específicas do banco de teste ficam em `MatchCV.Db/Migrations/Test/`. Os testes de integração devem usar dados descartáveis e não devem apontar para o banco de produção.

## Tipos de teste

- **Unitários:** verificam regras, validações e componentes isolados sem depender de serviços reais.
- **Integração de API:** verificam contratos HTTP e comportamento dos endpoints.
- **Banco e repositórios:** verificam conexão, schema e persistência no SQL Server.
- **Frontend:** executados pelo projeto Angular em `MatchCV.Frontend`.

Para os testes do frontend:

```bash
cd MatchCV.Frontend
npm ci
npm test
npm run build
```

## Diagnóstico de falhas

1. Leia o resumo final do pytest e separe erros de coleta de falhas de asserção.
2. Em erros de conexão, verifique contêiner, porta, banco e credenciais antes de alterar os testes.
3. Execute isoladamente o teste que falhou para reduzir o tempo de diagnóstico.
4. Não considere a suíte aprovada enquanto houver falhas ou erros não explicados.

## CI

O workflow `.github/workflows/ci.yml` executa testes unitários do backend e testes/build do frontend em pushes e pull requests para `developer` e `main`. Os testes que exigem um SQL Server real não são executados por esse job unitário.

## Documentação relacionada

- [Guia de instalação](Getting-Started.md)
- [Banco de dados](Database.md)
- [CI/CD](CI-CD.md)
