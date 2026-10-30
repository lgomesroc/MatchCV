# Estrutura do Projeto

Este documento descreve a organização do projeto MatchCV e a responsabilidade de cada módulo.

A estrutura foi planejada para separar domínio, aplicação, infraestrutura, processamento de documentos, inteligência artificial, testes e interface.

## Estrutura geral

```text
MatchCV/
├── .dockerignore
├── .env.example
├── .github/
│   └── workflows/
│       ├── cd.yml
│       ├── ci.yml
│       └── sql-server-integration.yml
├── .gitignore
├── docker-compose.test.yml
├── docker-compose.yml
├── Dockerfile
├── Docs/
│   └── test-job-description.txt
├── MatchCV/
│   └── __init__.py
├── MatchCV.AI/
│   ├── __init__.py
│   ├── Exceptions/
│   │   ├── __init__.py
│   │   └── AIProviderException.py
│   ├── Models/
│   │   ├── __init__.py
│   │   ├── AIAnalysisResponse.py
│   │   └── AIProviderConfig.py
│   ├── Providers/
│   │   ├── __init__.py
│   │   ├── DevelopmentAIProvider.py
│   │   ├── OpenAICompatibleProvider.py
│   │   └── SecondaryAIProvider.py
│   └── Services/
│       ├── __init__.py
│       ├── AIHttpClient.py
│       ├── AIProviderService.py
│       ├── AIResponseParser.py
│       ├── AnalysisPromptBuilder.py
│       └── IAIProvider.py
├── MatchCV.Api/
│   ├── __init__.py
│   ├── Dependencies/
│   │   ├── __init__.py
│   │   └── AnalysisDependencies.py
│   ├── main.py
│   ├── Routers/
│   │   ├── __init__.py
│   │   ├── AnalysisRouter.py
│   │   ├── AuthRouter.py
│   │   └── PasswordResetRouter.py
│   └── Schemas/
│       ├── __init__.py
│       ├── AnalysisResponse.py
│       ├── AuthSchemas.py
│       └── ErrorResponse.py
├── MatchCV.Application/
│   ├── __init__.py
│   ├── DTOs/
│   │   ├── __init__.py
│   │   ├── AnalysisResult.py
│   │   ├── AnalyzeResumeRequest.py
│   │   └── ParsedResumeResult.py
│   ├── Interfaces/
│   │   ├── __init__.py
│   │   ├── IAnalysisProvider.py
│   │   └── IResumeParserService.py
│   ├── Queue/
│   │   ├── __init__.py
│   │   ├── AnalysisQueueItem.py
│   │   ├── AnalysisQueuePayload.py
│   │   └── IAnalysisQueueRepository.py
│   ├── Repositories/
│   │   ├── __init__.py
│   │   ├── IAnalysisRepository.py
│   │   ├── IJobDescriptionRepository.py
│   │   └── IUserRepository.py
│   └── UseCases/
│       ├── __init__.py
│       └── AnalyzeResumeUseCase.py
├── MatchCV.Db/
│   ├── __init__.py
│   └── Migrations/
│       ├── __init__.py
│       ├── 001_initial_schema.sql
│       ├── 002_user_analysis_usage.sql
│       ├── 003_unique_admin.sql
│       ├── 004_analysis_history.sql
│       ├── 005_analysis_worker_queue.sql
│       ├── 006_password_reset_tokens.sql
│       ├── 007_admin_password_policy.sql
│       ├── 008_analysis_quota_reservations.sql
│       ├── 009_job_description_text_limit.sql
│       └── Test/
│           ├── 001_initial_schema.sql
│           ├── 002_user_analysis_usage.sql
│           ├── 003_unique_admin.sql
│           ├── 004_analysis_history.sql
│           ├── 005_analysis_worker_queue.sql
│           ├── 006_password_reset_tokens.sql
│           ├── 007_admin_password_policy.sql
│           ├── 008_analysis_quota_reservations.sql
│           └── 009_job_description_text_limit.sql
├── MatchCV.Docs/
│   ├── AI-Integration.md
│   ├── Analysis-Polling-Timeout.md
│   ├── API-Integration.md
│   ├── API.md
│   ├── Architecture.md
│   ├── Backend.md
│   ├── Business-Rules.md
│   ├── BusinessRules/
│   │   └── business-rules.md
│   ├── CI-CD.md
│   ├── Data-Retention-and-Deletion.md
│   ├── Database.md
│   ├── Decisions/
│   │   └── Architecture-Decisions.md
│   ├── Deployment.md
│   ├── Development-Guide.md
│   ├── Environments.md
│   ├── Frontend.md
│   ├── Getting-Started.md
│   ├── Infrastructure.md
│   ├── Live-Service-Validation.md
│   ├── Password-Recovery.md
│   ├── Privacy.md
│   ├── Project-Structure.md
│   ├── README.md
│   ├── Real-Services-E2E-Validation.md
│   ├── Resume-Processing.md
│   ├── Roadmap.md
│   ├── Security.md
│   ├── Technologies.md
│   └── Testing.md
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
│   │   ├── AnalysisStatus.py
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
│       └── __init__.py
├── MatchCV.Frontend/
│   ├── .editorconfig
│   ├── .gitignore
│   ├── .prettierrc
│   ├── angular.json
│   ├── e2e/
│   │   ├── analysis-states.spec.ts
│   │   ├── analysis.spec.ts
│   │   ├── live-services.spec.ts
│   │   ├── login.spec.ts
│   │   └── registration.spec.ts
│   ├── package-lock.json
│   ├── package.json
│   ├── playwright.config.ts
│   ├── public/
│   │   └── favicon.ico
│   ├── README.md
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.config.ts
│   │   │   ├── app.html
│   │   │   ├── app.routes.ts
│   │   │   ├── app.scss
│   │   │   ├── app.spec.ts
│   │   │   ├── app.ts
│   │   │   ├── core/
│   │   │   │   ├── guards/
│   │   │   │   │   ├── auth.guard.spec.ts
│   │   │   │   │   └── auth.guard.ts
│   │   │   │   ├── interceptors/
│   │   │   │   │   ├── auth.interceptor.spec.ts
│   │   │   │   │   └── auth.interceptor.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── analysis-response.ts
│   │   │   │   │   └── auth.ts
│   │   │   │   └── services/
│   │   │   │       ├── analysis.service.spec.ts
│   │   │   │       ├── analysis.service.ts
│   │   │   │       ├── auth.service.spec.ts
│   │   │   │       ├── auth.service.ts
│   │   │   │       └── memory-cache.service.ts
│   │   │   └── features/
│   │   │       ├── analysis/
│   │   │       │   ├── analysis.html
│   │   │       │   ├── analysis.scss
│   │   │       │   ├── analysis.spec.ts
│   │   │       │   ├── analysis.ts
│   │   │       │   └── components/
│   │   │       │       ├── analysis-failed/
│   │   │       │       │   ├── analysis-failed.html
│   │   │       │       │   ├── analysis-failed.scss
│   │   │       │       │   └── analysis-failed.ts
│   │   │       │       ├── analysis-input/
│   │   │       │       │   ├── analysis-input.html
│   │   │       │       │   ├── analysis-input.scss
│   │   │       │       │   └── analysis-input.ts
│   │   │       │       ├── analysis-processing/
│   │   │       │       │   ├── analysis-processing.html
│   │   │       │       │   ├── analysis-processing.scss
│   │   │       │       │   └── analysis-processing.ts
│   │   │       │       └── analysis-result/
│   │   │       │           ├── analysis-result.html
│   │   │       │           ├── analysis-result.scss
│   │   │       │           └── analysis-result.ts
│   │   │       ├── change-password/
│   │   │       │   ├── change-password.html
│   │   │       │   ├── change-password.scss
│   │   │       │   ├── change-password.spec.ts
│   │   │       │   └── change-password.ts
│   │   │       ├── forgot-password/
│   │   │       │   ├── forgot-password.html
│   │   │       │   ├── forgot-password.scss
│   │   │       │   ├── forgot-password.spec.ts
│   │   │       │   └── forgot-password.ts
│   │   │       ├── login/
│   │   │       │   ├── login.html
│   │   │       │   ├── login.scss
│   │   │       │   ├── login.spec.ts
│   │   │       │   └── login.ts
│   │   │       └── register/
│   │   │           ├── register.html
│   │   │           ├── register.scss
│   │   │           ├── register.spec.ts
│   │   │           └── register.ts
│   │   ├── environments/
│   │   │   ├── environment.production.ts
│   │   │   └── environment.ts
│   │   ├── index.html
│   │   ├── main.ts
│   │   └── styles.scss
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   └── tsconfig.spec.json
├── MatchCV.Infrastructure/
│   ├── __init__.py
│   ├── Config/
│   │   ├── __init__.py
│   │   ├── AISettings.py
│   │   └── AppSettings.py
│   ├── Database/
│   │   ├── __init__.py
│   │   └── DatabaseConnection.py
│   ├── Email/
│   │   └── PasswordResetEmailSender.py
│   ├── Models/
│   │   ├── __init__.py
│   │   ├── AnalysisRecord.py
│   │   ├── JobDescriptionRecord.py
│   │   └── UserRecord.py
│   ├── Repositories/
│   │   ├── __init__.py
│   │   ├── SqlServerAnalysisQueueRepository.py
│   │   ├── SqlServerAnalysisRepository.py
│   │   ├── SqlServerAnalysisUsageRepository.py
│   │   ├── SqlServerJobDescriptionRepository.py
│   │   ├── SqlServerPasswordResetRepository.py
│   │   └── SqlServerUserRepository.py
│   ├── Security/
│   │   ├── __init__.py
│   │   └── AnalysisPayloadEncryption.py
│   └── Services/
│       ├── __init__.py
│       ├── AIAnalysisProvider.py
│       ├── PasswordResetEmailSender.py
│       └── ResumeParserAdapter.py
├── MatchCV.Login/
│   ├── __init__.py
│   ├── Authentication/
│   │   ├── __init__.py
│   │   ├── AuthenticationService.py
│   │   ├── PasswordHasher.py
│   │   ├── PasswordPolicy.py
│   │   └── PasswordRecoveryPolicy.py
│   ├── Authorization/
│   │   ├── __init__.py
│   │   ├── CurrentUser.py
│   │   └── RoleChecker.py
│   ├── Dependencies/
│   │   ├── __init__.py
│   │   └── AuthDependencies.py
│   └── Tokens/
│       ├── __init__.py
│       └── TokenService.py
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
│       ├── __init__.py
│       ├── Data/
│       │   └── __init__.py
│       ├── ResumeFileValidator.py
│       └── ResumeStructureValidator.py
├── MatchCV.Script/
│   ├── change_admin_password.py
│   ├── create_admin.py
│   └── reset_admin_password.py
├── MatchCV.Tests/
│   ├── __init__.py
│   ├── Integration/
│   │   ├── __init__.py
│   │   ├── Api/
│   │   │   ├── __init__.py
│   │   │   ├── test_analysis_router.py
│   │   │   ├── test_analysis_upload_cleanup.py
│   │   │   ├── test_api_contract.py
│   │   │   ├── test_auth_router.py
│   │   │   ├── test_health_endpoint.py
│   │   │   ├── test_password_reset_router.py
│   │   │   └── test_swagger_security.py
│   │   ├── conftest.py
│   │   ├── Database/
│   │   │   ├── __init__.py
│   │   │   ├── test_database_connection.py
│   │   │   └── test_database_schema.py
│   │   ├── Parser/
│   │   │   ├── __init__.py
│   │   │   ├── test_real_resume_files.py
│   │   │   └── test_resume_parsing_pipeline.py
│   │   ├── Repositories/
│   │   │   ├── __init__.py
│   │   │   ├── repository_test_fixtures.py
│   │   │   ├── test_sql_server_analysis_repository.py
│   │   │   ├── test_sql_server_job_description_repository.py
│   │   │   ├── test_sql_server_user_repository.py
│   │   │   └── test_sql_server_workflow_persistence.py
│   │   └── TestDatabase/
│   │       ├── test_connection.py
│   │       ├── test_database_fixtures.py
│   │       └── test_schema.py
│   └── Unit/
│       ├── __init__.py
│       ├── AI/
│       │   └── test_ai_representative_cases.py
│       ├── Application/
│       │   ├── __init__.py
│       │   ├── test_analysis_result.py
│       │   ├── test_analyze_resume_request.py
│       │   ├── test_analyze_resume_use_case.py
│       │   ├── test_async_analysis_enqueue.py
│       │   ├── test_interfaces.py
│       │   └── test_parsed_resume_result.py
│       ├── Domain/
│       │   ├── __init__.py
│       │   ├── test_analysis.py
│       │   ├── test_job_description.py
│       │   ├── test_profanity_validator.py
│       │   ├── test_resume.py
│       │   └── test_text_content_validator.py
│       ├── Infrastructure/
│       │   └── test_password_reset_email_sender.py
│       ├── Login/
│       │   ├── test_authentication_service.py
│       │   ├── test_current_user_authorization.py
│       │   ├── test_password_hasher.py
│       │   ├── test_password_policy.py
│       │   ├── test_password_recovery_policy.py
│       │   ├── test_role_checker.py
│       │   └── test_token_service.py
│       ├── Parser/
│       │   ├── __init__.py
│       │   ├── test_doc_resume_parser.py
│       │   ├── test_docx_resume_parser.py
│       │   ├── test_parsed_resume.py
│       │   ├── test_pdf_resume_parser.py
│       │   ├── test_resume_file_validator.py
│       │   ├── test_resume_parser_service.py
│       │   └── test_resume_structure_validator.py
│       └── Worker/
│           └── test_analysis_worker.py
├── MatchCV.Worker/
│   ├── __init__.py
│   └── AnalysisWorker.py
├── README.md
├── requirements.txt
└── scripts/
    ├── ci_apply_test_migrations.py
    └── smoke_test_live_flow.py
```

## Organização da documentação

A documentação está separada por assunto para facilitar manutenção, consulta e evolução.

- `AI-Integration.md`: integração com provedores de inteligência artificial.
- `API.md`: contratos e endpoints da API.
- `API-Integration.md`: comunicação entre os componentes.
- `Architecture.md`: arquitetura e dependências entre camadas.
- `Backend.md`: organização e responsabilidades do backend.
- `BusinessRules/`: regras de negócio detalhadas.
- `CI-CD.md`: integração e entrega contínuas.
- `Database.md`: estrutura e persistência de dados.
- `Decisions/`: decisões arquiteturais registradas.
- `Deployment.md`: implantação e publicação.
- `Development-Guide.md`: orientações para desenvolvimento.
- `Environments.md`: configuração dos ambientes.
- `Frontend.md`: estrutura da interface.
- `Infrastructure.md`: componentes de infraestrutura.
- `Privacy.md`: privacidade e tratamento de dados.
- `README.md`: índice da documentação.
- `Resume-Processing.md`: processamento de currículos.
- `Roadmap.md`: planejamento de evolução.
- `Security.md`: requisitos de segurança.
- `Technologies.md`: tecnologias adotadas.
- `Testing.md`: estratégia de testes.

## Responsabilidades

| Módulo | Responsabilidade |
|---|---|
| `MatchCV.AI` | Integração com provedores de IA |
| `MatchCV.Api` | Exposição dos endpoints HTTP |
| `MatchCV.Application` | Casos de uso, contratos e DTOs |
| `MatchCV.Docs` | Documentação técnica, funcional e arquitetural |
| `MatchCV.Db` | Scripts e migrações do banco |
| `MatchCV.Frontend` | Interface do candidato |
| `MatchCV.Domain` | Entidades, regras e conceitos centrais |
| `MatchCV.Infrastructure` | Banco de dados, repositórios e serviços externos |
| `MatchCV.Parser` | Validação e extração de documentos |
| `MatchCV.Worker` | Execução do processamento assíncrono de análises |
| `MatchCV.Tests` | Testes unitários e de integração |

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

Responsável pela execução do processamento assíncrono de análises, retirando o trabalho pesado do fluxo HTTP principal.

Atualmente contém o worker de análise. A arquitetura também permite evoluções como:

* processamento adicional de tarefas de IA;
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

Contém os scripts SQL versionados de criação e evolução do schema, incluindo migrations específicas para o ambiente de teste.

Responsabilidades:

* migrations de produção;
* migrations isoladas para testes;
* versionamento da evolução do banco de dados.

### MatchCV.Frontend

Responsável pela interface Angular do usuário, incluindo a experiência de análise, autenticação e recuperação de senha.

Responsabilidades:

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

1. Separação de responsabilidades.
2. Baixo acoplamento entre módulos.
3. Dependências direcionadas às abstrações.
4. Regras de negócio independentes de infraestrutura.
5. Tratamento de documentos sem armazenamento permanente do currículo original.
6. Documentação atualizada conforme a implementação.
7. Compatibilidade de desenvolvimento com Windows e Linux.

## Estado do projeto

O MatchCV encontra-se em desenvolvimento.

A presença de um módulo ou documento nesta estrutura não significa que toda a funcionalidade correspondente esteja implementada ou validada.

