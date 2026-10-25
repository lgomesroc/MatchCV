# Roadmap — MatchCV

## Como ler este roadmap

Este documento resume o estado conhecido do projeto. Itens marcados como concluídos correspondem a componentes identificados no repositório; isso não substitui a execução de testes ou a validação operacional. Itens sem evidência suficiente permanecem pendentes de confirmação.

## Fundação e arquitetura

- [x] Repositório e módulos separados por responsabilidade.
- [x] SQL Server e migrations versionadas.
- [x] Entidades, validações e casos de uso centrais.
- [x] Abstração de provedores de IA.
- [x] Parser e testes de processamento de documentos.

## API e autenticação

- [x] API FastAPI e documentação Swagger.
- [x] Cadastro e login.
- [x] Token de acesso e consulta do usuário autenticado.
- [x] Alteração de senha.
- [x] Bootstrap administrativo protegido por token de configuração.
- [x] Rotas de solicitação e confirmação de recuperação de senha.
- [x] Enfileiramento de análises e consulta do estado/resultado.
- [x] Controle de acesso à análise pelo usuário proprietário.
- [x] Cota mensal para usuários comuns e exceção para administradores.
- [ ] Configurar e validar um canal de envio de e-mail para recuperação de senha.

## Processamento e inteligência artificial

- [x] Processamento assíncrono de análises.
- [x] Integração com provedores por abstração e configuração.
- [x] Estrutura de resultado com requisitos evidenciados/não evidenciados, lacunas, problemas e sugestões.
- [ ] Validar de ponta a ponta os provedores reais, limites, fallback e erros de serviço.
- [ ] Continuar avaliando robustez contra prompt injection e respostas de IA inválidas.
- [ ] Confirmar suporte efetivo aos formatos e casos-limite documentados pelos testes.

## Frontend e experiência do usuário

- [x] Aplicação Angular existente.
- [x] Integração frontend/API em evolução.
- [ ] Validar continuamente os fluxos completos com a API publicada, incluindo erros de autenticação, cota e processamento assíncrono.

## Qualidade e operação

- [x] Testes unitários de backend.
- [x] Testes de integração de API, banco e repositórios presentes no repositório.
- [x] Workflow GitHub Actions para testes unitários de backend e testes/build do frontend.
- [ ] Estabilizar e validar a execução completa da suíte de testes de integração com SQL Server.
- [ ] Definir e validar a execução de testes de integração no CI, caso seja desejada.
- [ ] Confirmar a configuração efetiva de deploy automático e monitoramento no provedor.
- [ ] Consolidar política operacional de retenção, backup e recuperação de dados.

## Critério de conclusão

Marque uma tarefa como concluída somente após verificar a implementação correspondente e executar os testes apropriados. A presença de um endpoint, classe ou documento isolado não comprova que o fluxo completo está pronto para produção.
