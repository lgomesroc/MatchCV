# Ambientes — MatchCV

## Ambientes

| Ambiente | Uso |
|---|---|
| Desenvolvimento local | API, frontend e banco para desenvolvimento |
| Testes | Testes unitários e de integração com dados descartáveis |
| Produção | Serviços publicados e banco configurado no provedor |

Homologação só deve ser considerada disponível quando houver infraestrutura configurada para esse propósito.

## Desenvolvimento local

- Python 3.12 ou compatível com as dependências.
- Ambiente virtual Python.
- Dependências de `requirements.txt`.
- Docker Engine e Docker Compose para SQL Server local.
- Driver ODBC compatível com SQL Server.
- Node.js e npm compatíveis com a versão do frontend Angular.

O `docker-compose.yml` define os serviços locais da aplicação. Use `docker compose ps` para conferir seu estado e `docker compose logs` para diagnosticar falhas.

## Testes

O arquivo `docker-compose.test.yml` define uma instância SQL Server separada, com porta local 1435 e banco de teste `MatchCVTest`. A configuração de teste usa a variável `TEST_DATABASE_PASSWORD`.

O Compose não carrega `.env.test` automaticamente. Quando a variável não estiver exportada no shell, inicie o serviço explicitamente com:

```bash
docker compose --env-file .env.test -f docker-compose.test.yml up -d
```

O arquivo `.env.test` é local e não deve ser versionado. Não reutilize credenciais de produção nos testes. Consulte [Testing.md](Testing.md).

## Produção

Os serviços frontend e API estão publicados no Render nos endereços registrados no [README principal](../README.md). Confirme a configuração atual diretamente no painel do provedor.

A configuração de produção deve fornecer, de forma segura, os valores necessários para conexão ao SQL Server, autenticação, provedores de IA e processamento assíncrono. Não presuma que um valor de desenvolvimento seja adequado para produção.

## Arquivos de configuração

- `.env.example`: modelo de variáveis.
- `.env`: configuração local, não versionada.
- `.env.test`: configuração local para testes, não versionada.
- `docker-compose.yml`: serviços de desenvolvimento.
- `docker-compose.test.yml`: SQL Server isolado para testes.
- `requirements.txt`: dependências Python.
- `MatchCV.Frontend/package.json` e `package-lock.json`: dependências do frontend.

## Segurança

Nunca registre ou publique senhas, tokens, chaves de API, strings de conexão completas ou dados reais de currículos. Separe os dados de desenvolvimento, testes e produção.
