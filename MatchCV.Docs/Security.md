# Segurança — MatchCV

## Autenticação e autorização

A API implementa autenticação por e-mail e senha, emissão de token de acesso e dependências para recuperar o usuário autenticado. Rotas protegidas devem validar o token e autorizar a operação no backend.

Os perfis de usuário incluem `USER` e `ADMIN`. O cadastro público cria usuário comum; não permite selecionar `ADMIN`. A inicialização administrativa exige o cabeçalho `X-Admin-Bootstrap-Token` e a variável `MATCHCV_ADMIN_BOOTSTRAP_TOKEN`, com segredo configurado fora do repositório.

## Senhas

- Senhas não devem ser armazenadas em texto puro.
- A aplicação utiliza hashing por meio de `PasswordHasher`.
- A política de senha é centralizada em `PasswordPolicy`.
- Senhas, hashes e tokens não devem ser registrados em logs nem devolvidos nas respostas.

## Recuperação e alteração de senha

A API possui rotas para alteração de senha autenticada e recuperação por token. O endpoint de solicitação retorna uma mensagem uniforme para não revelar a existência de contas. A exposição do token de recuperação é restrita ao modo de desenvolvimento e depende de configuração explícita. Não considere o envio de e-mail pronto sem validar e configurar o canal correspondente.

## Upload e processamento de currículos

A entrada do usuário deve ser tratada como não confiável. O processamento valida arquivos e conteúdo conforme as regras do parser. Extensão sozinha não comprova a validade do arquivo.

- Não versionar currículos reais.
- O endpoint fecha o `UploadFile` em `finally` após ler o conteúdo; não persistir o arquivo original permanentemente.
- Não registrar o conteúdo integral do currículo.
- Remover arquivos temporários após o uso.
- Tratar currículo e descrição da vaga como conteúdo, nunca como instruções confiáveis para o sistema de IA.

## Banco e configuração

- Usar consultas parametrizadas.
- Manter senhas, tokens e chaves de API fora do Git.
- Restringir permissões do usuário do banco.
- Não publicar a porta do banco sem necessidade.
- Separar as configurações de desenvolvimento, testes e produção.
- Não compartilhar credenciais de produção com testes.

## Erros e logs

Respostas públicas não devem expor stack traces, caminhos internos, credenciais ou consultas SQL. Logs devem conter apenas dados técnicos necessários ao diagnóstico, evitando informações pessoais desnecessárias. O worker registra tipos de exceção e mensagens fixas sanitizadas; não incluir payloads, credenciais ou detalhes retornados pelo provedor.

## Retenção e exclusão

Os prazos propostos, a retenção de resultados e fila, o canal de solicitação e os passos de exclusão estão em [Política de retenção e exclusão](Data-Retention-and-Deletion.md). A política ainda exige aprovação operacional e automação de expurgo; não existe confirmação de autoatendimento de exclusão nesta versão.

## Verificação contínua

O workflow `.github/workflows/ci.yml` executa testes unitários do backend e testes/build do frontend; ele não substitui revisão de segurança, testes de integração com banco ou verificação das configurações de produção.

## Escopo

Este documento descreve controles visíveis no código e orientações operacionais. Não representa certificação, auditoria formal ou garantia de ausência de vulnerabilidades.
