# Regras de Negócio — MatchCV

Este documento resume as regras funcionais principais. A referência numerada detalhada fica em [BusinessRules/business-rules.md](BusinessRules/business-rules.md). Quando houver divergência, valide a regra contra o código e os testes antes de alterar a implementação.

## Currículos

- Formatos tratados pelo fluxo: PDF, DOC e DOCX; a aceitação efetiva depende do parser disponível.
- Limite documentado: 1 MB.
- Limite documentado: duas páginas.
- Mínimo documentado: 30 caracteres úteis.
- Arquivos corrompidos, protegidos ou sem texto extraível devem ser rejeitados.
- OCR não faz parte do escopo documentado da V1.
- O arquivo original não deve ser armazenado permanentemente.

A capacidade real de contar páginas em formatos legados e de detectar layout depende do parser e precisa ser validada por testes específicos.

## Descrição da vaga

- Obrigatória.
- Mínimo documentado de 30 caracteres úteis.
- Máximo documentado de 3.000 caracteres.
- Conteúdo deve ser textual e apropriado para análise.

## Resultado da análise

A análise deve separar:
- requisitos evidenciados;
- requisitos sem evidência suficiente;
- lacunas;
- problemas do currículo;
- sugestões de melhoria.

A ausência de evidência não prova que a pessoa não possui a competência. Não inventar empresas, cargos, experiências, tecnologias, formação, certificações ou resultados.

## Cota e usuários

- O cadastro público cria usuário comum (`USER`).
- A criação inicial de administrador exige mecanismo de bootstrap protegido por configuração.
- Usuários comuns possuem cota de três análises por mês-calendário UTC.
- Administradores possuem análises ilimitadas.
- O fallback entre provedores é parte da mesma análise.
- Falhas tratadas antes da conclusão não devem consumir cota permanentemente; confira o fluxo de reserva/liberação e seus testes.

## Validação de conteúdo

Os campos textuais são validados de acordo com componentes de validação reutilizáveis, incluindo política para conteúdo inadequado. A normalização deve considerar acentos, maiúsculas/minúsculas e formas simples de ofuscação, sem bloquear indevidamente termos técnicos ou palavras legítimas.

## Privacidade

- Não incluir currículos reais no repositório.
- Não registrar o conteúdo integral do currículo em logs.
- Tratar arquivo original como temporário.
- Limitar a persistência aos dados necessários para operar o serviço.

## Status

Este resumo não substitui a verificação de implementação. Use as migrations, validadores, casos de uso e testes como fonte de verdade para comportamento efetivo.
