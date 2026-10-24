# Integração da API — MatchCV

## 1. Objetivo

Documentar a comunicação entre a API, Application, Parser, AI, Infrastructure, banco de dados e frontend.

## 2. Visão geral

```text
Frontend
   |
   | POST /api/v1/analysis/resume
   v
API
   |
   | valida, extrai texto e cria análise pendente
   v
Application
   |
   +------> SQL Server: analyses + analysis_queue
                 |
                 v
          Worker em thread separada
                 |
                 +------> AI providers
                 |
                 +------> SQL Server: status + resultado
```

## 3. Integração Frontend → API

O frontend enviará:

- Descrição da vaga.
- Arquivo de currículo.
- Credenciais ou token de autenticação, quando aplicável.

A API responde `202 Accepted` com `analysis_id` e status `pending`. O frontend consulta `GET /api/v1/analysis/{analysis_id}` até o status ser `completed` ou `failed`.

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

## 11. Worker assíncrono

A API só inicia a thread do worker quando `RUN_ANALYSIS_WORKER=true`. O worker consulta a fila SQL Server, descriptografa o payload temporário e processa a análise. `ANALYSIS_QUEUE_ENCRYPTION_KEY` deve ser uma chave Fernet válida e igual na API e no worker. A migração `005_analysis_worker_queue.sql` precisa estar aplicada no banco antes de habilitar o processamento assíncrono.

O frontend acompanha o processamento consultando o endpoint autenticado `GET /api/v1/analysis/{analysis_id}`. O endpoint restringe a consulta ao proprietário da análise.

No Render, a execução junto à API é provisória. Reinicializações e suspensão do serviço gratuito interrompem a thread; a fila e a recuperação de leases permitem recuperar tarefas, mas não substituem um worker dedicado em produção.
