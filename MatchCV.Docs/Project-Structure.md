# Estrutura do Projeto

Este documento descreve a organização do projeto MatchCV e a responsabilidade de cada módulo.

A estrutura foi planejada para separar domínio, aplicação, infraestrutura, processamento de documentos, inteligência artificial, testes e interface.

## Estrutura geral

```text
MatchCV/
├── MatchCV.AI/
│   ├── Exceptions/
│   │   ├── __init__.py
│   │   └── AIProviderException.py
│   ├── Models/
│   │   ├── __init__.py
│   │   ├── AIAnalysisResponse.py
│   │   └── AIProviderConfig.py
│   ├── Providers/
│   │   ├──  __init__.py
│   │   └──SecondaryAIProvider.py
│   └── Services/
│   │   ├── __init__.py
│   │   ├── AIProviderService.py
│   │   ├── AIResponseParser.py
│   │   ├── AnalysisPromptBuilder.py
│   │   └── IAIProvider.py
│   │   └── OpenAICompatibleProvider.py
│   └── __init__.py
├── MatchCV.Api/
├── MatchCV.Application/
│   ├── DTOs/
│   │   ├── AnalysisResult.py
│   │   └── AnalyzeResumeRequest.py
│   ├── Interfaces/
│   │   ├── __init__.py
│   │   └── IAnalysisProvider.py
│   └── UseCases/
│   │   ├── __init__.py
│   │   └── AnalyzeResumeUseCase.py
│   └── __init__.py
├── MatchCV.Db/
│   │   ├── Migrations/
│   │   │   ├── __init__.py
│   │   │   └── 001_initial_schema.sql
│   └── __init__.py
├── MatchCV.Docs/
│   ├── BusinessRules/
│   │   └── business-rules.md
│   ├── Project-Structure.md
│   └── Technologies.md
├── MatchCV.Domain/
│   ├── __init__.py
│   ├── Entities/
│   │   ├── __init__.py
│   │   ├── Analysis.py
│   │   ├── JobDescription.py
│   │   ├── Resume.py
│   │   └── User.py
│   ├── Enums/
│   │   ├── __init__.py
│   │   ├── FileType.py
│   │   └── UserRole.py
│   ├── Exceptions/
│   │   ├── __init__.py
│   │   └── DomainException.py
│   ├── Validation/
│   │   ├── __init__.py
│   │   ├── ProfanityValidator.py
│   │   └── TextContentValidator.py
│   └── ValueObjects/
│   │   └── __init__.py
├── MatchCV.Frontend/
├── MatchCV.Infrastructure/
│   │   ├── __init__.py
│   │   ├── Config/
│   │   │   ├── __init__.py
│   │   │   ├── AISettings.py
│   │   │   └── AppSettings.py
│   │   ├── Database/
│   │   │   ├── __init__.py
│   │   │   └── DatabaseConnection.py
│   │   ├── Repositories/
│   │   │   ├── __init__.py
│   │   │   ├── AnalysisRepository.py
│   │   │   ├── JobDescriptionRepository.py
│   │   │   └── UserRepository.py
│   │   └── Services/
│   │   │   └── __init__.py
├── MatchCV.Parser/
│   ├── __init__.py
│   ├── Exceptions/
│   │   ├── __init__.py
│   │   └── ParserException.py
│   ├── Interfaces/
│   │   ├── __init__.py
│   │   └── IResumeParser.py
│   ├── Models/
│   │   ├── __init__.py
│   │   └── ParsedResume.py
│   ├── Parsers/
│   │   ├── __init__.py
│   │   ├── DocResumeParser.py
│   │   ├── DocxResumeParser.py
│   │   └── PdfResumeParser.py
│   ├── Services/
│   │   ├── __init__.py
│   │   └── ResumeParserService.py
│   └── Validation/
│   │   ├── __init__.py
│   │   ├── Data/
│   │   │   └── __init__.py
│   │   ├── ResumeFileValidator.py
│   │   ├── ResumeStructureValidator.py
├── MatchCV.Tests/
│   ├── Integration/
│   │   ├── Api/
│   │   ├── Database/
│   │   ├── Parser/
│   │   └── Repositories/
│   └── Unit/
│   │   ├── Application/
│   │   ├── Domain/
│   │   └── Parser/
├── MatchCV.Worker/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Responsabilidades

### MatchCV.AI

Responsável pela integração com provedores de inteligência artificial.

Atualmente contém:

* contratos para provedores de IA;
* modelos de respostas estruturadas;
* configuração dos provedores;
* construção dos prompts;
* validação das respostas;
* cliente HTTP;
* provedor principal;
* provedor de fallback;
* coordenação de fallback entre provedores.

O módulo não deve conter regras de negócio específicas da aplicação.

### MatchCV.Api

Responsável pela exposição HTTP da aplicação.

Responsabilidades previstas:

* endpoints;
* recebimento de requisições;
* upload de currículo;
* recebimento da descrição da vaga;
* respostas HTTP;
* autenticação;
* autorização;
* tratamento de erros HTTP.

A API não deve conter as regras principais de negócio nem implementar diretamente o processamento de documentos.

### MatchCV.Application

Responsável pela orquestração dos casos de uso da aplicação.

Atualmente contém:

* contratos para serviços externos utilizados pelos casos de uso;
* DTOs de entrada e saída;
* casos de uso de análise;
* orquestração entre domínio, parser e serviços de IA.

O Application não deve conter detalhes de infraestrutura, HTTP ou implementação concreta de provedores externos.

### MatchCV.Domain

Contém os conceitos e regras centrais do domínio.

Atualmente contém:

* `Analysis`;
* `JobDescription`;
* `Resume`;
* `User`;
* `FileType`;
* `UserRole`;
* `DomainException`;
* `Validation/TextContentValidator`;
* `Validation/ProfanityValidator`.

O domínio não deve depender de infraestrutura externa.

### MatchCV.Infrastructure

Responsável por infraestrutura e integrações externas.

Responsabilidades previstas:

* banco de dados;
* repositórios;
* configuração de infraestrutura;
* serviços externos;
* persistência;
* componentes necessários para integração com recursos externos.

### MatchCV.AI

Responsável pela integração com inteligência artificial.

Responsabilidades previstas:

* contrato dos provedores;
* implementação dos dois provedores;
* seleção do provedor;
* fallback quando aplicável;
* tratamento de erros;
* montagem das solicitações;
* interpretação estruturada das respostas.

A camada de IA não deve substituir o Parser.

### MatchCV.Parser

Responsável pelo processamento e validação específica de documentos de currículo.

Atualmente contém:

* contratos de parser;
* modelos de currículo processado;
* seleção do parser conforme o formato;
* parsers específicos para PDF, DOC e DOCX;
* validação do arquivo recebido;
* validação da estrutura do documento;
* extração de texto;
* identificação de quantidade de páginas;
* verificação de texto extraível;
* identificação de documentos protegidos ou corrompidos;
* identificação de estruturas incompatíveis;
* representação estruturada do currículo processado.

As regras genéricas de domínio, como validação de nome, conteúdo textual e conteúdo inadequado, pertencem ao `MatchCV.Domain`.

### MatchCV.Worker

Responsável por processamentos assíncronos que possam ser retirados do fluxo HTTP principal.

Exemplos futuros:

* processamento de análise;
* processamento de IA;
* tarefas de limpeza;
* remoção de arquivos temporários.

### MatchCV.Tests

Contém os testes do projeto.

#### Unit

Testes isolados de:

* domínio;
* aplicação;
* Parser;
* validações;
* regras de negócio.

#### Integration

Testes de integração de:

* API;
* banco de dados;
* repositórios;
* Parser;
* integrações relevantes.

Testes de IA não devem depender obrigatoriamente de chamadas reais aos provedores.

### MatchCV.Db

Contém recursos relacionados ao banco de dados.

Responsabilidades futuras:

* scripts;
* inicialização;
* migrations, quando aplicável;
* configuração de banco;
* dados técnicos necessários ao ambiente.

### MatchCV.Frontend

Responsável pela interface do usuário.

Responsabilidades futuras:

* upload do currículo;
* entrada da descrição da vaga;
* apresentação dos resultados;
* cadastro de usuários;
* autenticação;
* funcionalidades administrativas.

### MatchCV.Docs

Centraliza a documentação do projeto.

A documentação deve permanecer separada do código de implementação.

## Princípio de organização

Cada módulo deve possuir uma responsabilidade clara.

O crescimento da estrutura não é um problema quando a separação representa responsabilidades reais do sistema.

O objetivo é evitar tanto um projeto monolítico desorganizado quanto a criação de abstrações sem responsabilidade prática.
