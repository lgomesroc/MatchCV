# Infraestrutura do MatchCV

## 1. Objetivo

Este documento descreve os componentes técnicos responsáveis
por configuração, persistência, conexão com serviços e execução
do ambiente.

## 2. Tecnologias

| Componente | Tecnologia |
|---|---|
| Linguagem principal | Python |
| Banco de dados | Microsoft SQL Server |
| Containerização | Docker |
| Driver Python | pyodbc |
| Configuração | Variáveis de ambiente |
| Controle de versão | Git |
| Repositório remoto | GitHub |

## 3. Organização

```text
MatchCV.Infrastructure/
├── Config/
│   ├── AISettings.py
│   └── AppSettings.py
├── Database/
│   └── DatabaseConnection.py
├── Models/
│   ├── AnalysisRecord.py
│   ├── JobDescriptionRecord.py
│   └── UserRecord.py
├── Repositories/
│   ├── SqlServerAnalysisRepository.py
│   ├── SqlServerJobDescriptionRepository.py
│   └── SqlServerUserRepository.py
└── Services/
    ├── AIAnalysisProvider.py
    └── ResumeParserAdapter.py
```
A estrutura representa a organização prevista dos componentes. A disponibilidade efetiva de cada funcionalidade depende da implementação correspondente.
