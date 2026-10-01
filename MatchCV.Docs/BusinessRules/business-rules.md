# MatchCV — Regras de Negócio

## 1. Objetivo

O MatchCV analisa um currículo em relação a uma descrição de vaga utilizando processamento de documentos e inteligência artificial.

O sistema não deve se limitar a produzir um percentual de aderência.

A análise deve identificar:

- requisitos claramente evidenciados no currículo;
- requisitos não evidenciados;
- possíveis lacunas;
- problemas de qualidade do currículo;
- sugestões de melhoria.

A inteligência artificial não pode inventar informações que não estejam presentes no currículo ou que não tenham sido fornecidas separadamente pelo candidato.

---

## 2. Regras do currículo

### BR-001 — Formatos aceitos

O sistema deve aceitar:

- PDF;
- DOC;
- DOCX.

### BR-002 — Tamanho máximo

O currículo não pode ultrapassar 1 MB.

### BR-003 — Quantidade máxima de páginas

O currículo não pode possuir mais de 2 páginas.

### BR-004 — Quantidade mínima de caracteres úteis

O currículo deve possuir pelo menos 30 caracteres úteis.

Caracteres úteis são caracteres alfanuméricos após a extração do conteúdo.

### BR-005 — Texto extraível

O currículo deve possuir texto que possa ser extraído pelo parser.

### BR-006 — PDF somente imagem

PDFs compostos exclusivamente por imagens ou digitalizações não serão processados na V1.

OCR não faz parte da V1.

### BR-007 — Imagens

Imagens não podem ser necessárias para compreender informações essenciais do currículo na V1.

### BR-008 — Estrutura em múltiplas colunas

Na V1, currículos que dependam de estrutura de múltiplas colunas devem ser rejeitados.

O formato aceito é uma estrutura linear de coluna única.

### BR-009 — Arquivo inválido

Arquivos corrompidos, inválidos ou impossíveis de interpretar devem ser rejeitados.

### BR-010 — Arquivo protegido

Arquivos protegidos por senha ou criptografados de forma que impeça a extração devem ser rejeitados.

### BR-011 — Validação real do arquivo

A extensão do arquivo não deve ser considerada suficiente para determinar seu formato.

O sistema deve validar:

- extensão;
- MIME type quando disponível;
- estrutura real do arquivo.

### BR-012 — Retenção do currículo

O arquivo original não deve ser armazenado permanentemente.

O arquivo poderá existir temporariamente durante o processamento e deverá ser removido após o período necessário.

### BR-013 — Dados extraídos

O texto e os dados extraídos devem possuir retenção limitada ao tempo necessário para o processamento.

---

## 3. Regras da descrição da vaga

### BR-014 — Descrição obrigatória

A descrição da vaga é obrigatória.

### BR-015 — Conteúdo mínimo

A descrição da vaga deve possuir pelo menos 30 caracteres úteis.

### BR-016 — Conteúdo máximo

A descrição da vaga não pode ultrapassar 3000 caracteres.

### BR-017 — Conteúdo textual

A descrição da vaga não pode ser composta exclusivamente por números ou caracteres especiais.

Números e caracteres especiais são permitidos quando fizerem parte de conteúdo semanticamente válido.

Exemplos válidos:

- .NET 10;
- Java 21;
- SQL Server 2022;
- 3 anos de experiência;
- C#;
- C++.

---

## 4. Regras de entrada textual

As regras desta seção devem ser implementadas por componentes reutilizáveis.

API, Application, Domain e Frontend não devem possuir versões diferentes da mesma regra.

### BR-018 — Valor obrigatório

Campos textuais obrigatórios não podem receber:

- null;
- string vazia;
- string contendo somente espaços.

### BR-019 — Espaços nas extremidades

Não são permitidos espaços no início ou no final do conteúdo enviado.

### BR-020 — Espaços consecutivos

Não são permitidos dois ou mais espaços consecutivos.

Exemplo inválido:

`João  Silva`

Exemplo válido:

`João Silva`

### BR-021 — Primeiro caractere

O primeiro caractere de um campo textual não pode ser um caractere especial quando isso não fizer sentido semântico para o campo.

O caractere `.` pode ser aceito como primeiro caractere em conteúdos técnicos nos quais isso seja semanticamente válido.

Exemplo válido:

`.NET`

Para nome de pessoa, o ponto inicial não é permitido.

### BR-022 — Caracteres especiais consecutivos

Campos que representam valores estruturados, como nome de pessoa, não podem possuir dois caracteres especiais consecutivos.

Exemplos inválidos:

`João--Silva`

`João@@Silva`

`João@#Silva`

`João-@Silva`

`João..Silva`

### BR-023 — Caracteres especiais semanticamente válidos

Caracteres especiais isolados podem ser permitidos quando fizerem sentido para o conteúdo.

Exemplos:

`João-Pedro`

`C# Developer`

`ASP.NET Core`

`Node.js`

### BR-024 — Caracteres acentuados

Caracteres acentuados são permitidos.

Exemplos:

`João`

`Análise`

`Desenvolvimento`

`Programação`

### BR-025 — Números

Números são permitidos em currículo e descrição de vaga quando fizerem sentido semântico.

Exemplos:

`Java 21`

`.NET 10`

`SQL Server 2022`

`3 anos de experiência`

Números não são permitidos como conteúdo exclusivo de um nome de pessoa.

### BR-026 — Conteúdo somente numérico

Currículo e descrição de vaga não podem ser compostos exclusivamente por números.

Exemplo inválido:

`12345678901234567890`

### BR-027 — Conteúdo somente especial

Currículo e descrição de vaga não podem ser compostos exclusivamente por caracteres especiais.

Exemplo inválido:

`@@@###---...`

---

## 5. Regras para nome de pessoa

### BR-028 — Nome obrigatório

O nome da pessoa é obrigatório.

### BR-029 — Nome não vazio

O nome não pode ser:

- null;
- vazio;
- composto somente por espaços.

### BR-030 — Nome somente numérico

O nome não pode ser composto exclusivamente por números.

### BR-031 — Início do nome

O nome não pode começar com:

- número;
- caractere especial.

### BR-032 — Espaços no nome

Espaços entre nomes são permitidos.

Exemplo:

`João Pedro Silva`

### BR-033 — Espaços consecutivos no nome

Não são permitidos espaços consecutivos.

### BR-034 — Hífen em nomes

O hífen pode ser utilizado quando fizer sentido no nome.

Exemplo:

`João-Pedro`

### BR-035 — Acentuação no nome

Caracteres acentuados são permitidos.

### BR-036 — Palavras inadequadas

O nome deve passar pela validação de conteúdo inadequado.

---

## 6. Regras de conteúdo inadequado, palavras chulas e palavrões

### BR-037 — Validação de conteúdo inadequado

Currículo, descrição da vaga e nome da pessoa devem passar por uma validação de conteúdo inadequado.

A validação deve considerar:

* palavrões;
* palavras chulas;
* termos sexuais inadequados ao contexto do sistema;
* termos fisiológicos inadequados ao contexto profissional;
* expressões vulgares ou de caráter ofensivo;
* formas comuns de ofuscação;
* termos em português;
* termos em inglês.

### BR-038 — Normalização antes da detecção

Antes da identificação de conteúdo inadequado, o sistema deve normalizar o texto considerando, quando aplicável:

* diferença entre maiúsculas e minúsculas;
* acentuação;
* caracteres especiais;
* asteriscos;
* separadores;
* repetição de caracteres;
* substituição de letras por números;
* formas simples de ofuscação.

Exemplos que devem ser considerados equivalentes quando a normalização permitir:

`caralho`

`ca***lho`

`c4r4lh0`

`cocô`

`coco`

`cu cabeludo`

`cucabeludo`

### BR-039 — Exemplos de termos inadequados

A lista inicial deve contemplar termos como:

**Português:**

* caralho;
* puta;
* piru;
* piroca;
* pica;
* buceta;
* vagina;
* pênis;
* cueca;
* calcinha;
* porra;
* cuzinho;
* cusinho;
* cuzão;
* cusão;
* pau;
* foda;
* foda-se;
* fodasse;
* fuder;
* fode;
* sexo;
* fezes;
* urina;
* cocô;
* coco;
* xixi;
* mijar;
* defecar;
* cucabeludo;
* cu cabeludo.

**Inglês:**

* sex;
* fuck;
* cock;
* asshole;
* pussy;
* bastard;
* bitch;
* bullshit;
* crap;
* damn;
* douche;
* douchebag;
* fag;
* faggot;
* jerk;
* motherfucker;
* shit;
* shitty;
* slut;
* whore;
* wtf;
* dick.

A lista não deve ficar limitada exclusivamente a esses exemplos.

### BR-040 — Prevenção de falso positivo

A detecção não deve bloquear um conteúdo apenas porque uma sequência curta de caracteres aparece dentro de outra palavra.

Exemplo:

`cu`

isoladamente não deve ser considerado suficiente para bloquear um conteúdo.

A detecção deve utilizar limites de palavra, contexto e/ou normalização apropriada.

Termos compostos devem ser reconhecidos mesmo quando escritos juntos ou separados por espaços, desde que a normalização permita identificar a expressão.

A validação deve evitar correspondências indevidas em palavras maiores, sem permitir que separadores ou caracteres de ofuscação sejam utilizados para contornar a restrição.

### BR-041 — Termos técnicos

A validação de conteúdo inadequado não deve bloquear termos técnicos legítimos apenas por possuírem caracteres semelhantes a termos inadequados.

Exemplos:

- C#;
- C++;
- .NET;
- Node.js;
- ASP.NET.

---

## 7. Parser

### BR-042 — Responsabilidade do Parser

O MatchCV.Parser é responsável pela extração e validação estrutural dos documentos.

### BR-043 — Parser não substituído pela IA

O Parser responde principalmente:

> O que existe no documento?

A IA responde principalmente:

> O que essas informações significam em relação à vaga?

A IA não substitui o parser.

### BR-044 — Resultado estruturado

O Parser deve retornar uma representação estruturada contendo, quando aplicável:

- nome do arquivo;
- tipo do arquivo;
- tamanho;
- quantidade de páginas;
- texto extraído;
- possibilidade de extração;
- estrutura de coluna;
- presença de imagens;
- proteção por senha.

### BR-045 — Formatos do Parser

O Parser deve suportar:

- PDF;
- DOC;
- DOCX.

---

## 8. Inteligência artificial

### BR-046 — Análise semântica

A comparação semântica entre currículo e vaga deve utilizar inteligência artificial.

### BR-047 — Dois provedores

O sistema deve possuir exatamente dois provedores de IA configurados na arquitetura.

Os provedores específicos ainda podem ser definidos.

### BR-048 — Fallback

O segundo provedor pode ser utilizado quando ocorrer uma falha elegível do primeiro provedor, principalmente falhas temporárias de disponibilidade ou serviço.

Falhas de configuração, como credenciais inválidas, não devem ser tratadas automaticamente da mesma maneira que uma indisponibilidade temporária.

### BR-049 — Uma consulta

A troca de provedor durante uma análise continua representando uma única consulta do usuário.

### BR-050 — Não inventar informações

A IA não pode inventar:

- experiências;
- empresas;
- cargos;
- tecnologias;
- formação;
- certificações;
- resultados;
- responsabilidades;
- competências;
- projetos;
- conquistas.

### BR-051 — Origem das informações

O resultado deve distinguir, quando aplicável:

- informação explicitamente encontrada no currículo;
- informação fornecida separadamente pelo candidato;
- interpretação da IA;
- requisito não evidenciado.

### BR-052 — Resultado da análise

A análise deve contemplar:

- requisitos evidenciados;
- requisitos não evidenciados;
- possíveis lacunas;
- problemas do currículo;
- sugestões de melhoria.

O sistema não deve ter como objetivo principal produzir apenas um percentual de aderência.

---

## 9. Consultas

### BR-053 — V1 sem limite

A V1 não possui limite de consultas.

### BR-054 — Limite futuro

Após a implementação de autenticação:

- USER terá direito a 3 consultas durante toda a vida da conta;
- ADMIN terá consultas ilimitadas.

O limite será vitalício e não mensal.

### BR-055 — Falha de validação

Uma tentativa que falhar durante a validação não deve consumir uma consulta.

### BR-056 — Controle independente

O controle de consultas deve ser independente do Parser e da integração com IA.

---

## 10. Usuários

### BR-057 — Criação de usuário

Usuários comuns poderão ser criados pelo sistema.

### BR-058 — Administrador inicial

A conta inicial de administrador será criada pela API utilizando `curl`.

Não haverá cadastro público de administrador pelo frontend.

### BR-059 — Autenticação

A autenticação será implementada posteriormente.

### BR-060 — Autorização

A autorização utilizará os papéis:

- USER;
- ADMIN.

### BR-061 — Consultas por usuário

Quando autenticação estiver implementada, o controle de consultas será associado ao usuário autenticado.

---

## 11. Privacidade e retenção

### BR-062 — Não armazenar currículo permanentemente

O currículo original não deve ser armazenado permanentemente.

### BR-063 — Retenção temporária

Arquivos e dados extraídos poderão permanecer temporariamente durante o processamento.

O período exato de retenção ainda será definido.

### BR-064 — Minimização de dados

O sistema deve armazenar somente os dados necessários para executar suas funções.

### BR-065 — Logs

Logs não devem conter o currículo completo, descrição completa da vaga ou outros dados pessoais desnecessários.

### BR-066 — Repositório

Currículos reais de candidatos não devem ser armazenados no repositório do projeto.

---

## 12. Segurança

### BR-067 — Segredos

Segredos não devem ser armazenados no código-fonte.

### BR-068 — Configuração

Configurações sensíveis devem utilizar variáveis de ambiente.

### BR-069 — Exemplo de configuração

O arquivo `.env.example` deve documentar as variáveis necessárias sem conter credenciais reais.

### BR-070 — Validação antes de processamento

Limites de upload e validações básicas devem ocorrer antes de operações potencialmente caras, como processamento de documentos e chamadas de IA.

---

## 13. Arquitetura

### BR-071 — MatchCV.Api

Responsável pela exposição HTTP da aplicação.

### BR-072 — MatchCV.Application

Responsável pelos casos de uso e pela orquestração da aplicação.

### BR-073 — MatchCV.Domain

Responsável pelos conceitos centrais e regras de negócio do domínio.

### BR-074 — MatchCV.Infrastructure

Responsável por persistência e integrações de infraestrutura.

### BR-075 — MatchCV.AI

Responsável pela abstração e integração dos provedores de inteligência artificial.

### BR-076 — MatchCV.Parser

Responsável pelo processamento e extração dos documentos.

### BR-077 — MatchCV.Worker

Responsável por processamento assíncrono quando necessário.

### BR-078 — MatchCV.Tests

Responsável pelos testes automatizados.

### BR-079 — MatchCV.Db

Responsável pelos recursos relacionados ao banco de dados.

### BR-080 — MatchCV.Docs

Responsável pela documentação do projeto.

### BR-081 — MatchCV.Frontend

Responsável pela interface do usuário.

### BR-082 — Banco de dados

O banco de dados da aplicação será SQL Server executado em Docker durante o desenvolvimento.

### BR-083 — Sistemas operacionais

O projeto deve ser desenvolvido considerando compatibilidade com Windows e Linux.

### BR-084 — Docker

Docker e Docker Compose devem ser utilizados para os componentes aplicáveis do ambiente de desenvolvimento.

---

## 14. Qualidade

### BR-085 — Testes unitários

Regras de negócio relevantes devem possuir testes unitários.

### BR-086 — Testes de integração

Integrações importantes devem possuir testes de integração.

### BR-087 — Testes do Parser

Cada formato suportado pelo Parser deve possuir testes específicos.

### BR-088 — Testes de IA

Os testes da integração de IA não devem depender obrigatoriamente de chamadas reais aos provedores.

Mocks ou implementações falsas devem ser utilizados nos testes automatizados.

---

## 15. Fluxo inicial

A V1 seguirá o fluxo:

Usuário
→ upload do currículo
→ validação do arquivo
→ Parser
→ extração e normalização
→ validação do conteúdo
→ descrição da vaga
→ validação da descrição
→ análise por IA
→ comparação currículo × vaga
→ resultado

Autenticação, autorização e controle de consultas serão incorporados posteriormente.