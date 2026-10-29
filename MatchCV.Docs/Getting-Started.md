# Guia de instalação e execução — MatchCV

## Pré-requisitos

- Git.
- Python 3.12, conforme o CI.
- Docker Engine e Docker Compose para SQL Server.
- Driver ODBC compatível com SQL Server.
- Node.js e npm compatíveis com a configuração do frontend.
- Credenciais próprias para os provedores de IA que forem utilizados no ambiente.

## Clonar o repositório

```bash
git clone https://github.com/lgomesroc/MatchCV.git
cd MatchCV
git switch developer
```

## Preparar o backend

Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Edite o arquivo local `.env` e configure as variáveis necessárias para o banco, autenticação, IA e processamento assíncrono. Nunca versione esse arquivo nem compartilhe valores secretos.

## SQL Server local

Na raiz do repositório:

```bash
docker compose up -d
docker compose ps
```

Aplique as migrations necessárias em `MatchCV.Db/Migrations/` na ordem correta no banco de desenvolvimento. Confira os scripts SQL antes de executá-los. A inicialização dos containers não significa necessariamente que o schema esteja criado ou atualizado.

## Executar a API

Com o ambiente virtual ativo e as configurações preenchidas:

```bash
uvicorn MatchCV.Api.main:app --reload
```

Endereço local padrão: `http://127.0.0.1:8000`.

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Confira no Swagger os prefixos e schemas efetivamente publicados pela versão em execução.

## Frontend

Em outro terminal:

```bash
cd MatchCV.Frontend
npm ci
npm start
```

Se o script `start` não existir na versão instalada, execute `npm run` para listar os scripts disponíveis. O servidor Angular normalmente usa `http://localhost:4200/`.

Para validar o frontend:

```bash
npm test
npm run build
```

## Fluxo de autenticação e análise

A API expõe rotas de autenticação sob `/auth`, incluindo cadastro, login, consulta do usuário autenticado e alteração de senha. A análise é submetida pela rota `/analysis/resume` com token Bearer e recebe a descrição da vaga e exatamente uma das opções: texto do currículo ou arquivo.

Uma resposta HTTP `202 Accepted` indica que a análise foi aceita para processamento assíncrono. Consulte a análise pelo endpoint `/analysis/{analysis_id}` e use o Swagger para conferir o prefixo global e os schemas exatos.

## Testes

Com o ambiente virtual ativado:

```bash
PYTHONPATH="$PWD" python -m pytest -q
```

Para testar o backend isoladamente:

```bash
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Unit -q
```

Os testes de integração que usam SQL Server dependem de uma instância e credenciais válidas. O banco de teste é isolado e usa a porta 1435:

```bash
docker compose --env-file .env.test -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml ps
```

Configure localmente `TEST_DATABASE_PASSWORD` em `.env.test`. O Compose não carrega esse arquivo automaticamente sem `--env-file`. Não compartilhe senhas em logs ou mensagens. Consulte [Testing.md](Testing.md).

## Encerrar os serviços

Interrompa a API com Ctrl+C. Para parar os serviços de desenvolvimento:

```bash
docker compose down
```

Esse comando não remove volumes persistentes. Não remova volumes se precisar preservar os dados locais.

## Diagnóstico

- **API não inicia:** confira o ambiente virtual, dependências, variáveis e diretório atual.
- **SQL Server inacessível:** confira `docker compose ps`, logs, porta, nome do banco e credenciais.
- **Falha de autenticação no SQL Server:** verifique se a senha atual dentro da instância corresponde à configuração local; mudar apenas o arquivo de ambiente não altera a senha de um contêiner já inicializado.
- **Falha de IA:** confira credenciais, modelo, limites de uso e disponibilidade do fornecedor.
- **Falha de parser:** confira o formato real, integridade, tamanho e conteúdo extraível do arquivo.

## Documentação relacionada

- [Índice da documentação](README.md)
- [API](API.md)
- [Banco de dados](Database.md)
- [Ambientes](Environments.md)
- [Testes](Testing.md)
- [Recuperação de senha por e-mail](Password-Recovery.md)
- [Processamento de currículos](Resume-Processing.md)
