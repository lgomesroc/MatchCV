# Processamento de Currículos — MatchCV

## Objetivo

Descrever o caminho do currículo desde o envio até a disponibilização do texto para análise, incluindo as limitações confirmadas dos parsers.

## Formatos e limites

- Tamanho máximo: 1 MiB (1.048.576 bytes).
- Até duas páginas, conforme a informação de paginação disponível ao parser.
- Mínimo de 30 caracteres alfanuméricos úteis extraídos.
- Extensões aceitas na entrada: PDF, DOC e DOCX, sem diferenciar maiúsculas de minúsculas.

**Importante:** aceitar uma extensão não significa que o formato esteja integralmente suportado. O parser DOC legado ainda não está implementado: arquivos `.doc` são rejeitados com uma mensagem orientando a conversão para DOCX ou PDF. DOCX é lido por `python-docx`; a paginação estimada não equivale necessariamente à paginação visual do Word.

## Fluxo

```text
Upload
  -> validação do nome, extensão e tamanho
  -> parser correspondente
  -> extração de texto
  -> validações estruturais
  -> caso de uso de análise
  -> enfileiramento para processamento assíncrono
```

## Validação de conteúdo

O conteúdo recebido é não confiável. Os parsers devem rejeitar arquivos vazios, corrompidos, protegidos por senha, sem texto extraível ou com texto insuficiente. O formato real é validado indiretamente pela capacidade do parser correspondente de abrir e ler o conteúdo; não se deve tratar a extensão como prova do tipo real.

PDFs somente com imagem não são processados por OCR no escopo da V1.

A descrição da vaga é obrigatória, com limite documentado de 3.000 caracteres e mínimo de 30 caracteres úteis.

## PDF, DOCX e DOC

- **PDF:** o parser usa `pypdf` para extrair texto. Arquivos corrompidos e protegidos por senha devem falhar com erro controlado.
- **DOCX:** o parser extrai parágrafos e tabelas. A quantidade de páginas é estimada a partir de quebras explícitas e pode não refletir a paginação real.
- **DOC:** formato binário legado não é processado nesta versão. Converta para DOCX ou PDF antes do envio.

## Testes com arquivos

A suíte `MatchCV.Tests/Integration/Parser/test_real_resume_files.py` gera documentos PDF e DOCX válidos durante o teste e também testa arquivos corrompidos, PDF protegido por senha, texto insuficiente, limite de tamanho e conteúdo incompatível com a extensão. Os arquivos são sintéticos; currículos pessoais não devem ser adicionados ao repositório.

Para executar:

```bash
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Integration/Parser -q
```

## Saída e análise semântica

O parser responde o que está presente no documento. A camada de IA interpreta o conteúdo em relação à vaga. A IA não substitui a validação estrutural nem pode inventar fatos profissionais.

O resultado deve distinguir requisitos evidenciados, requisitos sem evidência suficiente, lacunas, problemas do currículo e sugestões.

## Privacidade

O arquivo original deve ser temporário e removido após o processamento. Não salve currículos reais no Git nem registre conteúdo integral em logs.

## Falhas

Retorne erros controlados para formato inválido, arquivo corrompido/protegido, texto insuficiente e falhas de extração. Não exponha stack traces, caminhos internos ou conteúdo pessoal nas respostas públicas.
