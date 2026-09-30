# Estrutura do Projeto

Este documento apresenta a estrutura do projeto MatchCV em sua organização planejada.

A estrutura foi definida para separar responsabilidades entre domínio, aplicação, infraestrutura, processamento de documentos, inteligência artificial, processamento assíncrono, testes, banco de dados, frontend e documentação.

## Estrutura completa

```text
MatchCV/
├── MatchCV.AI/
├── MatchCV.Api/
├── MatchCV.Application/
├── MatchCV.Db/
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
│   │   └── Resume.py
│   ├── Enums/
│   │   ├── __init__.py
│   │   ├── FileType.py
│   │   └── UserRole.py
│   ├── Exceptions/
│   │   ├── __init__.py
│   │   └── DomainException.py
│   └── ValueObjects/
│       └── __init__.py
├── MatchCV.Frontend/
├── MatchCV.Infrastructure/
├── MatchCV.Parser/
│   ├── __init__.py
│   │
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
│   │   └── __init__.py
│   ├── Services/
│   │   ├── __init__.py
│   │   └── ResumeParserService.py
│   └── Validation/
│       ├── __init__.py
│       └── ResumeFileValidator.py
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

## Arquivos da raiz

### `.env.example`

Modelo das variáveis de ambiente necessárias para executar o projeto.

Não deve conter credenciais reais.

### `.gitignore`

Define arquivos e diretórios que não devem ser versionados.

Exemplos:

* `.env`;
* ambientes virtuais;
* arquivos temporários;
* caches;
* arquivos gerados;
* arquivos de build;
* arquivos específicos do sistema operacional.

### `docker-compose.yml`

Configuração dos serviços necessários para o ambiente de desenvolvimento através do Docker Compose.

### `README.md`

Documento principal do projeto.

Apresenta:

* objetivo;
* funcionamento;
* arquitetura;
* principais características;
* documentação;
* status;
* informações gerais de execução.

---

# Módulos

## `MatchCV.AI`

Responsável pela integração com inteligência artificial.

Responsabilidades previstas:

* abstração dos provedores;
* implementação dos dois provedores;
* seleção de provedor;
* fallback quando aplicável;
* tratamento de erros;
* comunicação com APIs externas;
* interpretação estruturada das respostas da IA.

A camada de IA não será responsável pela extração dos documentos.

---

## `MatchCV.Api`

Responsável pela exposição HTTP da aplicação.

Responsabilidades previstas:

* endpoints;
* upload de currículos;
* recebimento da descrição da vaga;
* respostas HTTP;
* autenticação;
* autorização;
* tratamento de erros;
* documentação da API.

A API não deve concentrar regras de negócio ou código de parsing.

---

## `MatchCV.Application`

Responsável pelos casos de uso e pela orquestração da aplicação.

Responsabilidades previstas:

* iniciar análise;
* coordenar validações;
* chamar o Parser;
* chamar a camada de IA;
* coordenar repositórios;
* controlar o fluxo dos casos de uso;
* aplicar regras de aplicação.

---

## `MatchCV.Db`

Responsável pelos recursos relacionados ao banco de dados.

Responsabilidades previstas:

* scripts;
* configuração;
* migrations;
* inicialização;
* recursos necessários ao banco de dados.

O banco de dados principal planejado é o Microsoft SQL Server.

---

## `MatchCV.Docs`

Responsável pela documentação do projeto.

### `BusinessRules/`

Contém as regras de negócio.

```text
MatchCV.Docs/
└── BusinessRules/
    └── business-rules.md
```

### `Project-Structure.md`

Documenta a organização dos arquivos e módulos do projeto.

### `Technologies.md`

Documenta as tecnologias utilizadas ou planejadas.

---

## `MatchCV.Domain`

Contém os conceitos e regras centrais do domínio.

### `Entities/`

Entidades principais do sistema.

```text
Entities/
├── __init__.py
├── Analysis.py
├── JobDescription.py
└── Resume.py
```

#### `Analysis.py`

Representa uma análise entre currículo e descrição de vaga.

#### `JobDescription.py`

Representa a descrição da oportunidade analisada.

#### `Resume.py`

Representa o currículo após suas informações básicas terem sido validadas.

### `Enums/`

Enumerações utilizadas pelo domínio.

```text
Enums/
├── __init__.py
├── FileType.py
└── UserRole.py
```

#### `FileType.py`

Define os formatos de currículo suportados:

* PDF;
* DOC;
* DOCX.

#### `UserRole.py`

Define os papéis de usuário:

* USER;
* ADMIN.

### `Exceptions/`

Exceções específicas do domínio.

```text
Exceptions/
├── __init__.py
└── DomainException.py
```

### `ValueObjects/`

Objetos de valor do domínio.

Novos objetos serão adicionados conforme surgirem necessidades reais do domínio.

---

## `MatchCV.Frontend`

Responsável pela interface de usuário da aplicação.

Responsabilidades previstas:

* upload do currículo;
* entrada da descrição da vaga;
* apresentação dos resultados;
* cadastro;
* autenticação;
* funcionalidades administrativas;
* interação com a API.

A tecnologia definitiva do frontend será registrada em `MatchCV.Docs/Technologies.md`.

---

## `MatchCV.Infrastructure`

Responsável pelas implementações de infraestrutura.

Responsabilidades previstas:

* persistência;
* repositórios;
* acesso ao banco;
* configurações;
* integrações externas;
* serviços de infraestrutura.

Essa camada implementará os contratos necessários definidos pelas camadas superiores.

---

## `MatchCV.Parser`

Responsável exclusivamente pelo processamento e extração das informações dos documentos.

Atualmente:

```text
MatchCV.Parser/
├── __init__.py
│
├── Exceptions/
│   ├── __init__.py
│   └── ParserException.py
│
├── Interfaces/
│   ├── __init__.py
│   └── IResumeParser.py
│
├── Models/
│   ├── __init__.py
│   └── ParsedResume.py
│
├── Parsers/
│   └── __init__.py
│
├── Services/
│   ├── __init__.py
│   └── ResumeParserService.py
│
└── Validation/
    ├── __init__.py
    └── ResumeFileValidator.py
```

### `Exceptions/`

Exceções relacionadas ao processamento dos documentos.

#### `ParserException.py`

Representa erros específicos encontrados durante o processamento de documentos.

### `Interfaces/`

Contratos utilizados pelos parsers.

#### `IResumeParser.py`

Define o contrato comum para os parsers de currículo.

### `Models/`

Modelos de dados produzidos pelo Parser.

#### `ParsedResume.py`

Representa o resultado estruturado do processamento do currículo.

Informações previstas:

* nome do arquivo;
* tipo;
* tamanho;
* quantidade de páginas;
* texto extraído;
* possibilidade de extração de texto;
* estrutura de colunas;
* presença de imagens.

### `Parsers/`

Implementações específicas para cada formato.

Serão adicionados:

* parser PDF;
* parser DOC;
* parser DOCX.

### `Services/`

Serviços responsáveis por coordenar o processamento.

#### `ResumeParserService.py`

Seleciona o parser adequado de acordo com o formato do documento.

### `Validation/`

Validações relacionadas aos arquivos.

#### `ResumeFileValidator.py`

Valida características básicas como:

* nome;
* tamanho;
* extensão;
* formatos permitidos.

Validações estruturais mais avançadas serão adicionadas posteriormente.

---

## `MatchCV.Tests`

Contém os testes automatizados.

```text
MatchCV.Tests/
├── Integration/
│   ├── Api/
│   ├── Database/
│   ├── Parser/
│   └── Repositories/
│
└── Unit/
    ├── Application/
    ├── Domain/
    └── Parser/
```

### `Unit/`

Testes isolados.

#### `Domain/`

Testes das regras e entidades do domínio.

#### `Application/`

Testes dos casos de uso e orquestração.

#### `Parser/`

Testes das validações e componentes do Parser.

### `Integration/`

Testes envolvendo componentes reais integrados.

#### `Api/`

Testes de integração dos endpoints.

#### `Database/`

Testes de integração com o banco de dados.

#### `Parser/`

Testes de integração do processamento dos documentos.

#### `Repositories/`

Testes de integração dos repositórios.

---

## `MatchCV.Worker`

Responsável por processamento assíncrono.

Responsabilidades futuras:

* processamento de análises;
* processamento de IA;
* tarefas de limpeza;
* remoção de arquivos temporários;
* tarefas que não precisam permanecer no fluxo HTTP.

---

# Princípios da estrutura

A estrutura do MatchCV deve crescer conforme surgirem responsabilidades reais.

Não devem ser criados arquivos ou camadas apenas para aumentar artificialmente o tamanho do projeto.

Cada módulo deve possuir responsabilidade definida e suas dependências devem respeitar a arquitetura estabelecida.

O Parser deve permanecer separado da IA.

O domínio deve permanecer independente de infraestrutura.

A API deve permanecer responsável pela exposição HTTP, enquanto os casos de uso ficam na camada Application.

Os testes devem acompanhar a implementação das funcionalidades.
