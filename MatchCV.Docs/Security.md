# Segurança — MatchCV

## 1. Objetivo

Definir os requisitos de segurança da aplicação.

## 2. Autenticação

O sistema deverá identificar o usuário antes de permitir operações protegidas.

O mecanismo definitivo de autenticação será registrado após implementação.

## 3. Autorização

Perfis previstos:

- USER
- ADMIN

O usuário comum não poderá executar operações administrativas.

A autorização deverá ser verificada no backend.

## 4. Senhas

- Não armazenar senhas em texto puro.
- Utilizar algoritmo de hash apropriado para senhas.
- Não registrar credenciais em logs.
- Não retornar hashes nas respostas da API.

## 5. Upload de arquivos

Validar:

- Extensão.
- Tipo real do arquivo.
- Tamanho.
- Estrutura.
- Integridade.
- Proteção por senha.
- Conteúdo extraído.

A extensão isoladamente não comprova que um arquivo é válido.

## 6. Banco de dados

- Utilizar consultas parametrizadas.
- Restringir permissões.
- Proteger credenciais.
- Evitar exposição pública desnecessária.
- Não concatenar entrada do usuário em SQL.

## 7. Inteligência artificial

Currículos e descrições são entradas não confiáveis.

A aplicação deverá reduzir riscos de prompt injection e impedir que o conteúdo enviado altere as instruções de segurança do sistema.

## 8. Logs

Não registrar:

- Senhas.
- Tokens.
- Chaves de API.
- Currículos completos.
- Dados pessoais desnecessários.

## 9. Proteção de endpoints

Endpoints administrativos devem exigir autenticação e autorização adequadas.

## 10. Dependências

Dependências devem ser avaliadas e atualizadas periodicamente.

## 11. Tratamento de erros

Mensagens públicas não devem revelar caminhos internos, credenciais, consultas SQL ou stack traces.

## 12. Status

Os requisitos estão documentados. A implementação e validação dependem dos módulos correspondentes.
