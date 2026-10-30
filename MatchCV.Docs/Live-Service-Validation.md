# Validação do fluxo real de produção

O script `scripts/smoke_test_live_flow.py` valida, sem mocks, o fluxo entre a API publicada, autenticação, fila persistida, worker, provedor de IA e consulta do resultado.

**Atenção:** cria uma análise real e pode consumir cota mensal. Use somente uma conta dedicada de teste e o texto sintético do próprio script. Não use currículos reais. A execução é manual e exige confirmação explícita; não deve rodar automaticamente em cada PR.

## Execução

O script usa apenas a biblioteca padrão do Python.

Linux/macOS/WSL:
```bash
export MATCHCV_API_BASE_URL="https://matchcv-api-0oi5.onrender.com"
export MATCHCV_LIVE_E2E_EMAIL="email-da-conta-de-teste"
export MATCHCV_LIVE_E2E_PASSWORD="senha-da-conta-de-teste"
export MATCHCV_LIVE_E2E_CONFIRM_PRODUCTION="YES"
python scripts/smoke_test_live_flow.py
```

PowerShell:
```powershell
$env:MATCHCV_API_BASE_URL = "https://matchcv-api-0oi5.onrender.com"
$env:MATCHCV_LIVE_E2E_EMAIL = "email-da-conta-de-teste"
$env:MATCHCV_LIVE_E2E_PASSWORD = "senha-da-conta-de-teste"
$env:MATCHCV_LIVE_E2E_CONFIRM_PRODUCTION = "YES"
python .\scripts\smoke_test_live_flow.py
```

Não compartilhe a senha nem a coloque em arquivos versionados. O teste não imprime token ou senha. O timeout pode ser ajustado por `MATCHCV_LIVE_E2E_TIMEOUT_SECONDS` (30–900 segundos).

## O que o teste verifica

1. `GET /health` confirma saúde básica da API.
2. Login real e validação de sessão em `/api/v1/auth/me`.
3. Enfileiramento de análise sintética com resposta HTTP 202.
4. Consulta autenticada até a análise chegar a `completed`, incluindo os cinco campos de resultado.

Um resultado concluído comprova que o fluxo ativo alcançou persistência/fila, worker e pelo menos um provedor configurado. Não prova que o fallback de IA foi acionado nem que a recuperação de leases foi exercitada.

## Conferências manuais obrigatórias no provedor de hospedagem

O repositório não permite consultar os segredos nem o painel do Render; confirmar os itens abaixo manualmente:

- [ ] Worker dedicado executando `python -m MatchCV.Worker.AnalysisWorker`, **ou** API deliberadamente configurada com `RUN_ANALYSIS_WORKER=true`.
- [ ] API e worker usam o mesmo SQL Server, banco, credenciais compatíveis e migrations da fila aplicadas.
- [ ] API e worker compartilham o mesmo valor válido de `ANALYSIS_QUEUE_ENCRYPTION_KEY`. Valores diferentes impedem descriptografar os itens da fila.
- [ ] `AI_PRIMARY_API_KEY`, `AI_PRIMARY_MODEL` e `AI_PRIMARY_BASE_URL` estão corretos.
- [ ] `AI_FALLBACK_API_KEY`, `AI_FALLBACK_MODEL` e `AI_FALLBACK_BASE_URL` estão corretos.
- [ ] Timeouts dos provedores são positivos e compatíveis com os limites deles.
- [ ] `APP_ENVIRONMENT`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER` e `DATABASE_PASSWORD` correspondem ao ambiente correto.
- [ ] `FRONTEND_ORIGIN` contém a origem publicada do frontend.
- [ ] Logs sanitizados confirmam a inicialização do worker e não expõem tokens, senhas, chaves ou conteúdo integral de currículos.

Quando existir worker dedicado, mantenha `RUN_ANALYSIS_WORKER=false` ou ausente na API para não iniciar outro loop junto ao servidor web.

## Interpretar falhas

- Timeout com status pendente/em processamento: conferir se o worker está ativo, se alcança o banco e se a chave de criptografia coincide.
- Status `failed`: verificar logs sanitizados do worker, conexão SQL e configuração/disponibilidade dos provedores.
- HTTP 401: conferir credenciais da conta de teste.
- HTTP 403 ao enfileirar: a cota mensal pode estar esgotada.
- Falha em `/health`: a API não está respondendo normalmente.

O smoke test não substitui a suíte de integração com SQL Server nem a inspeção manual das configurações e logs do ambiente.
