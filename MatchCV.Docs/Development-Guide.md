# Guia de desenvolvimento — MatchCV

## Pré-requisitos

- Git.
- Python 3.12, conforme o workflow de CI.
- Ambiente virtual Python.
- Docker Engine e Docker Compose para SQL Server local e de teste.
- Driver ODBC compatível com SQL Server.
- Node.js e npm conforme `.github/workflows/ci.yml` para o frontend.

## Preparar o repositório

```bash
git clone https://github.com/lgomesroc/MatchCV.git
cd MatchCV
git switch developer
```

## Backend Python

Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Configure o ambiente a partir do modelo `.env.example`. Mantenha valores secretos em arquivos locais ignorados pelo Git ou em configurações seguras do ambiente.

Para executar a API localmente:

```bash
uvicorn MatchCV.Api.main:app --reload
```

A documentação interativa costuma ficar em `http://127.0.0.1:8000/docs`.

## SQL Server

```bash
docker compose up -d
docker compose ps
```

Aplique as migrations necessárias ao banco local em ordem. Consulte [Database.md](Database.md).

Para testes de integração, use a instância isolada de `docker-compose.test.yml`; consulte [Testing.md](Testing.md). Não reutilize banco de produção em testes.

## Frontend

```bash
cd MatchCV.Frontend
npm ci
npm test
npm run build
```

Consulte `package.json` para os scripts disponíveis. O workflow de CI é a referência para as versões de runtime usadas nas verificações automatizadas.

## Organização do código

- `MatchCV.Api`: HTTP, schemas e dependências.
- `MatchCV.Application`: casos de uso.
- `MatchCV.Domain`: entidades e regras de domínio.
- `MatchCV.Infrastructure`: banco e repositórios.
- `MatchCV.Parser`: leitura e validação de documentos.
- `MatchCV.AI`: integração com provedores.
- `MatchCV.Worker`: processamento assíncrono.
- `MatchCV.Login`: autenticação e autorização.
- `MatchCV.Tests`: testes automatizados.

## Git e revisão

Trabalhe em uma branch adequada à tarefa, mantenha os commits focados e revise o diff antes de enviar alterações. Execute testes relevantes antes de abrir ou atualizar um Pull Request. Não faça commits de arquivos `.env`, credenciais, currículos reais ou outros dados pessoais.

## Documentação

Quando alterar comportamento, endpoints, schema, configuração ou regras de negócio, atualize os documentos relacionados. A estrutura de diretórios é documentada separadamente em [Project-Structure.md](Project-Structure.md).

## Verificações úteis

```bash
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Unit -q
python -m compileall -q MatchCV.Api MatchCV.AI MatchCV.Application MatchCV.Domain MatchCV.Infrastructure MatchCV.Parser
```

Para a suíte completa e os testes com banco, consulte [Testing.md](Testing.md).
