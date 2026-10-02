# Processamento de Currículos — MatchCV

## 1. Objetivo

Documentar o fluxo de recebimento, validação, extração e processamento de currículos.

## 2. Formatos previstos

- PDF.
- DOC.
- DOCX.

## 3. Limites

| Regra | Limite |
|---|---|
| Tamanho máximo | 1 MB |
| Quantidade máxima | 2 páginas |
| Conteúdo mínimo | 30 caracteres úteis |

## 4. Fluxo

```text
Upload
   |
   v
Validação inicial
   |
   v
Identificação do formato
   |
   v
Parser específico
   |
   v
Extração de texto
   |
   v
Validação estrutural
   |
   v
Resultado para Application
```

## 5. Validação inicial

Verificar:

- Nome do arquivo.
- Extensão permitida.
- Tamanho.
- Integridade.
- Formato real.
- Arquivo vazio.

## 6. PDF

A extração deverá identificar documentos inválidos, protegidos e sem texto extraível.

## 7. DOCX

A extração deverá considerar parágrafos e tabelas.

A contagem física de páginas exige mecanismo adicional de renderização ou conversão, pois a leitura textual isolada não garante paginação real.

## 8. DOC

O formato DOC legado exige estratégia específica de conversão ou processamento.

A aceitação da extensão não significa que o processamento esteja disponível.

## 9. Estrutura

A V1 prioriza currículos:

- Com texto extraível.
- Sem dependência de OCR.
- Sem imagens essenciais para interpretação.
- Com estrutura de coluna única.

A detecção de layout por heurística deve evitar rejeições indevidas.

## 10. Privacidade

O documento original deverá ser tratado temporariamente e removido após o processamento.

## 11. Erros

Erros de parser devem ser convertidos em mensagens compreensíveis, sem expor detalhes internos.

## 12. Status

O serviço de seleção de parser e os parsers iniciais estão em desenvolvimento. Suporte rigoroso a DOC e paginação física de DOCX permanece pendente.
