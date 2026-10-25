# Integração com Inteligência Artificial — MatchCV

## Objetivo

Descrever o papel da camada de IA na análise de currículos e descrições de vagas.

## Arquitetura

A integração fica isolada no módulo `MatchCV.AI`, que é utilizado pelo fluxo de aplicação para evitar acoplamento direto dos casos de uso a um fornecedor específico. As configurações devem vir do ambiente; chaves não devem ser versionadas.

## Fluxo funcional

1. A API recebe o currículo e a descrição da vaga.
2. O parser valida o arquivo e extrai o texto.
3. O caso de uso organiza a análise e a envia ao processamento assíncrono.
4. O worker processa a tarefa e utiliza o serviço de IA configurado.
5. O resultado é persistido e disponibilizado pela consulta autenticada da análise.

A submissão inicial retorna HTTP `202 Accepted`; isso significa que a tarefa foi aceita, não que a análise já terminou.

## Provedores e fallback

O projeto possui uma camada de integração com provedores configuráveis. A configuração de provedores, modelos, URLs e timeouts é específica do ambiente. O comportamento de fallback depende dos erros classificados pela implementação e das configurações presentes.

Não assuma que um provedor ou modelo está operacional apenas porque aparece em um exemplo de configuração. Confirme as variáveis e a disponibilidade da conta do fornecedor no ambiente em execução.

## Estrutura do resultado

A resposta de análise contempla:

- `evidenced_requirements`: requisitos evidenciados no currículo.
- `unevidenced_requirements`: requisitos sem evidência suficiente.
- `gaps`: lacunas identificadas.
- `resume_issues`: problemas de conteúdo ou estrutura do currículo.
- `suggestions`: sugestões de melhoria.

A ausência de evidência no currículo não prova que a pessoa não possua determinada competência. A análise deve se limitar ao conteúdo fornecido e não inventar experiências, empresas, cargos, tecnologias, certificações, formação ou resultados.

## Entradas não confiáveis

Currículo e descrição da vaga são dados de entrada, não instruções privilegiadas. A aplicação deve tratar tentativas de prompt injection como conteúdo não confiável e validar a estrutura da resposta antes de persistir ou exibir os resultados.

## Falhas operacionais

Considere indisponibilidade do provedor, timeout, limite de uso, credenciais inválidas, resposta malformada e falha de fallback. Mensagens de erro não devem expor chaves, dados pessoais ou o conteúdo integral dos documentos.

## Testes

Testes unitários devem usar provedores simulados sempre que possível. Testes que chamem serviços reais dependem de credenciais válidas, quota e disponibilidade externa e não devem ser requisito para executar a suíte unitária.

## Estado

Este documento descreve o fluxo e as garantias esperadas; a disponibilidade real de cada provedor, modelo e fallback deve ser verificada nas configurações e nos testes do ambiente correspondente.
