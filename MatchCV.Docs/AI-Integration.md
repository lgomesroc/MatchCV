# Integração com Inteligência Artificial — MatchCV

## Objetivo

Descrever o papel da camada de IA na análise de currículos e descrições de vagas.

## Arquitetura

A integração fica isolada no módulo `MatchCV.AI`, utilizado pelo fluxo de aplicação para evitar acoplamento direto a um fornecedor. As configurações vêm do ambiente; chaves não devem ser versionadas.

## Fluxo funcional

1. A API recebe o currículo e a descrição da vaga.
2. O parser valida o arquivo e extrai o texto.
3. O caso de uso organiza a análise e a envia ao processamento assíncrono.
4. O worker utiliza o serviço de IA configurado.
5. O resultado é persistido e disponibilizado pela consulta autenticada da análise.

A submissão inicial retorna HTTP `202 Accepted`: a tarefa foi aceita, mas a análise ainda não terminou.

## Provedores e fallback

O serviço tenta o provedor principal e usa o fallback para falhas classificadas como recuperáveis, incluindo timeout e HTTP 429. Se os dois provedores falharem, a análise termina com erro controlado. Respostas malformadas e incompletas são rejeitadas pelo parser; conforme a classificação atual, erros não recuperáveis não acionam fallback.

A disponibilidade real de cada provedor depende das credenciais, modelo, URL, quota e timeout configurados no ambiente.

## Contrato da resposta

A resposta deve conter cinco listas de textos:

- `evidenced_requirements`: requisitos com evidência identificável.
- `unevidenced_requirements`: requisitos sem evidência suficiente.
- `gaps`: diferenças concretas entre vaga e currículo.
- `resume_issues`: problemas objetivos no próprio currículo.
- `suggestions`: ações úteis sem recomendar inventar qualificações.

O parser rejeita JSON inválido, campos obrigatórios ausentes, campos que não sejam listas e itens que não sejam textos.

## Resistência a instruções maliciosas

O currículo e a descrição da vaga são dados não confiáveis, não instruções privilegiadas. Tentativas de prompt injection não podem alterar as regras, revelar o prompt ou forçar a aprovação. Os testes verificam a construção do prompt, o contrato de saída e o fluxo de fallback.

Esses testes não garantem, sozinhos, o comportamento de todos os modelos reais. A avaliação semântica de provedores externos deve ser feita com casos de referência controlados, sem dados pessoais.

## Datas

A data de referência é incluída dinamicamente no prompt usando a data do servidor, e pode ser fixada nos testes. Uma data passada não é inválida apenas por ser antiga: junho de 2025 deve ser aceita quando a referência é outubro de 2026.

Datas futuras só devem ser apontadas quando representarem claramente período profissional, projeto ou evento concluído que ainda não poderia ter ocorrido. Datas previstas para conclusão de formação acadêmica em andamento são permitidas e não devem ser marcadas como erro apenas por estarem no futuro. Se o contexto não permitir concluir que há erro, não invente inconsistência.

## Falhas operacionais

Considere indisponibilidade do provedor, timeout, limite de uso, credenciais inválidas, resposta malformada e falha de fallback. Mensagens de erro não devem expor chaves, dados pessoais ou o conteúdo integral dos documentos.

## Executar os testes

Na raiz do repositório, com as dependências instaladas:

```bash
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Unit/AI -q
```

Os testes usam provedores e respostas simulados. Não dependem de chaves de API, quota paga, acesso à rede nem dados reais de candidatos.

## Limitações

A suíte automatizada verifica o tratamento de erros, a classificação de falhas, o fallback, a estrutura de saída e as regras enviadas ao modelo. Para confirmar a qualidade semântica de um provedor real, é necessária uma avaliação controlada específica do modelo configurado. Uma resposta HTTP 200 não prova, por si só, que a análise está correta.
