# Validação ponta a ponta com serviços reais

Este roteiro valida o Angular publicado contra a API publicada, com SQL Server, fila persistida, worker e provedor de IA reais. O teste de integração ao vivo é opt-in: não roda no CI comum, pois cria contas e análises, consome cota e pode gerar custos no provedor de IA.

## Pré-requisitos

- Deploy de frontend e API compatíveis com a branch developer.
- Worker ativo e conectado ao mesmo SQL Server da API; fila e resultados precisam usar a mesma chave de criptografia.
- Migrações aplicadas e provedor primário ou fallback de IA configurado.
- Conta administrativa de teste existente. Não use credenciais pessoais nem compartilhe segredos no repositório.
- Node/npm do projeto, dependências instaladas e Chromium do Playwright.

## Execução (PowerShell)

Execute na pasta MatchCV.Frontend:

```powershell
$env:MATCHCV_LIVE_SERVICES = "true"
$env:MATCHCV_LIVE_CONFIRM_PRODUCTION = "YES"
$env:MATCHCV_LIVE_FRONTEND_URL = "https://URL-REAL-DO-FRONTEND"
$env:MATCHCV_LIVE_API_URL = "https://URL-REAL-DA-API"
$env:MATCHCV_LIVE_ADMIN_EMAIL = "EMAIL-DA-CONTA-ADMIN-DE-TESTE"
$env:MATCHCV_LIVE_ADMIN_PASSWORD = "SENHA-DA-CONTA-ADMIN-DE-TESTE"
npm run test:e2e -- e2e/live-services.spec.ts
```

A URL da API deve ser a origem do serviço (por exemplo, https://api.exemplo.com), sem /api/v1; o teste acrescenta os caminhos. O frontend publicado precisa ter sido compilado apontando para essa mesma API.

O teste cria duas contas comuns com e-mails @example.com aleatórios e senha gerada em memória. O conteúdo do currículo e da vaga é sintético. O relatório contém URLs, IDs das análises e os passos concluídos, mas não deve conter tokens ou senhas. O teste pode deixar análises enfileiradas ao validar cota; execute apenas em ambiente de teste controlado.

## O que o cenário real comprova

- Health da API, cadastro pela interface Angular, login e sessão autenticada em /auth/me.
- Envio pela interface de uma análise por texto e outra por PDF sintético.
- Resposta de enfileiramento HTTP 202 e espera pela conclusão real, consultando o status persistido até obter os cinco campos do resultado.
- Resultado final exibido no Angular.
- Conta diferente recebe HTTP 404 ao consultar análise alheia.
- A quarta reserva da conta comum é negada com HTTP 403 (cota de três análises).
- Conta administrativa consegue enfileirar mais de três análises.

O teste não inspeciona diretamente conexões SQL ou logs internos; a conclusão de que SQL Server, fila e worker participaram é inferida da conclusão de uma análise que foi enfileirada e depois retornada pela API. Confirme a execução do worker e os registros de falha nos logs do serviço durante a rodada.

## Erros, timeout e indisponibilidade da IA

Os testes E2E existentes com respostas simuladas cobrem erro HTTP da API na submissão e mensagem de erro na interface. Isso não substitui uma falha real do provedor. Para validar falha de IA sem risco, use um ambiente de homologação separado com credenciais inválidas ou endpoint de teste deliberadamente indisponível, sem modificar segredos nem interromper produção. Confirme nos logs que o provedor primário e o fallback falharam, que a análise foi marcada como falha e que a interface informa o problema. Para timeout, configure temporariamente um timeout baixo apenas na homologação e confirme que a execução termina com estado conhecido, sem ficar eternamente em processamento.

Não provoque indisponibilidade deliberada no serviço de produção. O teste de sucesso real é a prova obrigatória de ponta a ponta; falhas controladas são cenários adicionais de homologação.

## Evidências e critério de conclusão

Após a execução, o teste grava test-results/live-services-e2e-report.json (ou o caminho de MATCHCV_LIVE_REPORT_PATH). Anexe o relatório sem segredos à PR e registre data/hora da execução e links/identificadores dos deploys testados. Não marque a prioridade como concluída até que o cenário real termine com outcome: passed e o relatório seja revisado. Se o teste não foi executado por falta de acesso ao deploy ou à conta administrativa, a PR fornece o mecanismo, mas o critério de conclusão continua pendente.
