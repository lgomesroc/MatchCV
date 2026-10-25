# Infraestrutura — MatchCV

## Visão geral

O MatchCV utiliza Python/FastAPI, SQL Server via `pyodbc`, Docker Compose para ambientes locais e serviços publicados no Render. O frontend Angular é mantido em `MatchCV.Frontend`; o workflow de integração contínua fica em `.github/workflows/ci.yml`.

## Componentes

| Componente | Responsabilidade |
|---|---|
| API FastAPI | Receber requisições, autenticar usuários e iniciar operações |
| SQL Server | Persistir usuários, descrições, análises, fila e reservas de cota |
| Worker | Processar análises enfileiradas |
| Parser | Validar arquivos e extrair texto de currículos |
| Camada de IA | Integrar com provedores externos configurados |
| Angular | Interface web e comunicação HTTP com a API |
| Docker Compose | Executar serviços locais e instância isolada de SQL Server para testes |
| GitHub Actions | Executar testes unitários Python e testes/build do frontend |

## Configuração

As configurações devem ser fornecidas por variáveis de ambiente. O `.env.example` serve como modelo para desenvolvimento; `.env` e `.env.test` são arquivos locais e não devem ser versionados. Credenciais e chaves reais não devem aparecer em documentação, logs ou commits.

## SQL Server

O Compose de desenvolvimento e o Compose de testes têm finalidades distintas. O banco de testes é publicado na porta local 1435 e deve usar credenciais isoladas. Consulte `Database.md`, `Environments.md` e `Testing.md` antes de executar migrations ou testes de integração.

## Processamento assíncrono

A API pode enfileirar uma análise e responder HTTP 202 antes do término do processamento. A API e o worker precisam compartilhar a configuração do banco e as chaves necessárias para interpretar o payload da fila. Uma thread executada junto à API não equivale a um serviço worker dedicado e pode ser interrompida por reinicializações ou suspensão do host.

## Implantação

O frontend e a API possuem URLs de hospedagem documentadas no README principal. A disponibilidade, as variáveis configuradas, o banco utilizado e os gatilhos de deploy devem ser confirmados no painel do provedor. O workflow de CI não deve ser interpretado como prova de deploy automático.

## Operação segura

- Não misture dados de desenvolvimento, teste e produção.
- Não remova volumes persistentes sem confirmar a necessidade.
- Aplique migrations em ordem e no banco correto.
- Não registre conteúdo integral de currículos.
- Confira logs sanitizados e estado dos serviços ao investigar falhas.

## Referências

- `Database.md`
- `Environments.md`
- `Deployment.md`
- `CI-CD.md`
- `Testing.md`
