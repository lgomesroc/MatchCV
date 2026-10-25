# Backend — MatchCV

## Visão geral

O backend é desenvolvido em Python e utiliza FastAPI para expor endpoints HTTP. O código é organizado em módulos com responsabilidades separadas.

## Módulos

- `MatchCV.Api`: inicialização da aplicação, roteadores, dependências e schemas HTTP.
- `MatchCV.Application`: casos de uso, DTOs e coordenação do fluxo de análise.
- `MatchCV.Domain`: entidades, enums, validações e regras de domínio.
- `MatchCV.Infrastructure`: conexão SQL Server e implementações de repositórios.
- `MatchCV.Parser`: validação e extração de conteúdo de arquivos de currículo.
- `MatchCV.AI`: abstração e comunicação com provedores externos de IA.
- `MatchCV.Worker`: processamento assíncrono da fila de análises.
- `MatchCV.Login`: autenticação, hashing de senha, política de senha e autorização.
- `MatchCV.Db`: migrations SQL.
- `MatchCV.Tests`: testes unitários e de integração.

Consulte [Architecture.md](Architecture.md) para o fluxo entre componentes. Este resumo não substitui a [estrutura do projeto](Project-Structure.md).

## API e autenticação

Os roteadores de autenticação expõem cadastro, login, consulta do usuário autenticado, alteração de senha, bootstrap administrativo e recuperação de senha. O roteador de análise permite submeter currículo e descrição da vaga e consultar o estado/resultado de uma análise pertencente ao usuário autenticado.

A análise é enfileirada e a submissão bem-sucedida retorna HTTP 202. O processamento posterior é responsabilidade do fluxo assíncrono.

## Cota de análises

Usuários comuns têm cota de três análises por mês-calendário UTC. O fluxo reserva uma vaga antes de enfileirar e libera a reserva em falhas tratadas. Administradores não estão sujeitos a essa cota.

## Persistência

A persistência usa Microsoft SQL Server via `pyodbc`. O acesso é feito por repositórios e dependências de infraestrutura. As migrations ficam em `MatchCV.Db/Migrations/` e devem ser aplicadas de forma controlada; não presuma que iniciar a API as executa automaticamente.

## Provedores de IA

A integração com provedores externos está isolada no módulo `MatchCV.AI`. As credenciais e os parâmetros do provedor devem ser configurados no ambiente. Limites de uso, falhas de rede e disponibilidade do modelo podem afetar as análises.

## Privacidade e erros

O currículo é processado para análise; o documento original não deve ser armazenado permanentemente nem incluído em logs. Erros públicos devem ser controlados e não devem revelar segredos ou detalhes internos.

## Testes

A suíte está em `MatchCV.Tests/`. Execute os testes com o ambiente virtual ativo:

```bash
PYTHONPATH="$PWD" python -m pytest -q
```

Testes de integração que usam SQL Server precisam de instância de teste e credenciais válidas. Consulte [Testing.md](Testing.md).
