# MatchCV

Sistema de análise inteligente de currículos e vagas utilizando processamento de documentos e inteligência artificial.

O MatchCV foi desenvolvido para ir além de um simples percentual de compatibilidade entre currículo e vaga.

A proposta é analisar o conteúdo apresentado pelo candidato, confrontá-lo com os requisitos da oportunidade e apresentar informações que ajudem a compreender a aderência real entre os dois documentos.

## Objetivo

O MatchCV analisa:

* requisitos da vaga evidenciados no currículo;
* requisitos da vaga não evidenciados;
* possíveis lacunas;
* problemas estruturais ou de conteúdo no currículo;
* sugestões de melhoria;
* informações que podem ser interpretadas pela inteligência artificial sem inventar experiências ou qualificações.

O sistema não deve criar experiências, tecnologias, cargos, empresas, certificações, resultados ou qualquer outra informação que não esteja evidenciada no conteúdo fornecido.

## Fluxo principal

```text
Usuário
   ↓
Upload do currículo
   ↓
Validação do arquivo
   ↓
Parser
   ↓
Extração e normalização
   ↓
Descrição da vaga
   ↓
Análise com IA
   ↓
Comparação currículo × vaga
   ↓
Resultado da análise
```

## Principais características

* Suporte a PDF, DOC e DOCX;
* validação do tamanho do arquivo;
* validação da quantidade de páginas;
* validação do conteúdo extraído;
* análise estrutural do currículo;
* rejeição de documentos que não atendam aos critérios definidos;
* processamento de descrição de vaga;
* análise semântica com IA;
* arquitetura preparada para dois provedores de IA;
* processamento temporário dos currículos;
* minimização de dados armazenados;
* autenticação e autorização previstas para evolução do sistema;
* testes unitários e de integração;
* execução em Windows e Linux;
* infraestrutura de desenvolvimento com Docker.

## Arquitetura

O projeto é dividido em módulos com responsabilidades específicas:

| Módulo                   | Responsabilidade                             |
| ------------------------ | -------------------------------------------- |
| `MatchCV.Api`            | Exposição dos endpoints HTTP                 |
| `MatchCV.Application`    | Casos de uso e orquestração                  |
| `MatchCV.Domain`         | Regras e conceitos centrais do domínio       |
| `MatchCV.Infrastructure` | Persistência e integrações de infraestrutura |
| `MatchCV.AI`             | Abstração e integração dos provedores de IA  |
| `MatchCV.Parser`         | Processamento e extração de documentos       |
| `MatchCV.Worker`         | Processamentos assíncronos                   |
| `MatchCV.Tests`          | Testes unitários e de integração             |
| `MatchCV.Db`             | Recursos relacionados ao banco de dados      |
| `MatchCV.Frontend`       | Interface da aplicação                       |
| `MatchCV.Docs`           | Documentação do projeto                      |

## Regras de negócio

As regras de negócio do sistema estão documentadas separadamente em:

`MatchCV.Docs/BusinessRules/business-rules.md`

A documentação contempla regras relacionadas a:

* currículo;
* descrição da vaga;
* parser;
* inteligência artificial;
* consultas;
* usuários;
* privacidade;
* segurança;
* arquitetura;
* qualidade.

## Documentação

A documentação técnica está organizada em `MatchCV.Docs`.

### Estrutura do projeto

`MatchCV.Docs/Project-Structure.md`

### Tecnologias

`MatchCV.Docs/Technologies.md`

### Regras de negócio

`MatchCV.Docs/BusinessRules/business-rules.md`

## Status

O projeto está em desenvolvimento.

A implementação está sendo realizada de forma incremental, começando pelo domínio e pelo processamento dos documentos antes da construção das camadas de API, IA, persistência e interface.

## Execução

O MatchCV foi planejado para funcionar em ambientes Windows e Linux.

A infraestrutura de desenvolvimento utiliza Docker quando aplicável.

## Privacidade

Os currículos enviados ao sistema não fazem parte do armazenamento permanente da aplicação.

O projeto segue o princípio de minimização de dados, evitando manter informações pessoais além do período necessário para o processamento.

Currículos reais não devem ser armazenados no repositório.

## Licença

A definir.
