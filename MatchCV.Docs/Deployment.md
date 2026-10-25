# Implantação — MatchCV

## Ambientes publicados

A aplicação possui serviços publicados no Render:

- Frontend: https://matchcv-frontend-020d.onrender.com
- API: https://matchcv-api-0oi5.onrender.com
- Swagger da API: https://matchcv-api-0oi5.onrender.com/docs

A disponibilidade e os endereços podem mudar conforme a configuração da hospedagem. Confirme os valores no painel do Render antes de executar alterações de infraestrutura.

## Componentes

- **Frontend:** aplicação Angular em `MatchCV.Frontend`.
- **API:** aplicação FastAPI iniciada por `MatchCV.Api.main:app`.
- **Persistência:** Microsoft SQL Server.
- **Processamento assíncrono:** worker Python separado para processar análises enfileiradas.
- **Provedores de IA:** configurados por variáveis de ambiente.

A API e o worker precisam compartilhar as configurações de banco e de provedor necessárias ao processamento. Não exponha credenciais em arquivos versionados ou logs.

## Antes de publicar

1. Execute os testes unitários e de integração aplicáveis.
2. Execute `npm test` e `npm run build` no frontend.
3. Revise migrations pendentes e aplique-as de forma controlada ao banco correto.
4. Confirme as variáveis de ambiente no serviço de destino.
5. Verifique limites e disponibilidade dos provedores de IA.
6. Confirme que logs e respostas de erro não incluem currículos, senhas, tokens ou chaves.
7. Após a publicação, verifique o endpoint de saúde e a documentação da API.

## Banco de dados

As migrations estão em `MatchCV.Db/Migrations/`; a API não deve ser presumida como responsável por aplicá-las automaticamente. Revise e execute as migrations em ordem no banco de destino, com permissões adequadas e plano de recuperação compatível com o ambiente.

## CI/CD

O workflow `.github/workflows/ci.yml` executa verificações do backend e frontend. A existência desse workflow não significa, por si só, que a implantação automática esteja configurada. Consulte [CI/CD](CI-CD.md) e confirme os workflows e as configurações ativas no GitHub e no Render.

## Recuperação e segurança

- Mantenha credenciais em configurações seguras do serviço.
- Não publique arquivos `.env`.
- Preserve backups antes de alterações destrutivas no banco.
- Não use o banco local ou o banco de testes como banco de produção.
- Tenha em conta que serviços em planos gratuitos podem suspender ou demorar a iniciar.

## Estado

Este documento registra os serviços publicados conhecidos e um checklist operacional. O estado efetivo de cada deploy deve ser confirmado nos painéis dos provedores; não é garantia de disponibilidade contínua.
