# CI/CD — MatchCV

## Integração contínua configurada

O workflow `.github/workflows/ci.yml` é acionado em pushes e pull requests direcionados às branches `developer` e `main`.

Ele possui dois jobs:

### Backend — Python

1. Usa Ubuntu.
2. Configura Python 3.12.
3. Instala as dependências de `requirements.txt` e pytest.
4. Executa `python -m pytest MatchCV.Tests/Unit -q`.

Esse job executa os testes unitários; não inicializa o SQL Server de integração.

### Frontend — Angular

1. Usa Node.js 24.19.0.
2. Instala npm 11.19.0.
3. Executa `npm ci`.
4. Executa `npm test` com `CI=true`.
5. Executa `npm run build`.

## Fluxo de contribuição

O fluxo recomendado é trabalhar em uma branch específica, revisar as alterações, executar testes relevantes e abrir ou atualizar um Pull Request para revisão. A branch `main` deve representar o estado integrado estável.

Não presuma que uma verificação passou apenas porque o workflow foi disparado: confira o resultado dos jobs no GitHub.

## Entrega e implantação

O workflow de CI não prova, por si só, que o deploy esteja automatizado. A publicação dos serviços é feita no Render conforme a configuração do projeto e do provedor. Confirme os gatilhos e o estado do deploy nos painéis correspondentes.

## Segredos

Credenciais e chaves devem ser configuradas em mecanismos seguros do ambiente. Não as inclua em arquivos versionados, logs, mensagens de commit ou artefatos de CI.

## Limitações atuais documentadas

- O job do backend executa testes unitários, não a suíte completa de integração com SQL Server.
- A execução de testes de integração local exige configuração separada; consulte [Testing.md](Testing.md).
- A configuração de deploy deve ser verificada diretamente nos serviços hospedados antes de afirmar que uma publicação foi concluída.
