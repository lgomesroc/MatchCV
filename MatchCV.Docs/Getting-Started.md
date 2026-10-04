# Guia de instalação e execução — MatchCV

Este documento apresenta os procedimentos necessários para preparar o ambiente de desenvolvimento, configurar o banco de dados SQL Server e executar a API do MatchCV localmente.

## 1. Pré-requisitos

Antes de iniciar, tenha instalado:

* Python 3.12 ou superior;
* Git;
* Docker Engine ou Docker Desktop;
* Docker Compose;
* acesso a pelo menos um provedor de IA configurado.

O desenvolvimento pode ser realizado em Linux ou Windows.

## 2. Clonar o repositório

Clone o repositório:

```bash
git clone https://github.com/lgomesroc/MatchCV.git
```

Acesse o diretório:

```bash
cd MatchCV
```

Durante o desenvolvimento, utilize a branch `developer`:

```bash
git checkout developer
```

A branch `main` deve permanecer protegida e não deve receber alterações diretamente.

## 3. Criar o ambiente virtual Python

### Linux

Crie o ambiente virtual:

```bash
python3 -m venv .venv
```

Ative:

```bash
source .venv/bin/activate
```

### Windows — CMD

Crie o ambiente:

```cmd
python -m venv .venv
```

Ative:

```cmd
.venv\Scripts\activate
```

Quando o ambiente estiver ativo, o terminal apresentará o prefixo:

```text
(.venv)
```

## 4. Instalar as dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

## 5. Configurar as variáveis de ambiente

O MatchCV utiliza um arquivo `.env` para armazenar configurações locais.

Crie o arquivo a partir do modelo:

### Linux

```bash
cp .env.example .env
```

### Windows — CMD

```cmd
copy .env.example .env
```

Abra o arquivo `.env` no VS Code e configure as variáveis necessárias.

### Configuração dos provedores de IA

O fluxo previsto para produção utiliza:

* OpenAI como provedor principal;
* Google Gemini como provedor de fallback.

Exemplo da configuração:

```env
AI_PRIMARY_API_KEY=sua_chave_openai
AI_PRIMARY_MODEL=gpt-5.5
AI_PRIMARY_BASE_URL=https://api.openai.com/v1/chat/completions
AI_PRIMARY_TIMEOUT_SECONDS=60

AI_FALLBACK_API_KEY=sua_chave_gemini
AI_FALLBACK_MODEL=gemini-3-flash-preview
AI_FALLBACK_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
AI_FALLBACK_TIMEOUT_SECONDS=60
```

Utilize suas próprias credenciais nos campos correspondentes.

**Importante:** nunca adicione chaves de API, senhas ou outras credenciais ao Git. O arquivo `.env` está incluído no `.gitignore`.

A disponibilidade dos provedores depende das condições das respectivas APIs, incluindo limites de utilização, créditos e disponibilidade dos modelos.

## 6. Inicializar o SQL Server

O banco de dados do MatchCV utiliza SQL Server em ambiente Docker.

Na raiz do projeto, execute:

```bash
docker compose up -d
```

Verifique os containers:

```bash
docker compose ps
```

Para acompanhar os logs:

```bash
docker compose logs -f
```

O SQL Server precisa estar disponível antes da execução das operações que dependem de persistência.

## 7. Criar o banco de dados

A migration inicial está localizada em:

```text
MatchCV.Db/Migrations/001_initial_schema.sql
```

O banco utilizado pela aplicação é:

```text
MatchCV
```

A migration deve ser executada no SQL Server para criar a estrutura inicial necessária à aplicação.

A documentação complementar está em:

[Database.md](Database.md)

## 8. Executar a API

Com o ambiente virtual ativado e as configurações necessárias disponíveis, execute na raiz do projeto:

```bash
uvicorn MatchCV.Api.main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

### Documentação interativa

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

O Swagger permite visualizar os endpoints e realizar requisições durante o desenvolvimento.

Para encerrar a API, pressione `Ctrl+C` no terminal em que o Uvicorn está sendo executado.

## 9. Executar uma análise de currículo

O endpoint de análise é:

```http
POST /api/v1/analysis/resume
```

A requisição recebe:

* `resume`: arquivo de currículo;
* `job_description`: descrição textual da vaga.

### Exemplo com cURL no Linux

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analysis/resume" \
  -F "resume=@/caminho/para/curriculo.pdf" \
  -F "job_description=<Docs/test-job-description.txt"
```

Substitua o caminho do currículo pelo caminho real do arquivo que deseja analisar.

O projeto possui uma descrição de vaga de exemplo:

```text
Docs/test-job-description.txt
```

Os formatos de currículo aceitos são PDF, DOC e DOCX, respeitando as regras de validação implementadas.

## 10. Verificar a compilação dos módulos

Para verificar erros de sintaxe nos módulos principais:

```bash
python -m compileall -q \
  MatchCV.Api \
  MatchCV.AI \
  MatchCV.Application \
  MatchCV.Domain \
  MatchCV.Infrastructure \
  MatchCV.Parser
```

A ausência de saída indica que a compilação foi concluída sem erros.

## 11. Executar os testes automatizados

Os testes estão organizados em:

```text
MatchCV.Tests/
├── Unit/
└── Integration/
```

Para executar a suíte:

```bash
pytest
```

A cobertura de testes está em evolução durante o desenvolvimento do projeto.

Testes que utilizem provedores externos de IA podem depender de credenciais, créditos e disponibilidade dos serviços. Testes unitários devem priorizar provedores simulados, evitando chamadas externas desnecessárias.

Consulte:

[Testing.md](Testing.md)

## 12. Encerrar o ambiente

Para interromper a API:

```text
Ctrl+C
```

Para parar os containers:

```bash
docker compose down
```

Esse comando interrompe e remove os containers definidos no Compose, mas não deve ser confundido com a exclusão dos volumes persistentes.

Não utilize comandos de remoção de volumes se desejar preservar os dados locais do banco.

## 13. Problemas comuns

### API não inicia

Verifique:

* se o ambiente virtual está ativado;
* se as dependências foram instaladas;
* se o comando está sendo executado na raiz do projeto;
* se as variáveis necessárias estão configuradas.

### SQL Server não está disponível

Verifique:

```bash
docker compose ps
```

E consulte os logs:

```bash
docker compose logs
```

### Erro de autenticação ou limite na API de IA

Verifique:

* se a chave está correta;
* se o provedor está habilitado;
* se existem créditos ou quota disponíveis;
* se o modelo configurado está acessível;
* se o serviço está operacional.

Falhas do provedor principal podem acionar o fallback. Se ambos falharem, a aplicação retorna um erro controlado.

### Erro ao processar currículo

Verifique:

* formato do arquivo;
* tamanho;
* quantidade de páginas;
* presença de texto extraível;
* estrutura do documento.

Consulte:

[Resume-Processing.md](Resume-Processing.md)

---

## Documentação relacionada

* [README principal](../README.md)
* [Índice da documentação](README.md)
* [Estrutura do projeto](Project-Structure.md)
* [Integração com IA](AI-Integration.md)
* [Banco de dados](Database.md)
* [Processamento de currículos](Resume-Processing.md)
* [Testes](Testing.md)
