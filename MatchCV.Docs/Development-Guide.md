# Guia de Desenvolvimento — MatchCV

## 1. Objetivo

Orientar a preparação do ambiente e o desenvolvimento do MatchCV.

## 2. Requisitos

- Python.
- Git.
- Docker Desktop.
- SQL Server em container.
- Driver ODBC 18 para SQL Server.
- Editor ou IDE compatível.

## 3. Repositório

```cmd
git clone git@github.com:lgomesroc/MatchCV.git
cd MatchCV
```

## 4. Ambiente Python

Criar ambiente virtual:

```cmd
python -m venv .venv
```

Ativar no Windows CMD:

```cmd
.venv\Scripts\activate
```

Instalar dependências:

```cmd
python -m pip install -r requirements.txt
```

## 5. Configuração

Copiar `.env.example` para `.env` e preencher os valores locais.

O arquivo `.env` não deve ser versionado.

## 6. Banco de dados

Iniciar os serviços definidos no Docker Compose:

```cmd
docker compose up -d
```

Verificar os containers:

```cmd
docker compose ps
```

## 7. Desenvolvimento

As alterações devem respeitar a separação de responsabilidades.

- Domain: regras de negócio.
- Application: casos de uso.
- Infrastructure: integrações.
- Parser: documentos.
- AI: provedores.
- API: HTTP.
- Frontend: interface.

## 8. Testes

Executar a suíte configurada no projeto.

Os testes que dependem do SQL Server ou de arquivos reais devem ser executados em ambiente apropriado.

## 9. Git

Fluxo recomendado:

1. Criar ou utilizar branch de trabalho.
2. Implementar alterações relacionadas.
3. Revisar diferenças.
4. Executar verificações.
5. Agrupar alterações coerentes.
6. Criar commit.
7. Abrir ou atualizar Pull Request.

## 10. Documentação

Alterações de arquitetura, banco, API ou regras devem atualizar os documentos correspondentes.

## 11. Segurança

Não adicionar:

- `.env`.
- Senhas.
- Tokens.
- Currículos reais.
- Dados pessoais de terceiros.

## 12. Status

Este guia descreve o fluxo previsto. Os comandos definitivos de execução da aplicação serão atualizados após a conclusão da API.