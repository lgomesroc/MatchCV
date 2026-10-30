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

Os prazos operacionais propostos, o tratamento de resultados antigos, a fila e o procedimento de exclusão estão documentados em [Política de retenção e exclusão](Data-Retention-and-Deletion.md). Esses prazos ainda exigem aprovação e automação de expurgo; não devem ser anunciados como garantidos até essa implementação.

## Provedores externos

A análise pode enviar conteúdo necessário a provedores externos de IA. Antes de utilizar um provedor em produção, verificar quais dados são enviados, a finalidade, os termos de tratamento, as opções de retenção e as credenciais/configurações aplicadas.

## Segurança operacional

Tokens, senhas, chaves e strings de conexão não devem ser registrados em logs nem versionados. Logs devem priorizar códigos de erro e identificadores técnicos de correlação, sem dados pessoais desnecessários.

## Direitos e solicitações

Ainda não há fluxo de autoatendimento de exclusão confirmado na API/interface. Até que seja implementado, a operação deve configurar e publicar um canal oficial de privacidade e seguir o procedimento documentado em [Política de retenção e exclusão](Data-Retention-and-Deletion.md). Não afirmar que a exclusão automática está disponível.

## Estado

A política operacional proposta está documentada, mas a aprovação dos prazos, o canal oficial, o job de expurgo, a exclusão automatizada e a retenção de backups/provedores ainda precisam de validação operacional.
