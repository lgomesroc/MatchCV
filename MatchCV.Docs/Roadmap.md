
# Roadmap — MatchCV

## 1. Objetivo

Registrar o planejamento de desenvolvimento e acompanhar a evolução do MatchCV.

## 2. Status

- [x] Estrutura inicial do repositório.
- [x] Definição do SQL Server como banco de dados.
- [x] Migração da estrutura inicial para SQL Server.
- [x] Separação inicial de módulos.
- [x] Definição das abstrações iniciais de IA.
- [x] Definição do contrato de análise.
- [x] Início da implementação dos parsers.
- [ ] Conclusão da abstração do parser na Application.
- [ ] Adapter de parser na Infrastructure.
- [ ] Validação rigorosa de arquivos.
- [ ] Suporte efetivo a DOC legado.
- [ ] Validação real de paginação DOCX.
- [ ] Conclusão dos testes unitários.
- [ ] Testes de integração com SQL Server.
- [ ] Implementação completa da API.
- [ ] Autenticação.
- [ ] Autorização USER/ADMIN.
- [ ] Implementação dos provedores reais de IA.
- [ ] Tratamento de prompt injection.
- [ ] Frontend.
- [ ] Integração frontend/API.
- [ ] Pipeline CI.
- [ ] Pipeline CD.
- [ ] Implantação.
- [ ] Documentação operacional final.

## 3. Fase 1 — Fundação

Objetivos:

- Organização do repositório.
- Definição das camadas.
- Entidades de domínio.
- Contratos de aplicação.
- Configuração do banco.
- Documentação técnica.

## 4. Fase 2 — Processamento

Objetivos:

- Parser PDF.
- Parser DOCX.
- Estratégia para DOC.
- Validação de arquivos.
- Extração de texto.
- Testes de processamento.

## 5. Fase 3 — Análise

Objetivos:

- Provedores de IA.
- Fallback.
- Resposta estruturada.
- Validação de resultados.
- Proteção contra conteúdo malicioso.

## 6. Fase 4 — API e segurança

Objetivos:

- Endpoints.
- Autenticação.
- Autorização.
- Tratamento de erros.
- Persistência integrada.

## 7. Fase 5 — Frontend

Objetivos:

- Formulário de análise.
- Upload.
- Integração com API.
- Exibição dos resultados.
- Tratamento de estados e erros.

## 8. Fase 6 — Qualidade e publicação

Objetivos:

- Testes automatizados.
- CI/CD.
- Segurança.
- Observabilidade.
- Implantação.

## 9. Critério de conclusão

Uma etapa somente deverá ser marcada como concluída após implementação e validação compatíveis com seu escopo.

## 10. Observação

O roadmap é um documento vivo e deverá ser atualizado conforme o desenvolvimento real.