# Processamento de Currículos — MatchCV

## Objetivo

Descrever o caminho do currículo desde o envio até a disponibilização do texto para análise, incluindo as limitações confirmadas dos parsers e os limites de entrada aplicados pela aplicação.

## Formatos e limites

- Tamanho máximo do arquivo enviado: 1 MiB (1.048.576 bytes).
- Até duas páginas, conforme a informação de paginação disponível ao parser.
- Mínimo de 30 caracteres alfanuméricos úteis extraídos.
- Máximo de 15000 caracteres para o texto do currículo, tanto quando colado no formulário quanto quando extraído de um arquivo.
- Máximo de 15000 caracteres para a descrição da vaga.
- Extensões aceitas na entrada: PDF, DOC e DOCX, sem diferenciar maiúsculas de minúsculas.

**Importante:** aceitar uma extensão não significa que o formato esteja integralmente suportado. O parser DOC legado ainda não está implementado: arquivos `.doc` são rejeitados com uma mensagem orientando a conversão para DOCX ou PDF.

DOCX é lido por `python-docx`; a paginação estimada não equivale necessariamente à paginação visual do Word.

O limite de 15000 caracteres não altera o limite de tamanho do arquivo enviado nem o limite de duas páginas.

## Fluxo

```text
Upload ou texto colado
  -> validação da entrada
  -> validação do nome, extensão e tamanho (quando arquivo)
  -> identificação e validação do formato
  -> parser correspondente (quando arquivo)
  -> extração de texto
  -> validações estruturais
  -> caso de uso de análise
  -> enfileiramento para processamento assíncrono
```

## Validação de conteúdo

O conteúdo recebido é não confiável. Os parsers devem rejeitar arquivos vazios, corrompidos, protegidos por senha, sem texto extraível ou com texto insuficiente.

O formato real é validado indiretamente pela capacidade do parser correspondente de abrir e ler o conteúdo; não se deve tratar a extensão como prova do tipo real.

O texto extraído do currículo deve respeitar o limite máximo de 15000 caracteres. A mesma restrição é aplicada ao currículo inserido diretamente no formulário.

PDFs somente com imagem não são processados por OCR no escopo da V1.

A descrição da vaga é obrigatória, com limite de 15000 caracteres e mínimo de 30 caracteres úteis.

O currículo também possui limite de 15000 caracteres, tanto quando colado no formulário quanto quando extraído de PDF/DOC/DOCX.

## PDF, DOCX e DOC

- **PDF:** o parser usa `pypdf` para extrair texto. Arquivos corrompidos e protegidos por senha devem falhar com erro controlado. PDFs sem texto extraível não são processados por OCR nesta versão.
- **DOCX:** o parser extrai parágrafos e tabelas. A quantidade de páginas é estimada a partir de quebras explícitas e pode não refletir a paginação real do documento no Word.
- **DOC:** formato binário legado não é processado nesta versão. Arquivos `.doc` são rejeitados. Converta para DOCX ou PDF antes do envio.

## Testes com arquivos

A suíte `MatchCV.Tests/Integration/Parser/test_real_resume_files.py` gera documentos PDF e DOCX válidos durante o teste e também testa arquivos corrompidos, PDF protegido por senha, texto insuficiente, limite de tamanho e conteúdo incompatível com a extensão.

Os arquivos são sintéticos; currículos pessoais não devem ser adicionados ao repositório.

Os testes também devem validar os limites de caracteres aplicados ao texto extraído e ao texto inserido diretamente.

Para executar:

```bash
PYTHONPATH="$PWD" python -m pytest MatchCV.Tests/Integration/Parser -q
```

## Saída e análise semântica

O parser responde o que está presente no documento. A camada de IA interpreta o conteúdo em relação à vaga. A IA não substitui a validação estrutural nem pode inventar fatos profissionais.

O resultado deve distinguir:

- Requisitos evidenciados.
- Requisitos sem evidência suficiente.
- Lacunas entre currículo e vaga.
- Problemas identificados no currículo.
- Sugestões de melhoria.

A ausência de informação no currículo não deve ser interpretada automaticamente como prova de incapacidade ou falta de experiência.

## Privacidade

O arquivo original deve ser temporário e removido após o processamento.

Não salve currículos reais no Git nem registre conteúdo integral em logs.

O processamento deve evitar a exposição de informações pessoais em mensagens de erro ou registros operacionais.

## Falhas

Retorne erros controlados para:

- Formato inválido ou não suportado.
- Arquivo corrompido.
- Arquivo protegido por senha.
- Arquivo sem texto extraível.
- Texto insuficiente.
- Currículo com mais de 15000 caracteres.
- Arquivo acima do limite de tamanho.
- Documento acima do limite de páginas.
- Falhas durante a extração.

Não exponha stack traces, caminhos internos ou conteúdo pessoal nas respostas públicas.