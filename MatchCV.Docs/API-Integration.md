# Integração da API — MatchCV

## 1. Objetivo

Documentar a comunicação entre a API, Application, Parser, AI, Infrastructure, banco de dados e frontend.

## 2. Visão geral

```text
Frontend
   |
   | HTTP / HTTPS
   v
API
   |
   v
Application
   |
   +------> Parser
   |
   +------> AI
   |
   +------> Repositories
                 |
                 v
             SQL Server
```

## 3. Integração Frontend → API

O frontend enviará:

- Descrição da vaga.
- Arquivo de currículo.
- Credenciais ou token de autenticação, quando aplicável.

A API retornará respostas estruturadas em JSON.

## 4. Integração API → Application

A API não deve executar regras de negócio diretamente.

Ela deve invocar os casos de uso da Application.

## 5. Integração Application → Parser

A Application utiliza o contrato IResumeParserService.

A implementação concreta deve ser fornecida por um adaptador externo.

## 6. Integração Application → AI

A Application utiliza uma abstração de análise.

A implementação concreta coordena os provedores de IA.

## 7. Integração Application → Infrastructure

Os repositórios são acessados por interfaces definidas na Application.

Infrastructure implementa esses contratos.

## 8. Integração com SQL Server

A comunicação utiliza `pyodbc`.

Consultas devem utilizar parâmetros.

## 9. Falhas de integração

Devem ser previstas falhas de:

- Banco de dados.
- Parser.
- Provedor principal de IA.
- Provedor de fallback.
- Comunicação HTTP.
- Autenticação.

## 10. Segurança

Dados recebidos de currículos e descrições de vaga devem ser tratados como conteúdo não confiável.

O conteúdo não pode sobrescrever instruções de sistema ou regras de segurança do modelo de IA.

## 11. Status

O fluxo descreve a integração arquitetural prevista. A composição concreta das dependências será concluída na camada API.
