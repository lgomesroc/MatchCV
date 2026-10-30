# Testes — MatchCV

## Objetivo

Documentar como executar os testes automatizados e distinguir testes unitários, testes de integração e testes de ponta a ponta.

## Pré-requisitos

- Python 3.12.
- Ambiente virtual ativado.
- Dependências instaladas por `python -m pip install -r requirements.txt`.
- Para testes de banco, Docker e SQL Server acessível.
- Node.js e npm conforme as versões definidas em `.github/workflows/ci.yml`.
- Para Playwright local, Chromium instalado por `npx playwright install chromium`.

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

O arquivo `docker-compose.test.yml` define uma instância separada do SQL Server 2022, publicada na porta local 1435 e destinada exclusivamente ao banco `MatchCVTest`. Configure as variáveis `TEST_DATABASE_PASSWORD` e `MATCHCV_TEST_DATABASE_PASSWORD` com uma senha exclusiva de teste, no ambiente ou em um arquivo local `.env.test`. Nunca versione esse arquivo nem compartilhe suas credenciais.

Como o Compose não carrega automaticamente `.env.test` e o script de migrations precisa receber as variáveis no ambiente do processo, carregue-as no terminal antes de iniciar os testes:

```bash
set -a
. ./.env.test
set +a

docker compose --env-file .env.test -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml ps
docker logs --tail 50 matchcv-test-sqlserver
```

Confirme que o SQL Server está pronto e que as credenciais configuradas no contêiner coincidem com as usadas pelos testes antes de iniciar a suíte.

As migrações específicas do banco de teste ficam em `MatchCV.Db/Migrations/Test/`. Para aplicá-las e validar o schema localmente:

```bash
python scripts/ci_apply_test_migrations.py
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Integration -q
```

O script aguarda o SQL Server ficar disponível, aplica os arquivos SQL de teste em ordem e valida a existência das tabelas obrigatórias. Ele recusa hosts não locais, portas diferentes de 1435 e bancos diferentes de `MatchCVTest`. Os testes de integração devem usar dados descartáveis e nunca apontar para o banco de produção.

Ao terminar, remova a instância e o volume descartável:

```bash
docker compose -f docker-compose.test.yml down --volumes --remove-orphans
```

## Frontend Angular e Playwright

Na raiz do repositório:

```bash
cd MatchCV.Frontend
npm ci
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

O Playwright inicia o servidor Angular local em `http://127.0.0.1:4200`. Os cenários de ponta a ponta interceptam as chamadas HTTP da API com respostas sintéticas, portanto não precisam de credenciais, serviços reais, banco de produção nem cota de análise.

A suíte cobre login e cadastro, validação do formulário, envio do currículo, acompanhamento do processamento assíncrono, exibição do resultado, falha da API, cota esgotada, API indisponível e retorno ao formulário.

## Tipos de teste

- **Unitários:** verificam regras, validações e componentes isolados sem depender de serviços reais.
- **Integração de API:** verificam contratos HTTP e comportamento dos endpoints.
- **Banco e repositórios:** verificam conexão, schema e persistência no SQL Server.
- **Frontend:** testes unitários Angular, build e testes Playwright de ponta a ponta.

## Diagnóstico de falhas

1. Leia o resumo final do pytest e separe erros de coleta de falhas de asserção.
2. Em erros de conexão, verifique contêiner, porta, banco e credenciais antes de alterar os testes.
3. Execute isoladamente o teste que falhou para reduzir o tempo de diagnóstico.
4. Em falhas Playwright, confira o trace e a captura de tela gerados para o teste que falhou.
5. Não considere a suíte aprovada enquanto houver falhas ou erros não explicados.

## CI

O workflow `.github/workflows/ci.yml` executa os testes unitários do backend, os testes unitários Angular, o build do frontend e os testes Playwright em pushes e pull requests para `developer` e `main`. Os testes Playwright usam a API simulada pelo navegador e não dependem de serviços externos nem do SQL Server.

O workflow separado `.github/workflows/sql-server-integration.yml` inicia um contêiner SQL Server 2022 exclusivo na porta 1435, aplica em ordem os scripts de `MatchCV.Db/Migrations/Test/`, valida as tabelas obrigatórias e executa `MatchCV.Tests/Integration`. Ao final, remove o contêiner e o volume de teste.

O script `scripts/ci_apply_test_migrations.py` recusa qualquer host que não seja local, porta diferente de 1435 ou banco diferente de `MatchCVTest`. As fixtures da suíte também validam os parâmetros de conexão antes de conectar. O job utiliza uma senha exclusiva de teste, que pode ser substituída pelo secret opcional `MATCHCV_TEST_DATABASE_PASSWORD`; não utiliza credenciais ou endpoints de produção.

Para reproduzir localmente a suíte de integração, carregue `TEST_DATABASE_PASSWORD` e `MATCHCV_TEST_DATABASE_PASSWORD` com uma senha exclusiva de teste, inicie `docker-compose.test.yml`, aplique as migrations com `python scripts/ci_apply_test_migrations.py` e execute `PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Integration -q`. Nunca reutilize credenciais ou endpoints de produção.

## Documentação relacionada

- [Guia de instalação](Getting-Started.md)
- [Banco de dados](Database.md)
- [CI/CD](CI-CD.md)
