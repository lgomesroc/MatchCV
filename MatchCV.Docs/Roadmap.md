# Roadmap — MatchCV

## Como ler este roadmap

Este documento resume o estado identificado no código e nos arquivos do repositório. Itens marcados como concluídos indicam que há implementação ou estrutura correspondente no projeto; isso não substitui a execução dos testes, a validação dos serviços externos ou a confirmação do comportamento em produção. Itens sem evidência suficiente permanecem pendentes.

## Fundação e arquitetura

- [x] Repositório e módulos separados por responsabilidade.
- [x] SQL Server e migrations versionadas para produção e testes.
- [x] Entidades, enums, validações e casos de uso centrais.
- [x] Abstrações e contratos para dependências entre as camadas.
- [x] Parser com suporte implementado a PDF, DOC e DOCX.
- [x] Estrutura de testes unitários e de integração.
- [x] Documentação técnica, funcional e arquitetural organizada em `MatchCV.Docs/`.

## API e autenticação

- [x] API FastAPI com rotas versionadas em `/api/v1`.
- [x] Endpoint básico de saúde em `/health`.
- [x] Documentação Swagger, ReDoc e OpenAPI protegida por HTTP Basic quando configurada.
- [x] Cadastro de usuário comum e login.
- [x] Emissão de token de acesso e consulta do usuário autenticado.
- [x] Alteração de senha com validação da senha atual e política de senha.
- [x] Bootstrap administrativo protegido por token de configuração.
- [x] Rotas de solicitação e confirmação de recuperação de senha.
- [x] Resposta uniforme na solicitação de recuperação, sem devolver o token pela API.
- [x] Enfileiramento de análises e consulta do estado/resultado.
- [x] Controle de acesso à análise pelo usuário proprietário.
- [x] Cota mensal de três análises para usuários comuns e exceção para administradores.
- [ ] Configurar e validar um canal real de envio de e-mail para recuperação de senha.
- [ ] Validar o fluxo completo de recuperação no ambiente publicado, incluindo expiração e uso único do token.

## Processamento e inteligência artificial

- [x] Processamento assíncrono de análises por fila SQL Server e worker.
- [x] Recuperação de tarefas com lease expirado e renovação do lease durante o processamento.
- [x] Proteção do payload da fila por cifragem.
- [x] Limpeza do payload cifrado ao concluir ou marcar uma tarefa como falha.
- [x] Integração com provedores por abstração, configuração e serviço coordenador.
- [x] Estrutura de resultado com requisitos evidenciados/não evidenciados, lacunas, problemas e sugestões.
- [ ] Validar de ponta a ponta os provedores reais, limites, fallback, timeouts e erros de serviço.
- [ ] Continuar avaliando robustez contra prompt injection e respostas de IA inválidas.
- [ ] Confirmar suporte efetivo aos formatos e casos-limite documentados pelos testes.

## Currículos e descrições de vagas

- [x] Entrada de currículo por texto ou arquivo, sem aceitar as duas modalidades simultaneamente.
- [x] Limite de 15.000 caracteres para o currículo e para a descrição da vaga.
- [x] Limite de 1 MiB para o arquivo enviado e máximo de duas páginas.
- [x] Validação de conteúdo útil, texto extraível e estrutura do documento.
- [ ] Confirmar os casos-limite dos formatos suportados com arquivos representativos e testes no ambiente de execução.

## Frontend e experiência do usuário

- [x] Aplicação Angular estruturada por funcionalidades.
- [x] Telas e serviços de autenticação, cadastro, alteração e recuperação de senha presentes no projeto.
- [x] Fluxo de análise, estados de processamento e apresentação de resultados presentes no projeto.
- [x] Testes automatizados de componentes/serviços e cenários E2E com Playwright presentes no repositório.
- [ ] Validar continuamente os fluxos completos com a API publicada, incluindo autenticação, cota, upload, processamento assíncrono e recuperação de senha.
- [ ] Confirmar comportamento em navegadores e condições reais de rede.

## Qualidade e operação

- [x] Suíte de testes unitários de backend presente no repositório.
- [x] Testes de integração de API, banco, Parser e repositórios presentes no repositório.
- [x] Workflow GitHub Actions para testes unitários de backend e testes/build do frontend.
- [x] Workflow separado para integração com SQL Server.
- [x] Workflow de entrega contínua presente em `.github/workflows/cd.yml`.
- [ ] Executar e estabilizar a suíte completa de testes de integração com SQL Server.
- [ ] Definir e validar a execução de testes de integração no CI, incluindo isolamento e limpeza do banco de teste.
- [ ] Confirmar a configuração efetiva de deploy automático, variáveis de ambiente e monitoramento no provedor.
- [ ] Validar API e worker em execução publicada, compartilhando banco, migrations e chave de cifragem compatíveis.
- [ ] Consolidar política operacional de retenção, backup e recuperação de dados.

## Critério de conclusão

Marque uma tarefa como concluída somente após verificar a implementação correspondente e executar os testes apropriados. A presença de um endpoint, classe, workflow ou documento isolado não comprova que o fluxo completo está pronto para produção.

A conclusão da V1 deve considerar, além do código, os testes automatizados, a configuração dos serviços externos, a implantação real e os procedimentos operacionais necessários para manter o serviço.
