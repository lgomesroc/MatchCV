# MatchCV

Sistema de análise inteligente de currículos e vagas utilizando processamento de documentos e inteligência artificial.

O MatchCV vai além de um simples percentual de compatibilidade entre currículo e vaga: analisa o conteúdo apresentado pelo candidato, confronta-o com os requisitos da oportunidade e apresenta informações que ajudam a compreender a aderência real entre os dois documentos.

O sistema não deve inventar experiências, tecnologias, cargos, empresas, certificações, resultados ou outras qualificações que não estejam evidenciadas no conteúdo fornecido.

## Aplicação publicada

- **Frontend:** https://matchcv-frontend-020d.onrender.com
- **API:** https://matchcv-api-0oi5.onrender.com
- **Documentação interativa da API (Swagger):** https://matchcv-api-0oi5.onrender.com/docs

A aplicação está hospedada no Render. A disponibilidade pode depender do estado atual dos serviços e do plano de hospedagem.

## Objetivo

O MatchCV apresenta:

- Requisitos da vaga evidenciados no currículo.
- Requisitos da vaga não evidenciados.
- Possíveis lacunas entre currículo e vaga.
- Problemas estruturais ou de conteúdo no currículo.
- Sugestões de melhoria.
- Informações interpretadas pela inteligência artificial sem inventar experiências ou qualificações.

## Tecnologias

| Componente | Tecnologia |
| --- | --- |
| Linguagem do backend | Python |
| API | FastAPI |
| Frontend | Angular e TypeScript |
| Banco de dados | Microsoft SQL Server |
| Driver de banco | pyodbc |
| Infraestrutura local | Docker e Docker Compose |
| Inteligência artificial | Provedores externos integrados por abstração |
| Hospedagem da aplicação | Render |
| Repositório remoto | GitHub |

Consulte [Technologies.md](MatchCV.Docs/Technologies.md) para mais detalhes.

## Banco de dados

O projeto utiliza Microsoft SQL Server. A instância configurada para o ambiente hospedado no Somee utiliza o host:

`MatchCV.mssql.somee.com`

O acesso ao banco é feito por uma conexão SQL Server configurada na aplicação. Não coloque senhas, strings de conexão com credenciais ou outros segredos neste README ou no repositório. Os parâmetros de conexão devem ser fornecidos pela configuração segura do ambiente.

Consulte [Database.md](MatchCV.Docs/Database.md) e [Environments.md](MatchCV.Docs/Environments.md).

## Como executar localmente

O MatchCV utiliza Python, FastAPI e SQL Server, com suporte à execução local e infraestrutura de desenvolvimento por Docker Compose.

Para instalar as dependências, configurar as variáveis de ambiente, iniciar os serviços necessários e executar a API, siga o:

**[Guia de instalação e execução](MatchCV.Docs/Getting-Started.md)**

Após iniciar a API localmente, a documentação interativa estará disponível em:

http://127.0.0.1:8000/docs

Consulte também a [documentação técnica](MatchCV.Docs/README.md).

## Fluxo principal

```text
Usuário
   |
   v
Envio do currículo
   |
   v
Validação do arquivo
   |
   v
Extração e normalização do conteúdo
   |
   v
Descrição da vaga
   |
   v
Análise com IA
   |
   v
Comparação entre currículo e vaga
   |
   v
Resultado da análise
```

## Principais características

- Processamento e validação de currículos.
- Validação do tamanho do arquivo, quantidade de páginas e conteúdo extraído.
- Análise estrutural do currículo.
- Processamento da descrição da vaga.
- Análise semântica com inteligência artificial.
- Integração com provedores de IA por meio de uma camada de abstração.
- Processamento assíncrono de análises.
- Autenticação e autorização.
- Persistência de dados em SQL Server.
- Testes automatizados.
- Execução local em ambientes Windows e Linux.

## Arquitetura

O projeto é organizado em módulos com responsabilidades específicas:

| Módulo | Responsabilidade |
| --- | --- |
| `MatchCV.Api` | Endpoints HTTP e inicialização da API |
| `MatchCV.Application` | Casos de uso e orquestração |
| `MatchCV.Domain` | Entidades, validações e regras centrais do domínio |
| `MatchCV.Infrastructure` | Persistência e integrações de infraestrutura |
| `MatchCV.AI` | Integração com provedores de inteligência artificial |
| `MatchCV.Parser` | Processamento e extração de documentos |
| `MatchCV.Worker` | Processamento assíncrono de análises |
| `MatchCV.Tests` | Testes automatizados |
| `MatchCV.Db` | Recursos relacionados ao banco de dados |
| `MatchCV.Frontend` | Interface Angular |
| `MatchCV.Docs` | Documentação do projeto |

Consulte [Architecture.md](MatchCV.Docs/Architecture.md) e [Project-Structure.md](MatchCV.Docs/Project-Structure.md).

## Documentação

### Arquitetura e estrutura

- [Arquitetura](MatchCV.Docs/Architecture.md)
- [Estrutura do projeto](MatchCV.Docs/Project-Structure.md)
- [Tecnologias](MatchCV.Docs/Technologies.md)
- [Decisões arquiteturais](MatchCV.Docs/Decisions/Architecture-Decisions.md)

### Backend e integração

- [Backend](MatchCV.Docs/Backend.md)
- [API](MatchCV.Docs/API.md)
- [Integração da API](MatchCV.Docs/API-Integration.md)
- [Frontend](MatchCV.Docs/Frontend.md)
- [Integração com IA](MatchCV.Docs/AI-Integration.md)
- [Processamento de currículos](MatchCV.Docs/Resume-Processing.md)

### Infraestrutura e banco de dados

- [Infraestrutura](MatchCV.Docs/Infrastructure.md)
- [Ambientes](MatchCV.Docs/Environments.md)
- [Banco de dados](MatchCV.Docs/Database.md)
- [CI/CD](MatchCV.Docs/CI-CD.md)
- [Implantação](MatchCV.Docs/Deployment.md)

### Segurança e qualidade

- [Segurança](MatchCV.Docs/Security.md)
- [Privacidade](MatchCV.Docs/Privacy.md)
- [Testes](MatchCV.Docs/Testing.md)
- [Guia de desenvolvimento](MatchCV.Docs/Development-Guide.md)

### Regras e planejamento

- [Regras de negócio](MatchCV.Docs/Business-Rules.md)
- [Roadmap](MatchCV.Docs/Roadmap.md)

## Regras de negócio

As regras de negócio contemplam currículo, descrição da vaga, extração de documentos, inteligência artificial, consultas, usuários, privacidade, segurança, arquitetura e qualidade.

Consulte [Business-Rules.md](MatchCV.Docs/Business-Rules.md).

## Status

O projeto está em desenvolvimento e já possui uma aplicação publicada para acesso. A implementação e a evolução dos módulos são incrementais; consulte o [Roadmap](MatchCV.Docs/Roadmap.md) para acompanhar o planejamento.

## Privacidade

Os currículos enviados ao sistema não devem fazer parte do armazenamento permanente da aplicação. O projeto segue o princípio de minimização de dados, evitando manter informações pessoais além do período necessário para o processamento.

Currículos reais, credenciais e segredos de configuração não devem ser armazenados no repositório.

Consulte [Privacy.md](MatchCV.Docs/Privacy.md).

## Licença

A definir.
