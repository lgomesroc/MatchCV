# Banco de Dados — MatchCV

## 1. Objetivo

O MatchCV utiliza Microsoft SQL Server para persistência dos dados da aplicação.

O banco é executado localmente durante o desenvolvimento através de Docker.

## 2. Tecnologia

| Item                        | Tecnologia           |
| --------------------------- | -------------------- |
| SGBD                        | Microsoft SQL Server |
| Versão                      | SQL Server 2022      |
| Ambiente de desenvolvimento | Docker               |
| Driver Python               | pyodbc               |
| Linguagem de consulta       | T-SQL                |
| Banco                       | MatchCV              |
| Schema                      | dbo                  |

## 3. Princípios de persistência

* Utilizar identificadores UUID.
* Utilizar `DATETIME2` para datas e horários.
* Armazenar datas de referência em UTC.
* Utilizar parâmetros nas consultas SQL.
* Evitar persistência desnecessária de dados pessoais.
* Não armazenar permanentemente o arquivo original do currículo.
* Não registrar conteúdo integral de currículos em logs.
* Utilizar transações quando uma operação envolver múltiplas alterações relacionadas.

## 4. Modelo de dados

O modelo inicial contempla três tabelas principais:

* `dbo.users`
* `dbo.job_descriptions`
* `dbo.analyses`

## 5. Banco

Nome padrão:

```text
MatchCV
```

## 6. Configuração

As informações de conexão são fornecidas por variáveis de ambiente.

```text
DATABASE_HOST=localhost
DATABASE_PORT=1433
DATABASE_NAME=MatchCV
DATABASE_USER=sa
DATABASE_PASSWORD=<senha>
```

A senha real não deve ser armazenada no repositório.

## 7. String de conexão

O formato utilizado pela aplicação segue o padrão:

```text
DRIVER={ODBC Driver 18 for SQL Server};
SERVER=host,port;
DATABASE=name;
UID=user;
PWD=password;
Encrypt=no;
TrustServerCertificate=yes;
```

Os valores devem ser obtidos das configurações do ambiente.

## 8. Tabela users

Armazena os dados de identificação e controle de acesso dos usuários.

| Campo         | Tipo SQL Server  | Descrição                |
| ------------- | ---------------- | ------------------------ |
| id            | UNIQUEIDENTIFIER | Identificador do usuário |
| name          | NVARCHAR(150)    | Nome                     |
| email         | NVARCHAR(255)    | E-mail                   |
| password_hash | NVARCHAR(255)    | Hash da senha            |
| role          | NVARCHAR(30)     | Perfil de acesso         |
| created_at    | DATETIME2        | Data de criação          |
| updated_at    | DATETIME2        | Última atualização       |

### Regras

* O e-mail deve possuir unicidade.
* Senhas nunca devem ser armazenadas em texto puro.
* O perfil ADMIN deve possuir permissões administrativas.
* O perfil USER deve possuir permissões comuns.
* O cadastro público não deve permitir a criação de administradores.

## 9. Tabela job_descriptions

Armazena a descrição da vaga utilizada em uma análise.

| Campo      | Tipo SQL Server  | Descrição                  |
| ---------- | ---------------- | -------------------------- |
| id         | UNIQUEIDENTIFIER | Identificador da descrição |
| content    | NVARCHAR(MAX)    | Conteúdo da vaga           |
| created_at | DATETIME2        | Data de criação            |

### Regras

* O conteúdo deve ser validado antes da persistência.
* O tamanho permitido é de 30 a 3000 caracteres úteis, conforme as regras de negócio.
* O conteúdo não deve ser tratado como instrução de sistema para o modelo de IA.

## 10. Tabela analyses

Armazena o estado e o resultado de uma análise.

| Campo                    | Tipo SQL Server  | Descrição                                           |
| ------------------------ | ---------------- | --------------------------------------------------- |
| id                       | UNIQUEIDENTIFIER | Identificador da análise                            |
| resume_id                | UNIQUEIDENTIFIER | Identificador de referência do currículo processado |
| job_description_id       | UNIQUEIDENTIFIER | Referência à descrição da vaga                      |
| status                   | NVARCHAR(30)     | Estado da análise                                   |
| evidenced_requirements   | NVARCHAR(MAX)    | Requisitos evidenciados                             |
| unevidenced_requirements | NVARCHAR(MAX)    | Requisitos sem evidência                            |
| gaps                     | NVARCHAR(MAX)    | Lacunas identificadas                               |
| resume_issues            | NVARCHAR(MAX)    | Problemas do currículo                              |
| suggestions              | NVARCHAR(MAX)    | Sugestões                                           |
| created_at               | DATETIME2        | Data de criação                                     |
| updated_at               | DATETIME2        | Última atualização                                  |

Os campos que representam listas podem ser serializados como JSON em `NVARCHAR(MAX)`.

## 11. Relacionamentos

```text
dbo.job_descriptions
        │
        │ 1:N
        ▼
   dbo.analyses

dbo.users
        │
        └── Relacionamento com análises de usuários
            a definir na evolução do modelo
```

A associação explícita entre usuário e análise deverá ser definida na evolução do schema, antes da implementação de consultas autenticadas por usuário.

## 12. Estados da análise

Estados previstos:

* PENDING
* PROCESSING
* COMPLETED
* FAILED

As transições devem ser controladas pela entidade de domínio `Analysis`.

## 13. Retenção e privacidade

O MatchCV não deve manter o arquivo original do currículo permanentemente.

A retenção dos textos extraídos e resultados deverá respeitar a política de privacidade e as regras de negócio definidas para a aplicação.

A persistência de resultados não deve implicar armazenamento automático do documento original.

## 14. Migrações

As alterações de schema devem ser versionadas em:

`MatchCV.Db/Migrations/`

Cada migração deve:

* Possuir identificação sequencial.
* Ser revisada antes da execução.
* Ser compatível com SQL Server.
* Evitar perda acidental de dados.
* Ser acompanhada de atualização deste documento.

## 15. Backup e recuperação

Os ambientes de homologação e produção devem possuir estratégia de backup e recuperação compatível com a criticidade dos dados.

O volume Docker local é destinado ao desenvolvimento e não substitui uma política de backup de produção.

## 16. Segurança

* Utilizar credenciais fora do repositório.
* Não expor a porta do banco publicamente sem necessidade.
* Utilizar consultas parametrizadas.
* Restringir permissões do usuário de banco.
* Não registrar senhas ou conteúdo sensível em logs.

## 17. Situação

Este documento descreve o modelo inicial e as diretrizes de persistência. O schema efetivamente implementado deve permanecer sincronizado com as migrações SQL.
