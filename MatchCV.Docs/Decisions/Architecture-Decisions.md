# Decisões Arquiteturais — MatchCV

## ADR-001 — Utilização de SQL Server

### Contexto

O projeto necessita de um banco relacional para persistência de usuários, descrições de vagas e resultados de análise.

### Decisão

Utilizar Microsoft SQL Server 2022.

### Consequências

- Utilização de T-SQL.
- Driver Python `pyodbc`.
- Migrações compatíveis com SQL Server.
- Ambiente local via Docker.

---

## ADR-002 — Separação em camadas

### Contexto

O projeto precisa manter regras de negócio independentes de infraestrutura e fornecedores externos.

### Decisão

Organizar o sistema em Domain, Application, Infrastructure, Parser, AI, API, Frontend e Worker.

### Consequências

- Redução de acoplamento.
- Maior testabilidade.
- Contratos explícitos.
- Implementações concretas fora da camada de aplicação.

---

## ADR-003 — Abstração dos provedores de IA

### Contexto

A aplicação não deve depender permanentemente de um único fornecedor.

### Decisão

Utilizar uma interface comum de provedor e um serviço coordenador com fallback.

### Consequências

- Possibilidade de substituição de provedores.
- Tratamento centralizado de falhas.
- Uma análise permanece uma consulta mesmo com fallback.

---

## ADR-004 — Não persistir permanentemente o currículo original

### Contexto

Currículos contêm dados pessoais e informações profissionais.

### Decisão

O arquivo original deve ser processado temporariamente e não armazenado permanentemente.

### Consequências

- Uso de processamento temporário.
- Minimização de dados.
- Cuidados especiais com logs e arquivos temporários.

---

## ADR-005 — Análise sem invenção de qualificações

### Contexto

O sistema utiliza IA para comparar currículo e vaga.

### Decisão

A IA não pode inventar experiências, tecnologias, cargos, empresas, certificações ou resultados.

### Consequências

A resposta deve separar evidência, ausência de evidência, lacunas e sugestões.

---

## ADR-006 — Documentação modular

### Contexto

Um README excessivamente extenso dificulta manutenção e consulta.

### Decisão

Manter um README principal conciso e documentos separados por responsabilidade.

### Consequências

- Navegação por links relativos.
- Documentação específica por módulo.
- Atualização mais simples.
- Planejamento separado do status de implementação.
