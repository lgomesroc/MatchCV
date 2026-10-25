# Decisões Arquiteturais — MatchCV

Este documento registra decisões relevantes. Decisões descrevem o racional do projeto; comportamento efetivo deve ser verificado no código e nos testes.

## ADR-001 — SQL Server

**Decisão:** utilizar Microsoft SQL Server como banco relacional, com acesso Python via `pyodbc` e migrations SQL versionadas.

**Consequências:** consultas devem ser parametrizadas; migrations precisam ser aplicadas em ordem; bancos de desenvolvimento, teste e produção devem ser separados. A instância de teste usa configuração própria.

## ADR-002 — Separação modular

**Decisão:** manter módulos distintos para API, Application, Domain, Infrastructure, Parser, AI, Worker, Login, banco, testes e frontend.

**Consequências:** regras de negócio devem permanecer testáveis e não ficar duplicadas na API ou no frontend. Integrações concretas devem ser isoladas por contratos quando apropriado.

## ADR-003 — Provedores de IA por abstração

**Decisão:** integrar provedores externos por uma camada comum, permitindo substituição e fallback para falhas elegíveis.

**Consequências:** credenciais e parâmetros são configurados por ambiente. Uma tentativa de fallback pertence à mesma análise e não deve gerar uma nova cobrança de cota de negócio. Não se garante que um provedor esteja operacional apenas por estar configurado.

## ADR-004 — Minimização de dados de currículo

**Decisão:** não armazenar permanentemente o arquivo original do currículo.

**Consequências:** arquivos temporários devem ser removidos após o processamento; logs não devem conter o conteúdo integral; testes devem usar dados sintéticos.

## ADR-005 — Evidência sem invenção

**Decisão:** o sistema não deve inventar experiências, cargos, empresas, tecnologias, formação, certificações ou resultados.

**Consequências:** o resultado distingue requisitos evidenciados, requisitos não evidenciados, lacunas, problemas do currículo e sugestões. Ausência de evidência não equivale a prova de ausência de competência.

## ADR-006 — Documentação modular

**Decisão:** manter o README principal para visão geral e guias separados por tema.

**Consequências:** links relativos devem ser mantidos válidos e mudanças de comportamento/configuração devem atualizar os documentos relacionados.

## ADR-007 — Análise assíncrona

**Decisão:** a submissão de análise enfileira o trabalho e retorna HTTP 202 antes do resultado final.

**Consequências:** a interface precisa consultar o estado posterior; API e worker devem compartilhar a configuração necessária para acessar o banco e processar a fila. Um HTTP 202 não garante que o worker terminou ou que a análise foi concluída.

## ADR-008 — Autenticação e cota

**Decisão:** proteger as operações de análise e associar cada análise ao usuário proprietário. Usuários comuns têm cota mensal de três análises; administradores não têm esse limite.

**Consequências:** a autorização deve ser verificada no backend; cadastro público não pode criar administradores; bootstrap administrativo exige segredo de configuração.

## ADR-009 — Ambientes de teste isolados

**Decisão:** usar uma instância SQL Server separada para testes de integração.

**Consequências:** credenciais e dados de teste são separados dos ambientes normais. A execução da suíte completa depende de a instância estar saudável e de as credenciais configuradas corresponderem às credenciais reais do contêiner.
