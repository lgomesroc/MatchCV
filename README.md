# MatchCV

O MatchCV analisa um currículo em relação a uma descrição de vaga usando processamento de documentos e inteligência artificial. O resultado não se limita a um percentual: separa requisitos evidenciados, requisitos sem evidência suficiente, lacunas, problemas do currículo e sugestões de melhoria.

O sistema não deve inventar experiências, cargos, empresas, tecnologias, certificações, formação ou resultados que não estejam evidenciados nas informações fornecidas.

## Status da versão

**V1 concluída e fechada.**

O escopo planejado para a primeira versão do MatchCV foi concluído. A V1 está encerrada e passa a ser a versão de referência do projeto. Novas funcionalidades ou mudanças de escopo deverão ser tratadas como evolução de uma futura versão, sem reabrir o escopo da V1.

O encerramento da V1 não significa que o sistema esteja livre de possíveis correções: ajustes necessários para corrigir defeitos, segurança, compatibilidade ou estabilidade poderão ser realizados sem caracterizar reabertura do escopo funcional.

## Aplicação publicada

- **Frontend:** https://matchcv-frontend-020d.onrender.com
- **API:** https://matchcv-api-0oi5.onrender.com
- **Swagger:** https://matchcv-api-0oi5.onrender.com/docs

Os endereços são os registrados para o projeto; disponibilidade e configuração atual devem ser confirmadas no provedor.

## Stack

| Componente | Tecnologia |
|---|---|
| Backend/API | Python, FastAPI |
| Frontend | Angular, TypeScript |
| Banco de dados | Microsoft SQL Server |
| Driver SQL | pyodbc |
| Processamento de documentos | Parsers para PDF, DOC e DOCX |
| IA | Provedores externos por camada de integração |
| Processamento assíncrono | Worker e fila persistida no banco |
| Ambiente local | Docker Compose |
| Testes | pytest e testes do frontend |
| CI | GitHub Actions |
| Hospedagem conhecida | Render |

Consulte [Tecnologias](MatchCV.Docs/Technologies.md) para mais detalhes.

## Funcionalidades principais

- Cadastro, login e autenticação por token.
- Alteração e recuperação de senha por rotas da API.
- Envio de currículo por arquivo ou texto e descrição da vaga.
- Processamento assíncrono de análises.
- Consulta autenticada do estado e resultado da análise.
- Resultados estruturados em requisitos evidenciados, requisitos não evidenciados, lacunas, problemas do currículo e sugestões.
- Controle de cota mensal para usuários comuns e tratamento diferenciado para administradores.
- Persistência em SQL Server.

A presença de uma rota não significa que todo serviço externo relacionado esteja configurado. O canal de e-mail para recuperação de senha, por exemplo, precisa ser configurado e validado separadamente.

## Arquitetura

O repositório separa responsabilidades em módulos:

- `MatchCV.Api`: HTTP, schemas e dependências.
- `MatchCV.Application`: casos de uso.
- `MatchCV.Domain`: entidades e regras de negócio.
- `MatchCV.Infrastructure`: persistência e integrações de infraestrutura.
- `MatchCV.Parser`: validação e extração de documentos.
- `MatchCV.AI`: integração com provedores de IA.
- `MatchCV.Worker`: processamento assíncrono.
- `MatchCV.Login`: autenticação e autorização.
- `MatchCV.Db`: migrations SQL.
- `MatchCV.Tests`: testes automatizados.
- `MatchCV.Frontend`: aplicação Angular.
- `MatchCV.Docs`: documentação.

Consulte [Arquitetura](MatchCV.Docs/Architecture.md). A estrutura detalhada do repositório está documentada em [Project-Structure.md](MatchCV.Docs/Project-Structure.md).

## Executar localmente

Pré-requisitos: Python 3.12, Docker Compose, driver ODBC compatível com SQL Server e Node/npm para o frontend.

Consulte o [Guia de instalação e execução](MatchCV.Docs/Getting-Started.md) para configurar variáveis de ambiente, iniciar o banco, aplicar migrations e executar a API e o frontend.

Com a API local em execução, o Swagger normalmente fica em `http://127.0.0.1:8000/docs`.

## Testes

Ative o ambiente virtual e execute na raiz:

```bash
PYTHONPATH="$PWD" python -m pytest -q
```

Os testes de integração com SQL Server precisam de banco e credenciais de teste válidos. O workflow de CI executa os testes unitários do backend e os testes/build do frontend; não representa, por si só, execução da suíte completa de integração.

Consulte [Testing.md](MatchCV.Docs/Testing.md).

## Documentação

O índice completo está em [MatchCV.Docs/README.md](MatchCV.Docs/README.md). Documentos de referência:

- [API](MatchCV.Docs/API.md)
- [Integração da API](MatchCV.Docs/API-Integration.md)
- [Banco de dados](MatchCV.Docs/Database.md)
- [Segurança](MatchCV.Docs/Security.md)
- [Privacidade](MatchCV.Docs/Privacy.md)
- [Regras de negócio](MatchCV.Docs/Business-Rules.md)
- [Roadmap](MatchCV.Docs/Roadmap.md)
- [CI/CD](MatchCV.Docs/CI-CD.md)
- [Implantação](MatchCV.Docs/Deployment.md)

## Privacidade

Currículos contêm dados pessoais e profissionais. O documento original não deve ser armazenado permanentemente nem incluído no Git; logs devem evitar conteúdo integral do currículo. A retenção de resultados e dados de conta deve seguir uma política definida para o ambiente.

## Licença

A definir.
