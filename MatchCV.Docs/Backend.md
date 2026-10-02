# Backend — MatchCV

## 1. Objetivo

O backend do MatchCV é responsável por receber as solicitações da aplicação,
executar os casos de uso, processar documentos, realizar análises e persistir
os dados necessários.

A implementação é dividida em módulos para reduzir acoplamento e separar
responsabilidades.

## 2. Componentes

```text
MatchCV.Api
MatchCV.Application
MatchCV.Domain
MatchCV.Infrastructure
MatchCV.Parser
MatchCV.AI
MatchCV.Worker
```

## 3. MatchCV.Api

A API representa a porta de entrada HTTP da aplicação.

Responsabilidades:

- Receber requisições.
- Validar entrada básica.
- Acionar casos de uso.
- Retornar respostas.
- Aplicar middleware.
- Tratar exceções.

A API não deve implementar diretamente regras complexas de negócio.

## 4. MatchCV.Application

A camada Application coordena os casos de uso.

Exemplos de responsabilidades:

- Receber dados da API.
- Validar o fluxo da operação.
- Solicitar processamento do currículo.
- Solicitar análise da descrição da vaga.
- Acionar o serviço de IA.
- Persistir resultados através de interfaces.
- Montar DTOs de resposta.

## 5. MatchCV.Domain

Contém os conceitos centrais do sistema.

Exemplos:

- Usuário.
- Descrição da vaga.
- Análise.
- Tipo de arquivo.
- Regras de domínio.
- Exceções específicas do domínio.

A camada deve permanecer independente de infraestrutura.

## 6. MatchCV.Infrastructure

Responsável pelas implementações concretas.

Inclui:

- SQL Server.
- Repositórios.
- Adaptadores.
- Serviços externos.
- Configurações técnicas.

## 7. MatchCV.Parser

O Parser é responsável pelo processamento do currículo.

Fluxo:

```text
Arquivo
   │
   ▼
Validação do arquivo
   │
   ▼
Identificação do formato
   │
   ▼
Extração de texto
   │
   ▼
Validação estrutural
   │
   ▼
Resultado estruturado
```

O Parser não realiza a comparação semântica entre currículo e vaga.

## 8. MatchCV.AI

O módulo de IA abstrai os provedores externos.

A aplicação deve trabalhar com uma interface e não depender diretamente de
um provedor específico.

Isso permite substituir ou adicionar provedores sem modificar os casos de
uso principais.

## 9. MatchCV.Worker

O Worker poderá ser utilizado quando operações assíncronas forem necessárias.

Exemplos:

- Análise demorada.
- Processamento em fila.
- Tarefas de segundo plano.

Enquanto não houver necessidade real, sua implementação permanece separada
do fluxo síncrono principal.

## 10. Persistência

O backend utiliza SQL Server.

As operações de banco devem ser executadas através da camada
MatchCV.Infrastructure.

Os casos de uso não devem criar conexões diretamente com o SQL Server.

## 11. Configuração

Configurações sensíveis devem ser fornecidas por variáveis de ambiente.

Exemplos:

```text
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
```

Configurações de provedores de IA também devem utilizar variáveis de ambiente
ou mecanismos equivalentes.

Credenciais não devem ser versionadas no Git.

## 12. Tratamento de currículo

O currículo é processado temporariamente.

O backend deve:

1. Receber o arquivo.
2. Validar o tamanho.
3. Validar a extensão.
4. Validar a integridade.
5. Extrair o texto.
6. Validar a quantidade de texto.
7. Validar características estruturais.
6. Encaminhar o conteúdo para análise.
9. Descartar o arquivo temporário quando o processamento terminar.

## 13. Logs

Os logs devem registrar informações técnicas suficientes para diagnóstico,
sem registrar o conteúdo do currículo.

Não devem ser registrados:

- Texto completo do currículo.
- Dados pessoais desnecessários.
- Senhas.
- Tokens.
- Chaves de API.
- Credenciais de banco.

## 14. Testes

O backend deve possuir:

- Testes unitários.
- Testes de integração.

Os testes devem cobrir principalmente:

- Regras de negócio.
- Validações.
- Parser.
- Casos de uso.
- Repositórios.
- Integrações críticas.

## 15. Status

O backend encontra-se em desenvolvimento.

A documentação não deve considerar funcionalidades futuras como implementadas até que existam no código e tenham sido validadas.
