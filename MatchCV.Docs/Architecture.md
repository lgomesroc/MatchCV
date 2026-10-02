# MatchCV — Arquitetura

## 1. Objetivo

Este documento descreve a arquitetura do MatchCV, suas principais camadas,
responsabilidades, dependências e fluxo de comunicação entre os componentes.

O objetivo da arquitetura é manter separadas as regras de negócio, o
processamento de documentos, a persistência de dados, as integrações externas
e as interfaces de entrada e saída da aplicação.

---

## 2. Visão arquitetural

O MatchCV utiliza uma arquitetura modular baseada na separação de
responsabilidades.

```text
                         ┌──────────────────────┐
                         │  MatchCV.Frontend     │
                         │      Interface        │
                         └──────────┬───────────┘
                                    │ HTTP
                                    ▼
                         ┌──────────────────────┐
                         │     MatchCV.Api      │
                         │    Endpoints HTTP    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                       ┌────────────────────────┐
                       │ MatchCV.Application     │
                       │                        │
                       │ Use Cases              │
                       │ DTOs                   │
                       │ Interfaces             │
                       └───────────┬────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
          ┌────────────────┐ ┌────────────┐ ┌───────────────┐
          │ MatchCV.Domain │ │ MatchCV.AI │ │ MatchCV.Parser │
          │                │ │            │ │               │
          │ Entities       │ │ Providers  │ │ PDF/DOC/DOCX  │
          │ Rules          │ │ Services   │ │ Validation    │
          │ Enums          │ │            │ │ Extraction    │
          └────────────────┘ └────────────┘ └───────────────┘
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │ MatchCV.Infrastructure│
                         │                      │
                         │ Repositories         │
                         │ Database             │
                         │ External Services    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      SQL Server      │
                         └──────────────────────┘
```

## 3. Camadas
### 3.1 MatchCV.Api

Responsável pela entrada HTTP da aplicação.

Responsabilidades:

- Receber requisições HTTP.
- Validar dados básicos de entrada.
- Encaminhar solicitações para a camada Application.
- Retornar respostas HTTP.
- Configurar middleware.
- Configurar tratamento de exceções.
- Expor documentação da API quando implementada.

A camada API não deve conter regras de negócio complexas.

### 3.2 MatchCV.Application

Contém os casos de uso da aplicação.

Responsabilidades:

- Orquestrar operações.
- Definir DTOs.
- Definir interfaces utilizadas pelos casos de uso.
- Coordenar Parser, IA e persistência por meio de abstrações.
- Aplicar regras relacionadas ao fluxo da aplicação.

A camada Application não deve depender diretamente de detalhes de infraestrutura.

### 3.3 MatchCV.Domain

Representa o núcleo conceitual do sistema.

Responsabilidades:

- Entidades.
- Enums.
- Value Objects.
- Exceções de domínio.
- Regras que pertencem diretamente ao domínio.

A camada Domain deve permanecer independente de:

- Banco de dados.
- Framework web.
- Provedores de IA.
- Sistema operacional.
- Interface gráfica.

### 3.4 MatchCV.Infrastructure

Implementa detalhes técnicos necessários para a aplicação funcionar.

Responsabilidades:

- Acesso ao SQL Server.
- Repositórios.
- Configuração de conexão.
- Serviços externos.
- Adaptadores.
- Implementações das interfaces definidas nas camadas superiores.

A infraestrutura pode depender de bibliotecas e serviços externos.

### 3.5 MatchCV.Parser

Responsável pelo processamento dos documentos de currículo.

Responsabilidades:

- Identificação do tipo de arquivo.
- Validação do arquivo.
- Extração de texto.
- Contagem de páginas.
- Verificações estruturais.
- Detecção de condições incompatíveis com o processamento da V1.

Formatos previstos:

- PDF.
- DOC.
- DOCX.

O Parser não deve decidir se o candidato atende ou não aos requisitos da vaga.

### 3.6 MatchCV.AI

Responsável pela integração com provedores de inteligência artificial.

Responsabilidades:

- Definir contratos de integração.
- Implementar provedores.
- Enviar dados necessários para análise.
- Processar respostas.
- Normalizar resultados.
- Permitir mecanismo de provedor primário e fallback.

A IA não deve inventar experiências, qualificações, empresas,
certificações ou resultados que não estejam presentes nas informações
fornecidas.

### 3.7 MatchCV.Worker

Responsável por processamento assíncrono quando essa funcionalidade estiver
implementada.

Possíveis responsabilidades:

- Processamento de tarefas demoradas.
- Execução de análises assíncronas.
- Processamento de filas.
- Execução de tarefas em segundo plano.

A utilização efetiva do Worker depende da evolução da aplicação.

### 3.8 MatchCV.Frontend

Responsável pela interface utilizada pelo candidato.

Responsabilidades previstas:

- Upload do currículo.
- Entrada da descrição da vaga.
- Exibição de validações.
- Exibição do resultado da análise.
- Exibição de requisitos identificados.
- Exibição de lacunas.
- Exibição de sugestões de melhoria.

O frontend não deve ser responsável pela implementação das regras de negócio
principais.

## 4. Dependências entre camadas

As dependências devem seguir uma direção previsível.

```text
Api
 │
 ▼
Application
 │
 ├──────────────► Domain
 │
 ├──────────────► Parser (por abstração/adaptação)
 │
 └──────────────► AI (por abstração)
                       ▲
                       │
Infrastructure ────────┘
```

O objetivo é evitar que uma camada superior fique diretamente acoplada a
detalhes de implementação.

## 5. Regra de dependência

As regras de negócio não devem depender diretamente de:

- SQL Server.
- Docker.
- Sistema de arquivos.
- HTTP.
- Provedores específicos de IA.
- Frameworks de apresentação.

Quando uma integração externa for necessária, deve ser utilizada uma
abstração.

Exemplo conceitual:

```text
Application
    │
    ▼
IResumeParserService
    ▲
    │
ResumeParserAdapter
    │
    ▼
MatchCV.Parser
```

Dessa forma, a camada Application conhece o contrato, enquanto a implementação
concreta fica fora dela.

## 6. Fluxo de análise

O fluxo principal previsto é:

```text
1. Usuário envia currículo
           │
           ▼
2. API recebe arquivo
           │
           ▼
3. Validação inicial
           │
           ▼
4. Parser identifica o formato
           │
           ▼
5. Parser extrai o texto
           │
           ▼
6. Validação estrutural
           │
           ▼
7. Usuário informa a descrição da vaga
           │
           ▼
8. Sistema valida a descrição
           │
           ▼
9. Sistema normaliza os dados
           │
           ▼
10. IA realiza análise semântica
           │
           ▼
11. Sistema compara currículo e vaga
           │
           ▼
12. Resultado estruturado
           │
           ▼
13. API retorna resultado
           │
           ▼
14. Frontend apresenta a análise
```

## 7. Isolamento do currículo

O currículo enviado pelo usuário deve ser tratado como dado temporário.

A aplicação deve evitar armazenamento permanente do arquivo original,
conforme as regras de privacidade definidas no projeto.

O conteúdo do currículo também não deve ser registrado em logs.

## 8. Persistência

A aplicação utiliza SQL Server como banco de dados.

A infraestrutura de persistência é responsável por:

- Conexão com o banco.
- Execução de consultas.
- Persistência das entidades necessárias.
- Recuperação dos dados.
- Controle de transações quando aplicável.

O acesso ao banco deve permanecer isolado na camada de infraestrutura.

## 9. Inteligência artificial

A integração com IA deve ser realizada por meio de abstrações.

Estrutura conceitual:

```text
Application
      │
      ▼
IA Provider Interface
      │
      ├──────────► Primary Provider
      │
      └──────────► Fallback Provider
```

O provedor secundário não representa uma segunda consulta independente para
fins de negócio.

Quando uma análise precisar de fallback por erro transitório elegível,
a tentativa alternativa pertence à mesma operação de análise.

## 10. Tratamento de erros

Os erros devem ser classificados de acordo com sua origem.

Exemplos:

- Arquivo inválido.
- Formato não suportado.
- Arquivo acima do limite permitido.
- Documento protegido.
- Texto insuficiente.
- Descrição de vaga inválida.
- Erro de banco.
- Erro de integração.
- Erro temporário do provedor de IA.
- Erro interno da aplicação.

A API deve converter erros internos em respostas apropriadas sem expor
informações sensíveis ou detalhes desnecessários da implementação.

## 11. Segurança arquitetural

A arquitetura deve considerar:

- Validação de entrada.
- Limitação de tamanho dos arquivos.
- Controle de tipos de arquivo.
- Não exposição de credenciais.
- Variáveis de ambiente para configurações sensíveis.
- Não registro do conteúdo do currículo em logs.
- Controle de acesso quando autenticação for implementada.
- Separação entre usuário comum e administrador quando essa funcionalidade estiver implementada.

## 12. Evolução arquitetural

A arquitetura deve permitir a evolução do projeto sem exigir alterações
estruturais desnecessárias.

Possíveis evoluções:

- Autenticação.
- Autorização.
- Frontend completo.
- Processamento assíncrono.
- Novos provedores de IA.
- Novos formatos de documentos.
- Observabilidade.
- Cache.
- Filas.
- Deploy em ambiente de produção.

Essas funcionalidades devem ser incorporadas somente quando realmente
necessárias ao estágio do projeto.

## 13. Status

Este documento descreve a arquitetura atual e os componentes planejados.

Funcionalidades marcadas como futuras ou dependentes de implementação não
devem ser interpretadas como concluídas.
