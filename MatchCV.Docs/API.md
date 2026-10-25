# API — MatchCV

## Base URL e documentação interativa

A API usa FastAPI. Em execução local, o Swagger fica em `http://127.0.0.1:8000/docs` e o ReDoc em `http://127.0.0.1:8000/redoc`. Em produção, confirme a URL ativa no provedor de hospedagem.

As rotas de aplicação são registradas pelos roteadores em `MatchCV.Api/Routers/`; consulte o Swagger para o contrato atualizado de cada schema.

## Autenticação

| Método | Rota | Finalidade |
|---|---|---|
| POST | `/auth/register` | Cadastrar usuário comum |
| POST | `/auth/login` | Autenticar por e-mail e senha e receber token |
| GET | `/auth/me` | Consultar o usuário autenticado |
| POST | `/auth/change-password` | Alterar a senha do usuário autenticado |
| POST | `/auth/admin/bootstrap` | Inicializar o administrador sob configuração protegida |

O cadastro público não permite escolher o perfil administrativo. A inicialização do administrador exige o cabeçalho `X-Admin-Bootstrap-Token` e a variável `MATCHCV_ADMIN_BOOTSTRAP_TOKEN` configurada no ambiente. A rota de bootstrap deve ser tratada como operação sensível.

As rotas protegidas usam token Bearer. Consulte os schemas no Swagger para os campos obrigatórios e as respostas exatas.

## Recuperação de senha

| Método | Rota | Finalidade |
|---|---|---|
| POST | `/auth/password-reset/request` | Solicitar recuperação |
| POST | `/auth/password-reset/confirm` | Confirmar token e definir nova senha |

A resposta da solicitação é uniforme para evitar revelar se uma conta existe. O token só pode ser incluído na resposta em desenvolvimento quando `MATCHCV_PASSWORD_RESET_EXPOSE_TOKEN=true` e `APP_ENVIRONMENT=development`. O envio de e-mail não deve ser considerado configurado apenas porque as rotas existem; o canal de recuperação precisa ser validado separadamente.

## Análise de currículo

| Método | Rota | Finalidade |
|---|---|---|
| POST | `/analysis/resume` | Enfileirar uma análise |
| GET | `/analysis/{analysis_id}` | Consultar o estado e resultado de uma análise do usuário autenticado |

A submissão aceita a descrição da vaga e exatamente uma das opções de currículo: texto em `resume_text` ou arquivo em `resume`. Enviar ambos ou nenhum resulta em erro de validação. O envio bem-sucedido retorna HTTP `202 Accepted`, pois a análise é processada de forma assíncrona.

A consulta de uma análise é restrita ao usuário autenticado que a possui; uma análise inexistente ou pertencente a outro usuário não é retornada.

Usuários comuns estão sujeitos à cota mensal de três análises. Administradores não estão sujeitos a esse limite. A cota é reservada durante o envio e liberada em falhas tratadas pelo fluxo da API.

## Saúde

O endpoint de saúde é definido na aplicação principal. Consulte o Swagger ou `MatchCV.Api/main.py` para o caminho e formato exatos publicados pela versão atual.

## Códigos HTTP relevantes

| Código | Uso |
|---|---|
| 202 | Análise aceita para processamento assíncrono |
| 201 | Cadastro ou inicialização de recurso concluída |
| 400 | Entrada inválida ou operação não concluída |
| 401 | Credenciais ausentes ou inválidas |
| 403 | Operação não permitida, inclusive cota esgotada |
| 404 | Análise não encontrada para o usuário |
| 422 | Erro de validação de schema ou política de senha |
| 429 | Limite de provedor externo, quando propagado/tratado |
| 500 | Falha interna |
| 503 | Serviço ou configuração necessária indisponível |

O código efetivo depende da rota e da exceção. Use os schemas e respostas do Swagger como contrato operacional.

## Segurança

- Não inclua tokens, senhas, currículos ou chaves de API em URLs ou logs.
- Não trate um ID fornecido pelo cliente como prova de autorização.
- Use HTTPS em ambientes publicados.
- Mantenha o token de bootstrap fora do repositório.
- Não considere rotas planejadas como implementadas sem confirmação no código.
