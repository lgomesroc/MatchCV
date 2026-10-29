# Recuperação de senha por e-mail

A recuperação pública usa as rotas:

- `POST /api/v1/auth/password-reset/request`: recebe o e-mail e sempre responde com a mesma mensagem genérica, sem indicar se a conta existe ou se é elegível.
- `POST /api/v1/auth/password-reset/confirm`: recebe token, nova senha e confirmação. O token tem validade de 15 minutos e é consumido atomicamente; tokens expirados, já usados ou inválidos são recusados.

O token original é enviado somente por e-mail. O SQL Server armazena apenas SHA-256 do token. A API não retorna tokens no corpo da resposta e não oferece mecanismo de desenvolvimento para expô-los. O link usa o fragmento `#token=` da URL, que não é enviado ao servidor web em requisições HTTP. A interface remove o token da barra de endereço depois de capturá-lo.

## Configuração

Configure as variáveis no ambiente da API (Render ou outro host), nunca no código nem no repositório:

- `APP_ENVIRONMENT=production`
- `PASSWORD_RESET_FRONTEND_URL=https://SEU-FRONTEND-PUBLICADO` — origem pública do Angular, sem barra final.
- `SMTP_HOST` — servidor SMTP do provedor.
- `SMTP_PORT=587` — porta com STARTTLS.
- `SMTP_USERNAME` e `SMTP_PASSWORD` — credenciais SMTP ou senha de aplicativo.
- `SMTP_FROM_EMAIL` — remetente autorizado pelo provedor.
- `SMTP_FROM_NAME=MatchCV`
- `SMTP_TIMEOUT_SECONDS=10`

Não use a senha normal da sua conta de e-mail se o provedor oferecer senha de aplicativo. Confirme no painel do provedor que o remetente está verificado e que a hospedagem permite conexões SMTP de saída. Se a plataforma bloquear SMTP, use um provedor transacional compatível em vez de contornar o bloqueio.

## Validar sem expor segredos

1. Configure as variáveis SMTP e a URL pública do frontend no ambiente de homologação.
2. Aplique a migração `006_password_reset_tokens.sql` no SQL Server utilizado pela API.
3. Solicite recuperação para uma conta de teste e confirme que o e-mail chega.
4. Abra o link, altere a senha e entre com a senha nova.
5. Tente usar o mesmo link novamente e confirme que a API recusa.
6. Solicite um link, aguarde mais de 15 minutos e confirme que ele expirou.
7. Repita a solicitação com um endereço inexistente. A resposta HTTP e a mensagem devem ser iguais às de uma conta existente.
8. Confira logs do servidor sem registrar o token, link completo, senha ou conteúdo sensível.

Se o envio falhar, a API continua retornando uma resposta genérica para não revelar existência da conta, registra o erro internamente e tenta revogar o token recém-criado. A configuração de SMTP precisa ser testada no ambiente publicado: testes com remetente simulado não provam entregabilidade real.
