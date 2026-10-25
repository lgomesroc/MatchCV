# Processamento de Currículos — MatchCV

## Objetivo

Descrever o caminho do currículo desde o envio até a disponibilização do texto para análise.

## Formatos e limites

Os formatos previstos são PDF, DOC e DOCX. As regras de negócio documentam limite de 1 MB, até duas páginas e mínimo de 30 caracteres úteis. A capacidade efetiva de cada formato depende do parser concreto e deve ser confirmada por testes; não trate extensão permitida como garantia de suporte completo.

## Fluxo

```text
Upload
  -> validação da entrada e tamanho
  -> identificação/validação do formato real
  -> parser correspondente
  -> extração de texto
  -> validações estruturais
  -> caso de uso de análise
  -> enfileiramento para processamento assíncrono
```

## Validação

O conteúdo recebido é não confiável. A validação deve considerar extensão, estrutura real, integridade, proteção por senha e disponibilidade de texto extraível. PDFs somente com imagem não são processados por OCR no escopo documentado da V1.

A descrição da vaga é obrigatória, com limite documentado de 3.000 caracteres e mínimo de 30 caracteres úteis.

## PDF, DOCX e DOC

- **PDF:** validar arquivo e texto extraível; documento protegido ou sem texto útil deve falhar de forma controlada.
- **DOCX:** a extração textual pode não reproduzir a paginação visual; contar páginas com precisão pode exigir renderização/conversão.
- **DOC:** formato legado exige implementação ou conversão compatível; aceitar a extensão não prova que o parser esteja operacional para todos os arquivos.

## Saída e análise semântica

O parser responde o que está presente no documento. A camada de IA interpreta o conteúdo em relação à vaga. A IA não substitui a validação estrutural nem pode inventar fatos profissionais.

O resultado deve distinguir requisitos evidenciados, requisitos sem evidência suficiente, lacunas, problemas do currículo e sugestões.

## Privacidade

O arquivo original deve ser temporário e removido após o processamento. Não salvar currículos reais no Git nem registrar conteúdo integral em logs.

## Falhas

Retornar erros controlados para formato inválido, arquivo corrompido/protegido, texto insuficiente e falhas de extração. Não expor stack traces, caminhos internos ou conteúdo pessoal nas respostas públicas.

## Estado

As regras documentadas não comprovam suporte completo de cada formato. Confirme o código de seleção de parser e os testes de PDF, DOC e DOCX antes de afirmar compatibilidade integral.
