# API — MatchCV

## Base URL e documentação interativa

A API usa FastAPI. Em execução local, a base dos endpoints versionados é `http://127.0.0.1:8000/api/v1`. Em produção, confirme a URL ativa no provedor de hospedagem.

A documentação interativa fica em `/docs` (Swagger), o ReDoc em `/redoc` e o schema OpenAPI em `/openapi.json`. Esses três recursos são protegidos por autenticação HTTP Basic quando `SWAGGER_USERNAME` e `SWAGGER_PASSWORD` estão configurados. Se as credenciais não estiverem configuradas, os recursos de documentação retornam HTTP 404. O endpoint `/health` informa a saúde básica da API.

As rotas de aplicação são registradas pelos roteadores em `MatchCV.Api/Routers/`; consulte o Swagger para os schemas e detalhes atualizados de cada operação.

## Autenticação

As rotas abaixo usam o prefixo `/api/v1`.

| Método | Rota | Finalidade |
|---|---|---|
| POST | `/auth/register` | Cadastrar usuário comum |
| POST | `/auth/login` | Autenticar por e-mail e senha e receber token |
| GET | `/auth/me` | Consultar o usuário autenticado |
| POST | `/auth/change-password` | Alterar a senha do usuário autenticado |
| POST | `/auth/admin/bootstrap` | Inicializar o administrador sob configuração protegida |

O cadastro público não permite escolher o perfil administrativo. A inicialização do administrador exige o cabeçalho `X-Admin-Bootstrap-Token` e a variável `MATCHCV_ADMIN_BOOTSTRAP_TOKEN` configurada no ambiente com pelo menos 32 caracteres. A rota de bootstrap deve ser tratada como operação sensível e usada somente no processo controlado de inicialização.

As rotas protegidas usam token Bearer. Consulte os schemas no Swagger para os campos obrigatórios e as respostas exatas.

## Recuperação de senha

| Método | Rota | Finalidade |
|---|---|---|
| POST | `/auth/password-reset/request` | Solicitar recuperação |
| POST | `/auth/password-reset/confirm` | Confirmar token e definir nova senha |

A resposta da solicitação é sempre uniforme para evitar revelar se uma conta existe ou se ela é elegível para recuperação. **O token nunca é devolvido no corpo da resposta da API.** Quando a conta é elegível, a API armazena o hash do token e envia por e-mail um link para o frontend, com o token original no fragmento da URL (`#token=...`).

A geração e o envio dependem de `PASSWORD_RESET_FRONTEND_URL` e das configurações SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, além de `SMTP_FROM_NAME` e `SMTP_TIMEOUT_SECONDS` opcionais. A configuração presente no código não comprova que o provedor SMTP esteja operacional; o envio real precisa ser validado no ambiente publicado.

O token expira em 15 minutos e só pode ser consumido uma vez. A confirmação exige que a nova senha e sua confirmação coincidam e aplica `PasswordPolicy`. Tokens inválidos, expirados ou já utilizados não alteram a senha.

## Análise de currículo

| Método | Rota | Finalidade |
|---|---|---|
| POST | `/analysis/resume` | Enfileirar uma análise |
| GET | `/analysis/{analysis_id}` | Consultar o estado e resultado de uma análise do usuário autenticado |

A submissão aceita a descrição da vaga e exatamente uma das opções de currículo: texto em `resume_text` ou arquivo em `resume`. Enviar ambos ou nenhum resulta em erro de validação. O envio bem-sucedido retorna HTTP `202 Accepted`, pois a análise é enfileirada e processada de forma assíncrona.

Regras de entrada atualmente implementadas no domínio:

- Currículo textual extraído: até 15.000 caracteres.
- Descrição da vaga: até 15.000 caracteres.
- Arquivo de currículo: até 1 MiB (1.048.576 bytes).
- Documento: no máximo duas páginas.
- Currículo e descrição da vaga: pelo menos 30 caracteres alfanuméricos úteis.
- O currículo enviado por arquivo precisa ter texto extraível e passar pelas validações de formato e estrutura do Parser.

O limite de 15.000 caracteres também se aplica ao texto extraído do arquivo. O limite de 1 MiB do arquivo permanece independente do limite de caracteres.

A consulta de uma análise é restrita ao usuário autenticado que a possui; uma análise inexistente ou pertencente a outro usuário não é retornada.

Usuários comuns estão sujeitos à cota mensal de três análises. Administradores não estão sujeitos a esse limite. A cota é reservada durante o envio; reservas são liberadas em falhas tratadas pelo fluxo da API e reconciliadas pelo worker em seu processo de recuperação.

## Saúde

- `GET /health`: retorna o estado básico da API, com `status: "ok"` e `service: "MatchCV API"`.
- Esse endpoint não comprova, isoladamente, que SQL Server, worker, SMTP ou provedores de IA estejam disponíveis.

## Códigos HTTP relevantes

| Código | Uso |
|---|---|
| 200 | Operação concluída, como login, consulta do usuário ou alteração de senha |
| 202 | Análise aceita para processamento assíncrono |
| 201 | Cadastro ou inicialização de recurso concluída |
| 400 | Entrada inválida ou operação não concluída |
| 401 | Credenciais ausentes ou inválidas |
| 403 | Operação não permitida, token de bootstrap inválido ou cota esgotada |
| 404 | Análise não encontrada para o usuário ou documentação indisponível quando não configurada |
| 409 | Conflito na inicialização administrativa |
| 422 | Erro de validação de schema ou política de senha |
| 500 | Falha interna |
| 503 | Serviço ou configuração necessária indisponível |

O código efetivo depende da rota e da exceção. Use os schemas e respostas do Swagger como contrato operacional. Erros de provedores externos podem ser tratados pelo serviço de IA ou pelo worker, sem necessariamente serem propagados diretamente ao cliente HTTP.

## Segurança

- Não inclua tokens, senhas, currículos ou chaves de API em URLs ou logs. A recuperação usa fragmento de URL para transportar o token até o frontend; o token não deve ser enviado a servidores de terceiros nem registrado em logs.
- Não trate um ID fornecido pelo cliente como prova de autorização.
- Use HTTPS em ambientes publicados.
- Mantenha o token de bootstrap fora do repositório.
- Proteja as credenciais HTTP Basic da documentação e não as reutilize como credenciais da aplicação.
- Não considere rotas planejadas como implementadas sem confirmação no código.
