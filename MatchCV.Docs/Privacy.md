# Privacidade — MatchCV

## Objetivo e princípio

O MatchCV processa currículos para compará-los com descrições de vagas. O documento original é dado pessoal e profissional e não deve ser armazenado permanentemente.

## Categorias de dados

Dependendo do fluxo utilizado, podem ser tratados:
- nome e e-mail da conta;
- arquivo de currículo durante o processamento;
- texto extraído do currículo;
- descrição da vaga;
- estado e resultado da análise;
- dados técnicos mínimos necessários para operação e diagnóstico.

## Minimização e retenção

- Não versionar currículos reais.
- Não utilizar currículos reais em testes automatizados.
- Não registrar conteúdo integral de currículos ou descrições de vagas em logs.
- Remover arquivos temporários após o processamento.
- Armazenar somente dados necessários ao funcionamento do produto.
- Definir e documentar o período de retenção dos resultados e dos dados da conta.

A política formal de retenção e os procedimentos de exclusão devem ser confirmados antes de declarar concluído o ciclo de vida de dados.

## Provedores externos

A análise pode enviar conteúdo necessário a provedores externos de IA. Antes de utilizar um provedor em produção, verificar quais dados são enviados, a finalidade, os termos de tratamento, as opções de retenção e as credenciais/configurações aplicadas.

## Segurança operacional

Tokens, senhas, chaves e strings de conexão não devem ser registrados em logs nem versionados. Logs devem priorizar códigos de erro e identificadores técnicos de correlação, sem dados pessoais desnecessários.

## Direitos e solicitações

Os procedimentos para atender solicitações de acesso, correção ou exclusão devem ser definidos conforme a legislação aplicável e a política de operação. Não declare que há um fluxo automatizado de atendimento sem confirmar sua implementação.

## Estado

Este documento registra princípios e cuidados. A política formal de retenção, os procedimentos de exclusão e as configurações de privacidade de cada provedor externo ainda precisam de validação operacional.
