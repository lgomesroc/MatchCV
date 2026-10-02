
# Regras de Negócio — MatchCV

## 1. Objetivo

Este documento centraliza as regras funcionais do MatchCV.

A numeração deve permanecer estável para permitir rastreabilidade entre documentação, código e testes.

## 2. Currículos

- Formatos permitidos: PDF, DOC e DOCX.
- Tamanho máximo: 1 MB.
- Quantidade máxima: duas páginas.
- Mínimo de 30 caracteres úteis.
- Arquivos protegidos por senha devem ser rejeitados.
- Arquivos corrompidos devem ser rejeitados.
- Documentos sem texto extraível não são aceitos na V1.
- OCR não faz parte do escopo inicial.

## 3. Descrição da vaga

- Campo obrigatório.
- Mínimo de 30 caracteres úteis.
- Máximo de 3000 caracteres.
- Deve conter conteúdo válido para análise.

## 4. Análise

O resultado deve distinguir:

- Requisitos evidenciados.
- Requisitos não evidenciados.
- Lacunas.
- Problemas do currículo.
- Sugestões.

O sistema não deve inventar qualificações.

## 5. Consultas

A V1 não possui limite de consultas.

A evolução de autenticação e planos poderá estabelecer:

- USER: três consultas totais.
- ADMIN: consultas ilimitadas.

O fallback entre provedores representa uma única consulta.

## 6. Usuários

Perfis previstos:

- USER.
- ADMIN.

O cadastro público não deve conceder privilégios administrativos.

## 7. Privacidade

O arquivo original do currículo não deve ser armazenado permanentemente.

## 8. Conteúdo inadequado

Currículo, descrição de vaga e campos textuais devem passar por validação de conteúdo inadequado conforme as regras específicas BR-037 a BR-040.

A normalização deve considerar:

- Maiúsculas e minúsculas.
- Acentos.
- Separadores.
- Caracteres especiais.
- Obfuscação simples.
- Substituições numéricas.
- Repetição de caracteres.

A validação deve evitar falsos positivos em palavras legítimas.

## 9. Segurança

- Não expor credenciais.
- Validar entradas.
- Proteger operações administrativas.
- Tratar conteúdo externo como não confiável.

## 10. Rastreabilidade

As regras detalhadas existentes devem ser preservadas. Este documento não substitui o conteúdo original das regras já aprovadas.

## 11. Status

As regras são referência funcional. Sua implementação deverá ser verificada por testes.
