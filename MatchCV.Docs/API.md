# API — MatchCV

## 1. Objetivo

Documentar a interface HTTP utilizada pelo frontend e por clientes autorizados.

## 2. Responsabilidades

A API será responsável por:

- Receber requisições.
- Validar dados de entrada.
- Controlar autenticação.
- Aplicar autorização.
- Invocar casos de uso.
- Converter resultados em respostas HTTP.
- Padronizar erros.

## 3. Endpoints planejados

Os caminhos abaixo representam o contrato inicial proposto. Não devem ser considerados endpoints implementados até sua criação e validação.

### Análise de currículo

`POST /api/v1/analyses`

Finalidade:

Enviar currículo e descrição da vaga para análise.

Entrada prevista:

- Arquivo do currículo.
- Descrição da vaga.

Resposta de sucesso prevista:

`200 OK`

Conteúdo:

- Requisitos evidenciados.
- Requisitos não evidenciados.
- Lacunas.
- Problemas do currículo.
- Sugestões.

### Consultar análise

`GET /api/v1/analyses/{id}`

Finalidade:

Consultar uma análise previamente registrada, respeitando autenticação e autorização.

### Usuário autenticado

`GET /api/v1/users/me`

Finalidade:

Retornar informações do usuário autenticado.

### Autenticação

Os endpoints de autenticação serão definidos conforme a implementação do mecanismo de identidade.

## 4. Códigos HTTP

| Código | Significado |
|---|---|
| 200 | Operação concluída |
| 201 | Recurso criado |
| 400 | Requisição inválida |
| 401 | Não autenticado |
| 403 | Sem autorização |
| 404 | Recurso não encontrado |
| 413 | Arquivo acima do limite |
| 415 | Tipo de mídia não suportado |
| 422 | Conteúdo não processável |
| 429 | Limite de consultas excedido |
| 500 | Erro interno |
| 502 | Falha em serviço externo |
| 503 | Serviço temporariamente indisponível |

## 5. Validação de entrada

A API deverá validar:

- Campos obrigatórios.
- Tamanho do arquivo.
- Tipo de arquivo.
- Descrição da vaga.
- Identificação do usuário.
- Permissões da operação.

## 6. Segurança

- Não expor stack traces ao cliente.
- Não aceitar identificação de usuário como prova de autorização.
- Não registrar arquivos ou currículos completos em logs.
- Proteger endpoints administrativos.
- Utilizar HTTPS em ambientes publicados.

## 7. Versionamento

A API utilizará versionamento de rota, inicialmente:

`/api/v1`

## 8. Status

Endpoints documentados como planejamento. A implementação será registrada conforme a evolução da API.
