# Tecnologias — MatchCV

Este documento distingue a stack existente das configurações que dependem do ambiente.

## Stack principal

| Componente | Tecnologia | Uso |
|---|---|---|
| Backend | Python | API, casos de uso, parser, worker e testes |
| API HTTP | FastAPI | Endpoints e documentação OpenAPI |
| Frontend | Angular e TypeScript | Interface web |
| Banco relacional | Microsoft SQL Server | Contas, análises, fila e dados relacionados |
| Driver SQL | pyodbc | Conexão Python com SQL Server |
| Acesso ao banco | ODBC Driver para SQL Server | Conectividade do ambiente |
| Processamento de documentos | Parsers PDF, DOC e DOCX | Validação e extração de texto |
| IA | Provedores externos via abstração | Análise semântica |
| Containers | Docker e Docker Compose | Infraestrutura local e banco de teste |
| Testes backend | pytest | Testes unitários e de integração |
| Versionamento | Git e GitHub | Histórico, branches e revisão |
| CI | GitHub Actions | Testes unitários do backend e testes/build do frontend |
| Hospedagem conhecida | Render | Frontend e API publicados |

## Versões

O workflow `.github/workflows/ci.yml` configura Python 3.12 e Node.js 24.19.0; também instala npm 11.19.0. O Angular CLI registrado no README do frontend é 22.2.0. Para versões exatas de bibliotecas Python e JavaScript, use `requirements.txt`, `package.json` e `package-lock.json` como fontes de verdade.

A imagem do SQL Server é declarada nos arquivos Compose. Confira a configuração ativa antes de assumir que ambientes locais e publicados usam a mesma versão.

## Organização técnica

- `MatchCV.Api`: aplicação HTTP.
- `MatchCV.Application`: casos de uso e coordenação.
- `MatchCV.Domain`: regras de negócio e entidades.
- `MatchCV.Infrastructure`: repositórios e persistência.
- `MatchCV.Parser`: extração e validação de currículos.
- `MatchCV.AI`: integração com modelos e provedores externos.
- `MatchCV.Worker`: processamento assíncrono.
- `MatchCV.Login`: autenticação, hashing e autorização.
- `MatchCV.Db`: migrations SQL.
- `MatchCV.Tests`: testes.
- `MatchCV.Frontend`: frontend Angular.

## Provedores de IA

Os nomes dos provedores, modelos, endpoints e timeouts dependem das variáveis de ambiente. Exemplos de configuração não garantem disponibilidade, quota ou acesso ao modelo. Não versionar chaves.

## Desenvolvimento e CI

O frontend usa npm e scripts definidos no `package.json`. O backend usa dependências listadas em `requirements.txt`. O workflow de CI executa os testes unitários Python e os testes e build do frontend; não executa a suíte completa de integração com SQL Server.

## Segurança e privacidade

Configurações sensíveis devem ficar fora do código-fonte. Currículos são dados pessoais: não devem ser versionados nem aparecer integralmente nos logs. Consulte [Security.md](Security.md) e [Privacy.md](Privacy.md).

## Manutenção deste documento

Atualize este inventário quando a stack mudar. Para detalhes sobre versões instaladas, prefira os manifests e lockfiles versionados em vez de manter números redundantes aqui.
