# Arquitetura — MatchCV

## Visão geral

O MatchCV é uma aplicação modular composta por frontend Angular, API FastAPI, casos de uso, domínio, parser de documentos, integração com IA, persistência SQL Server e processamento assíncrono.

```text
Angular Frontend
      | HTTP
      v
FastAPI (MatchCV.Api)
      |
      v
Application Use Cases ---- Domain rules
      |                         |
      +---- Parser              |
      +---- AI abstraction      |
      +---- Repositories -------+
                 |
             SQL Server
                 ^
                 |
             Worker
```

## Responsabilidades

- **MatchCV.Api:** rotas HTTP, schemas, autenticação, dependências e respostas.
- **MatchCV.Application:** coordenação dos casos de uso e fluxo de análise.
- **MatchCV.Domain:** entidades, enums, validações e regras de negócio.
- **MatchCV.Infrastructure:** conexão SQL Server e repositórios.
- **MatchCV.Parser:** validação de arquivos e extração de texto.
- **MatchCV.AI:** integração com provedores externos e normalização de respostas.
- **MatchCV.Worker:** processamento das análises enfileiradas.
- **MatchCV.Login:** hashing, política de senha, autenticação e autorização.
- **MatchCV.Db:** migrations SQL, incluindo as específicas de testes.
- **MatchCV.Tests:** testes unitários e de integração.
- **MatchCV.Frontend:** interface Angular.

A organização detalhada dos arquivos fica em [Project-Structure.md](Project-Structure.md).

## Fluxo de análise

1. O usuário autenticado envia descrição da vaga e currículo por texto ou arquivo.
2. A API valida a entrada e a cota aplicável.
3. O caso de uso cria e enfileira a análise.
4. A API responde HTTP 202, indicando que a tarefa foi aceita, não concluída.
5. O worker processa a tarefa, usando parser e provedor de IA configurado.
6. O estado e o resultado são persistidos no SQL Server.
7. O proprietário consulta o estado e o resultado pela API.

## Regras arquiteturais

- Regras de negócio não devem depender diretamente de HTTP, banco ou fornecedor de IA.
- Consultas SQL devem ser parametrizadas.
- Currículos e descrições de vagas são dados não confiáveis, não instruções privilegiadas.
- A IA não deve inventar qualificações ou fatos não evidenciados.
- A consulta de uma análise deve verificar a propriedade no backend.
- O arquivo original do currículo deve ser temporário; não deve ser armazenado permanentemente nem registrado integralmente em logs.
- A API e o worker precisam compartilhar a configuração necessária para processar as mesmas tarefas.
- Configurações sensíveis devem vir do ambiente, nunca de credenciais versionadas.

## Persistência e fila

O SQL Server guarda dados de conta, análises, resultados e registros necessários ao processamento assíncrono. As migrations versionadas em `MatchCV.Db/Migrations/` são a fonte de verdade do schema; as migrations específicas do banco de teste ficam em `MatchCV.Db/Migrations/Test/`.

Não se deve presumir que iniciar a API executa automaticamente todas as migrations. Aplique-as em ordem no ambiente correto.

## Autenticação e cota

O backend possui rotas de cadastro, login, consulta do usuário autenticado, alteração de senha, recuperação de senha e bootstrap administrativo protegido. O cadastro público cria usuário comum. Usuários comuns têm cota mensal de três análises; administradores não estão sujeitos a esse limite. Falhas técnicas tratadas pelo fluxo devem liberar a reserva correspondente.

## IA e fallback

A camada de IA abstrai os fornecedores externos. Quando um erro elegível exige fallback, a tentativa alternativa integra a mesma análise e não deve contar como uma nova solicitação do usuário. Credenciais, limites, modelos e disponibilidade dependem do ambiente.

## Operação e testes

O workflow de CI executa testes unitários Python e testes/build do frontend; não executa a suíte completa de integração SQL Server. Consulte [CI-CD.md](CI-CD.md), [Testing.md](Testing.md) e [Environments.md](Environments.md).

Este documento descreve o desenho funcional pretendido e os componentes presentes; não representa garantia de disponibilidade de serviços externos ou certificação de segurança.
