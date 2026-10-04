# MatchCV

Sistema de análise inteligente de currículos e vagas utilizando processamento de documentos e inteligência artificial.

O MatchCV foi desenvolvido para ir além de um simples percentual de compatibilidade entre currículo e vaga.

A proposta é analisar o conteúdo apresentado pelo candidato, confrontá-lo com os requisitos da oportunidade e apresentar informações que ajudem a compreender a aderência real entre os dois documentos.

## Objetivo

O MatchCV analisa:

* Requisitos da vaga evidenciados no currículo.
* Requisitos da vaga não evidenciados.
* Possíveis lacunas.
* Problemas estruturais ou de conteúdo no currículo.
* Sugestões de melhoria.
* Informações que podem ser interpretadas pela inteligência artificial sem inventar experiências ou qualificações.

O sistema não deve criar experiências, tecnologias, cargos, empresas, certificações, resultados ou qualquer outra informação que não esteja evidenciada no conteúdo fornecido.

## Como executar

O MatchCV utiliza Python, FastAPI e SQL Server, com execução local e banco de dados disponibilizado por Docker Compose.

Para instalar as dependências, configurar as variáveis de ambiente, iniciar o banco de dados e executar a API, consulte o guia:

**[Guia de instalação e execução](MatchCV.Docs/Getting-Started.md)**

Após iniciar a API, a documentação interativa estará disponível em:

http://127.0.0.1:8000/docs

Consulte também a [documentação técnica](MatchCV.Docs/README.md).

## Fluxo principal

```text
Usuário
   |
   v
Upload do currículo
   |
   v
Validação do arquivo
   |
   v
Parser
   |
   v
Extração e normalização
   |
   v
Descrição da vaga
   |
   v
Análise com IA
   |
   v
Comparação currículo x vaga
   |
   v
Resultado da análise
```

## Principais características

* Suporte previsto a PDF, DOC e DOCX.
* Validação do tamanho do arquivo.
* Validação da quantidade de páginas.
* Validação do conteúdo extraído.
* Análise estrutural do currículo.
* Rejeição de documentos que não atendam aos critérios definidos.
* Processamento de descrição de vaga.
* Análise semântica com IA.
* Arquitetura preparada para dois provedores de IA.
* Processamento temporário dos currículos.
* Minimização de dados armazenados.
* Autenticação e autorização previstas.
* Testes unitários e de integração.
* Execução em Windows e Linux.
* Infraestrutura de desenvolvimento com Docker.

## Tecnologias

| Componente              | Tecnologia                        |
| ----------------------- | --------------------------------- |
| Linguagem principal     | Python                            |
| Banco de dados          | Microsoft SQL Server              |
| Driver de banco         | pyodbc                            |
| Containerização         | Docker                            |
| API                     | A definir na implementação        |
| Frontend                | A definir na implementação        |
| Inteligência artificial | Provedores externos por abstração |
| Controle de versão      | Git                               |
| Repositório remoto      | GitHub                            |

Consulte [Technologies.md](MatchCV.Docs/Technologies.md).

## Arquitetura

O projeto é dividido em módulos com responsabilidades específicas:

| Módulo                   | Responsabilidade                             |
| ------------------------ | -------------------------------------------- |
| `MatchCV.Api`            | Exposição dos endpoints HTTP                 |
| `MatchCV.Application`    | Casos de uso e orquestração                  |
| `MatchCV.Domain`         | Regras e conceitos centrais do domínio       |
| `MatchCV.Infrastructure` | Persistência e integrações de infraestrutura |
| `MatchCV.AI`             | Abstração e integração dos provedores de IA  |
| `MatchCV.Parser`         | Processamento e extração de documentos       |
| `MatchCV.Worker`         | Processamentos assíncronos                   |
| `MatchCV.Tests`          | Testes unitários e de integração             |
| `MatchCV.Db`             | Recursos relacionados ao banco de dados      |
| `MatchCV.Frontend`       | Interface da aplicação                       |
| `MatchCV.Docs`           | Documentação do projeto                      |

Consulte [Architecture.md](MatchCV.Docs/Architecture.md) e [Project-Structure.md](MatchCV.Docs/Project-Structure.md).

## Documentação

A documentação técnica está organizada em arquivos separados.

### Arquitetura e estrutura

* [Arquitetura](MatchCV.Docs/Architecture.md)
* [Estrutura do projeto](MatchCV.Docs/Project-Structure.md)
* [Tecnologias](MatchCV.Docs/Technologies.md)
* [Decisões arquiteturais](MatchCV.Docs/Decisions/Architecture-Decisions.md)

### Backend e integração

* [Backend](MatchCV.Docs/Backend.md)
* [API](MatchCV.Docs/API.md)
* [Integração da API](MatchCV.Docs/API-Integration.md)
* [Frontend](MatchCV.Docs/Frontend.md)
* [Integração com IA](MatchCV.Docs/AI-Integration.md)
* [Processamento de currículos](MatchCV.Docs/Resume-Processing.md)

### Infraestrutura e banco de dados

* [Infraestrutura](MatchCV.Docs/Infrastructure.md)
* [Ambientes](MatchCV.Docs/Environments.md)
* [Banco de dados](MatchCV.Docs/Database.md)
* [CI/CD](MatchCV.Docs/CI-CD.md)
* [Implantação](MatchCV.Docs/Deployment.md)

### Segurança e qualidade

* [Segurança](MatchCV.Docs/Security.md)
* [Privacidade](MatchCV.Docs/Privacy.md)
* [Testes](MatchCV.Docs/Testing.md)
* [Guia de desenvolvimento](MatchCV.Docs/Development-Guide.md)

### Regras e planejamento

* [Regras de negócio](MatchCV.Docs/Business-Rules.md)
* [Roadmap](MatchCV.Docs/Roadmap.md)

## Regras de negócio

As regras de negócio contemplam:

* Currículo.
* Descrição da vaga.
* Parser.
* Inteligência artificial.
* Consultas.
* Usuários.
* Privacidade.
* Segurança.
* Arquitetura.
* Qualidade.

Consulte [Business-Rules.md](MatchCV.Docs/Business-Rules.md).

## Status

O projeto está em desenvolvimento.

A implementação está sendo realizada de forma incremental, começando pelo domínio e pelo processamento dos documentos antes da construção das camadas de API, IA, persistência e interface.

O andamento de cada módulo será acompanhado no [Roadmap](MatchCV.Docs/Roadmap.md).

## Execução

O MatchCV foi planejado para funcionar em ambientes Windows e Linux.

A infraestrutura de desenvolvimento utiliza Docker quando aplicável.

Consulte [Infrastructure.md](MatchCV.Docs/Infrastructure.md) e [Development-Guide.md](MatchCV.Docs/Development-Guide.md).

## Privacidade

Os currículos enviados ao sistema não fazem parte do armazenamento permanente da aplicação.

O projeto segue o princípio de minimização de dados, evitando manter informações pessoais além do período necessário para o processamento.

Currículos reais não devem ser armazenados no repositório.

Consulte [Privacy.md](MatchCV.Docs/Privacy.md).

## Licença

A definir.
