# Frontend — MatchCV

## 1. Objetivo

Documentar a interface de usuário do MatchCV.

## 2. Objetivo funcional

Permitir que o candidato envie um currículo e uma descrição de vaga e receba uma análise estruturada.

## 3. Telas previstas

### Página inicial

Apresentação do MatchCV e acesso à funcionalidade de análise.

### Tela de análise

Campos:

- Nome ou identificação do candidato, quando necessário.
- Upload de currículo.
- Descrição da vaga.
- Ação para iniciar análise.

### Tela de resultado

Seções:

- Requisitos evidenciados.
- Requisitos não evidenciados.
- Lacunas identificadas.
- Problemas do currículo.
- Sugestões de melhoria.

### Autenticação

Telas previstas para login e cadastro conforme a implementação do sistema de usuários.

### Área administrativa

Área restrita para operações administrativas previstas.

## 4. Componentes previstos

- Upload de arquivo.
- Campo de descrição da vaga.
- Validação de formulário.
- Indicador de processamento.
- Exibição de erros.
- Exibição de resultados.
- Componentes de autenticação.

## 5. Integração com API

A comunicação será realizada por HTTP/HTTPS.

A interface não deve acessar diretamente o SQL Server ou os provedores de IA.

## 6. Estados da interface

- Inicial.
- Validando.
- Enviando.
- Processando.
- Concluído.
- Falha.

## 7. Validações

O frontend poderá antecipar validações de tamanho, formato e campos obrigatórios.

A validação definitiva deverá ocorrer também no backend.

## 8. Acessibilidade

A interface deverá considerar:

- Navegação por teclado.
- Rótulos acessíveis.
- Mensagens de erro compreensíveis.
- Contraste adequado.
- Compatibilidade com tecnologias assistivas.

## 9. Privacidade

O frontend não deve manter cópias desnecessárias de currículos ou dados sensíveis.

## 10. Status

Frontend documentado como planejamento. Framework, componentes concretos e telas serão atualizados após implementação.
