# MatchCV — Regras de Negócio

## 1. Objetivo

Este documento registra regras funcionais e identificadores para rastreabilidade. Regras documentadas precisam ser confirmadas no código e nos testes antes de serem tratadas como garantias operacionais.

O MatchCV compara currículo e descrição de vaga. O resultado deve identificar requisitos evidenciados, requisitos sem evidência suficiente, lacunas, problemas do currículo e sugestões. A IA não pode inventar fatos profissionais.

## 2. Currículos

### BR-001 — Formatos
Os formatos previstos são PDF, DOC e DOCX. A compatibilidade efetiva depende do parser instalado e dos testes de cada formato.

### BR-002 — Tamanho máximo
O limite documentado é 1 MB.

### BR-003 — Páginas
O limite documentado é duas páginas. A contagem física exata pode exigir renderização ou conversão para alguns formatos.

### BR-004 — Texto mínimo
O documento deve fornecer pelo menos 30 caracteres úteis extraídos.

### BR-005 — Texto extraível
O parser deve conseguir extrair texto suficiente para análise.

### BR-006 — PDF somente imagem
PDFs sem texto extraível não são processados por OCR no escopo documentado da V1.

### BR-007 — Imagens
A análise não deve depender de imagens para compreender informações profissionais essenciais.

### BR-008 — Colunas
A regra de negócio prioriza documentos lineares de coluna única. A detecção automática de múltiplas colunas deve ser confirmada nos testes antes de se afirmar que todos esses arquivos são rejeitados corretamente.

### BR-009 — Arquivo inválido
Arquivos corrompidos ou impossíveis de interpretar devem falhar de forma controlada.

### BR-010 — Arquivo protegido
Arquivos protegidos por senha que impeçam a extração devem ser rejeitados.

### BR-011 — Validação do formato
A extensão isolada não comprova o formato real. A validação deve considerar a estrutura do arquivo e os mecanismos disponíveis.

### BR-012 — Retenção
O arquivo original deve ser temporário e não armazenado permanentemente.

### BR-013 — Texto extraído
A retenção do texto extraído deve limitar-se ao necessário para executar a análise e disponibilizar o resultado, conforme a política de retenção definida para o ambiente.

## 3. Descrição da vaga

### BR-014 — Obrigatória
A descrição da vaga é obrigatória.

### BR-015 — Mínimo
O limite documentado é 30 caracteres úteis.

### BR-016 — Máximo
A descrição da vaga aceita até 15.000 caracteres. O texto de currículo informado diretamente também aceita até 15.000 caracteres. O limite de upload de arquivo permanece em 1 MB e não é alterado por esta regra.

### BR-017 — Conteúdo textual
A descrição deve conter conteúdo textual válido. Números e caracteres especiais são permitidos quando semanticamente válidos, como `.NET 10`, `C++` e `Java 21`.

## 4. Validação textual

### BR-018 — Obrigatoriedade
Campos obrigatórios não podem ser nulos, vazios ou conter apenas espaços.

### BR-019 — Espaços externos
A entrada deve ser normalizada/validada quanto a espaços no início e no final.

### BR-020 — Espaços consecutivos
Campos sujeitos a essa regra não devem aceitar espaços consecutivos sem necessidade semântica.

### BR-021 — Primeiro caractere
A regra depende do campo. Conteúdo técnico pode começar por ponto, como `.NET`; nomes de pessoas têm validação própria.

### BR-022 — Especiais consecutivos
Campos estruturados devem rejeitar sequências de caracteres especiais que não sejam semanticamente válidas.

### BR-023 — Especiais válidos
Caracteres como hífen, ponto e sinais de linguagem são permitidos quando necessários, por exemplo em `C#`, `C++`, `Node.js` e `ASP.NET`.

### BR-024 — Acentos
Caracteres acentuados devem ser aceitos quando válidos para o campo.

### BR-025 — Números
Números podem aparecer em currículo e descrição de vaga quando fizerem sentido semântico.

### BR-026 — Somente números
Currículo e descrição de vaga não devem consistir exclusivamente em números.

### BR-027 — Somente especiais
Currículo e descrição de vaga não devem consistir exclusivamente em caracteres especiais.

## 5. Nome da pessoa

### BR-028 — Obrigatório
O nome é obrigatório quando exigido pelo fluxo de cadastro.

### BR-029 — Não vazio
O nome não pode ser nulo, vazio ou composto apenas por espaços.

### BR-030 — Somente números
O nome não pode consistir exclusivamente em números.

### BR-031 — Início
O nome não deve começar com número ou caractere especial sem significado válido.

### BR-032 — Espaços
Espaços simples entre partes do nome são permitidos.

### BR-033 — Espaços consecutivos
Espaços consecutivos devem ser rejeitados ou normalizados de acordo com o validador utilizado.

### BR-034 — Hífen
Hífens podem ser usados em nomes quando apropriados.

### BR-035 — Acentos
Nomes com caracteres acentuados devem ser aceitos.

### BR-036 — Conteúdo inadequado
O nome está sujeito à validação de conteúdo inadequado implementada pelo projeto.

## 6. Conteúdo inadequado

### BR-037 — Validação
Os campos aplicáveis devem ser validados contra conteúdo inadequado segundo a política do projeto.

### BR-038 — Normalização
A detecção pode normalizar caixa, acentos, separadores, repetição de caracteres e substituições comuns por números, conforme a implementação.

### BR-039 — Lista de termos
A lista concreta de termos e padrões deve ser mantida no componente de validação de conteúdo. Este documento não deve ser considerado a fonte operacional dessa lista.

### BR-040 — Falsos positivos
A validação deve evitar bloquear palavras legítimas apenas por conterem uma sequência curta de caracteres. Termos técnicos e contextos legítimos precisam de testes de regressão.

### BR-041 — Termos técnicos
Termos como `C#`, `C++`, `.NET`, `Node.js` e `ASP.NET` não devem ser bloqueados indevidamente.

## 7. Parser

### BR-042 — Responsabilidade
O parser valida e extrai o conteúdo do documento.

### BR-043 — Limite entre parser e IA
O parser identifica o conteúdo presente; a IA interpreta sua relação com a vaga. A IA não substitui a validação do arquivo.

### BR-044 — Resultado
Os metadados retornados dependem do parser e podem incluir nome, tipo, tamanho, páginas, texto e indicadores de extração. Não se deve assumir que cada metadado é fornecido para todos os formatos sem verificar a implementação.

### BR-045 — Formatos
PDF, DOC e DOCX são os formatos previstos; suporte completo precisa ser comprovado por testes.

## 8. Inteligência artificial

### BR-046 — Análise semântica
A camada de IA compara o conteúdo disponível com os requisitos da vaga.

### BR-047 — Provedores
O projeto possui uma camada de integração que abstrai provedores externos. O número e os nomes de provedores ativos dependem da configuração e da implementação atual.

### BR-048 — Fallback
Fallback só deve ocorrer para falhas classificadas como elegíveis pela implementação. Credenciais inválidas e erros de configuração não devem ser presumidos equivalentes a indisponibilidade temporária.

### BR-049 — Uma análise
A tentativa de fallback integra a mesma análise de negócio e não deve contar como nova análise do usuário.

### BR-050 — Não inventar
A IA não deve inventar experiências, empresas, cargos, tecnologias, formação, certificações, resultados, responsabilidades ou competências.

### BR-051 — Evidência
O resultado deve distinguir fatos evidenciados no currículo de interpretações e requisitos sem evidência suficiente.

### BR-052 — Resultado
A análise contempla requisitos evidenciados, requisitos sem evidência suficiente, lacunas, problemas do currículo e sugestões.

## 9. Cota de análises

### BR-053 — Cota vigente
A regra implementada/documentada atualmente é de três análises por usuário comum por mês-calendário UTC; administradores não estão sujeitos ao limite.

### BR-054 — Período
A cota é mensal, não vitalícia. Não use regras antigas de três análises durante toda a vida da conta.

### BR-055 — Falhas
Falhas de validação antes da reserva não devem consumir cota. Falhas posteriores devem liberar a reserva quando o fluxo de tratamento assim determinar; validar pelo código e testes.

### BR-056 — Independência
O controle de cota é uma responsabilidade distinta do parser e dos provedores de IA.

## 10. Usuários e acesso

### BR-057 — Cadastro
O cadastro público cria usuário comum.

### BR-058 — Bootstrap administrativo
A criação inicial de administrador exige operação de bootstrap protegida por segredo configurado no ambiente. Não há concessão pública de perfil administrativo.

### BR-059 — Autenticação
A autenticação por e-mail/senha e token de acesso está implementada na API.

### BR-060 — Perfis
Os papéis incluem `USER` e `ADMIN`.

### BR-061 — Propriedade da análise
A consulta de uma análise deve estar restrita ao usuário proprietário autenticado, conforme a autorização no backend.

## 11. Privacidade e retenção

### BR-062 — Arquivo original
O arquivo original não deve ser armazenado permanentemente.

### BR-063 — Temporários
Arquivos temporários devem ser removidos após o uso. O tempo de retenção de texto extraído e resultados deve ser definido por política operacional.

### BR-064 — Minimização
Persistir somente os dados necessários para as funções do produto.

### BR-065 — Logs
Não registrar currículo completo, descrição integral da vaga, credenciais ou tokens.

### BR-066 — Git
Currículos reais não devem ser adicionados ao repositório.

## 12. Segurança

### BR-067 — Segredos
Segredos não devem estar no código-fonte nem nos documentos versionados.

### BR-068 — Configuração
Configurações sensíveis devem ser fornecidas por ambiente ou mecanismo seguro.

### BR-069 — Exemplo
`.env.example` deve conter apenas nomes e exemplos não secretos de variáveis.

### BR-070 — Validação prévia
Limites e validações de entrada devem ocorrer antes de processamento caro sempre que possível.

## 13. Organização arquitetural

### BR-071 — API
`MatchCV.Api` expõe a interface HTTP.

### BR-072 — Application
`MatchCV.Application` coordena casos de uso.

### BR-073 — Domain
`MatchCV.Domain` contém entidades e regras de domínio.

### BR-074 — Infrastructure
`MatchCV.Infrastructure` implementa persistência e integrações técnicas.

### BR-075 — AI
`MatchCV.AI` integra provedores externos.

### BR-076 — Parser
`MatchCV.Parser` processa documentos.

### BR-077 — Worker
`MatchCV.Worker` executa o processamento assíncrono.

### BR-078 — Tests
`MatchCV.Tests` contém testes automatizados.

### BR-079 — Db
`MatchCV.Db` mantém migrations SQL.

### BR-080 — Docs
`MatchCV.Docs` contém a documentação técnica e funcional.

### BR-081 — Frontend
`MatchCV.Frontend` contém a interface Angular.

### BR-082 — Banco
SQL Server é utilizado para persistência, com configurações separadas por ambiente.

### BR-083 — Sistemas operacionais
O desenvolvimento contempla Windows e Linux, sujeito aos requisitos de ferramentas e drivers.

### BR-084 — Containers
Docker Compose é usado para os serviços locais e a instância SQL Server de testes.

## 14. Qualidade

### BR-085 — Testes unitários
Regras de negócio relevantes devem ter testes unitários.

### BR-086 — Testes de integração
Integrações importantes devem ter testes de integração.

### BR-087 — Parser
Cada formato suportado deve possuir testes específicos.

### BR-088 — IA
Os testes automatizados devem usar mocks/fakes sempre que possível e não depender obrigatoriamente de chamadas pagas a provedores reais.

## 15. Fluxo de análise

O fluxo atual é assíncrono: envio autenticado, validação, reserva de cota, criação/enfileiramento da análise, resposta HTTP 202, processamento pelo worker e consulta posterior do estado/resultado pelo proprietário. HTTP 202 confirma aceitação da tarefa, não conclusão da análise.

## Manutenção

Quando o comportamento do código mudar, atualize as regras relacionadas e seus testes. Este documento não substitui o código, as migrations nem a configuração efetiva do ambiente.
