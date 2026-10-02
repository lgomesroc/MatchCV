# CI/CD — MatchCV

## 1. Objetivo

Definir o processo de integração contínua e entrega contínua do MatchCV.

## 2. Estratégia Git

```text
Branch de desenvolvimento
          |
          v
      Alterações
          |
          v
     Testes locais
          |
          v
    Pull Request
          |
          v
   Revisão e CI
          |
          v
        main
          |
          v
     Implantação
```

## 3. Integração contínua

O pipeline deverá executar:

- Instalação de dependências.
- Verificação de sintaxe Python.
- Testes unitários.
- Testes de integração quando disponíveis.
- Verificação de qualidade.
- Verificação de dependências.
- Validação de arquivos de configuração.

## 4. Pull Requests

Cada PR deverá apresentar:

- Objetivo da alteração.
- Arquivos modificados.
- Testes executados.
- Impactos em banco de dados.
- Atualização documental quando necessária.

## 5. Branch principal

A branch `main` deverá representar o estado estável.

Alterações devem passar pelo fluxo de revisão definido no repositório.

## 6. Segredos

Tokens, senhas e chaves não devem ser incluídos no código ou nos arquivos versionados.

## 7. Entrega contínua

A implantação automatizada dependerá da configuração do ambiente de destino.

## 8. Status

O fluxo de trabalho está definido. Pipeline automatizado e publicação dependem de implementação.
