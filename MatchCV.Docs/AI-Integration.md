# Integração com Inteligência Artificial — MatchCV

## 1. Objetivo

Documentar a integração com provedores de IA utilizados para analisar currículos e descrições de vagas.

## 2. Arquitetura

A integração utiliza abstrações para reduzir o acoplamento a um único fornecedor.

## 3. Provedores

O sistema está preparado para:

- Provedor principal.
- Provedor de fallback.

Os fornecedores concretos serão definidos por configuração.

## 4. Fluxo

```text
Application
    |
    v
AIAnalysisProvider
    |
    v
AIProviderService
    |
    v
Provedor principal
    |
    +---- Sucesso ----> Resultado
    |
    +---- Falha elegível
                 |
                 v
          Provedor fallback
                 |
                 v
              Resultado
```

## 5. Fallback

O fallback deverá ser acionado somente em falhas classificadas como elegíveis para nova tentativa.

Falhas não recuperáveis devem ser propagadas.

A utilização do fallback continua representando uma única consulta do usuário.

## 6. Estrutura da resposta

A análise deverá retornar:

- Evidenced requirements.
- Unevidenced requirements.
- Gaps.
- Resume issues.
- Suggestions.

## 7. Integridade das informações

A IA não deve inventar:

- Experiências.
- Empresas.
- Cargos.
- Tecnologias.
- Certificações.
- Formação.
- Resultados profissionais.

> Ausência de evidência não significa necessariamente ausência de competência.

## 8. Prompt injection

Currículo e descrição da vaga devem ser tratados como dados, nunca como instruções privilegiadas.

## 9. Falhas

Devem ser tratados:

- Timeout.
- Indisponibilidade.
- Limite de requisições.
- Resposta inválida.
- Erros de autenticação do provedor.
- Falha do provedor principal.
- Falha do fallback.

## 10. Segurança

Chaves de API devem ser obtidas por configuração segura e não podem ser versionadas.

## 11. Status

A abstração e o mecanismo de fallback estão em desenvolvimento. Provedores reais e validação de respostas permanecem pendentes.