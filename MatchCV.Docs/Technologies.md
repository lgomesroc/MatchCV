# Tecnologias

Este documento registra as tecnologias utilizadas ou previstas no projeto MatchCV.

As versões específicas serão definidas conforme a implementação e a configuração dos ambientes de desenvolvimento e execução.

## Objetivo

Registrar as tecnologias utilizadas ou previstas no desenvolvimento do MatchCV.

## Stack principal

| Tecnologia | Finalidade | Situação |
|---|---|---|
| Python | Backend e serviços | Em utilização |
| SQL Server 2022 | Banco de dados | Definido |
| pyodbc | Driver de conexão | Definido |
| Docker | Ambiente de desenvolvimento | Definido |
| Git | Versionamento | Em utilização |
| GitHub | Repositório remoto | Em utilização |
| HTML | Estrutura frontend | Planejado |
| CSS | Estilização frontend | Planejado |
| JavaScript/TypeScript | Interface | A definir |
| Framework frontend | Interface web | A definir |
| Provedores de IA | Análise semântica | Em implementação |

## Backend

### Python

Linguagem principal do backend e dos componentes de processamento do MatchCV.

Utilização prevista:

* domínio;
* aplicação;
* API;
* Parser;
* integração com IA;
* Worker;
* testes.

## API

### FastAPI

Framework previsto para exposição da API HTTP.

Responsabilidades:

* endpoints;
* upload de arquivos;
* recebimento da descrição da vaga;
* autenticação;
* autorização;
* comunicação com a camada Application.

## Banco de dados

### Microsoft SQL Server

Banco de dados relacional principal do projeto.

O ambiente de desenvolvimento será executado através de Docker.

## Containerização

### Docker

Utilizado para padronizar componentes de infraestrutura e ambientes de desenvolvimento.

### Docker Compose

Utilizado para orquestrar os serviços necessários ao ambiente local.

## Processamento de documentos

O MatchCV terá suporte a:

* PDF;
* DOC;
* DOCX.

As bibliotecas específicas de processamento serão definidas conforme a implementação de cada formato.

O Parser será isolado da aplicação para evitar que as dependências específicas dos formatos contaminem as demais camadas.

## Inteligência Artificial

O MatchCV utilizará dois provedores de inteligência artificial.

A arquitetura utilizará uma abstração comum para os provedores, permitindo:

* troca de provedor;
* fallback quando aplicável;
* testes sem chamadas reais;
* isolamento das dependências externas.

Os provedores específicos serão registrados neste documento quando definidos.

## Frontend

A interface será desenvolvida em tecnologia web.

O frontend ficará isolado em:

`MatchCV.Frontend`

A tecnologia e as versões definitivas serão registradas conforme a implementação do frontend.

## Testes

Serão utilizados testes:

* unitários;
* integração;
* testes específicos do Parser;
* testes de regras de negócio;
* testes de integração da API;
* testes de integração com banco.

A integração real com provedores de IA não será requisito para os testes unitários.

## Controle de versão

### Git

Utilizado para controle de versão.

O fluxo planejado é:

```text
branch de desenvolvimento
        ↓
commit
        ↓
push
        ↓
Pull Request
        ↓
main protegida
        ↓
deploy
```

## CI/CD

O projeto terá pipeline de CI/CD.

A ordem planejada é:

```text
Git
 ↓
Testes
 ↓
CI
 ↓
Build
 ↓
Deploy
```

Observabilidade será adicionada posteriormente, depois que o fluxo principal de CI/CD estiver estabelecido.

## Ambiente

O projeto deverá funcionar em:

* Windows;
* Linux.

A infraestrutura dependente do sistema operacional deverá ser isolada sempre que possível.

## Segurança

As configurações sensíveis não devem ser armazenadas no código-fonte.

O projeto utilizará variáveis de ambiente e um arquivo:

`.env.example`

O arquivo `.env` real não deve ser versionado.

## Privacidade

O processamento de currículos deverá seguir:

* minimização de dados;
* retenção temporária;
* ausência de armazenamento permanente do currículo original;
* ausência de currículos reais no repositório;
* ausência do conteúdo completo do currículo nos logs.

## Documentação

A documentação técnica será mantida em:

`MatchCV.Docs`

Documentos principais:

* `BusinessRules/business-rules.md`
* `Project-Structure.md`
* `Technologies.md`

## Processamento de documentos

Bibliotecas previstas ou utilizadas:

- pypdf para leitura de PDF.
- python-docx para leitura de DOCX.
- Estratégia específica para documentos DOC legados.

## Inteligência artificial

A arquitetura deverá permitir a utilização de dois provedores.

A escolha dos provedores concretos depende da configuração e implementação das integrações.

## Containerização

Docker será utilizado para padronizar o ambiente local, especialmente o SQL Server.

## Compatibilidade

O projeto considera:

- Windows 11.
- Linux.
- Docker Desktop.
- Execução local.
- Ambientes automatizados de CI.

## Critério de atualização

Toda inclusão ou substituição relevante de tecnologia deve ser registrada neste documento.

## Status

As tecnologias definidas devem ser distinguidas das tecnologias ainda em avaliação.
