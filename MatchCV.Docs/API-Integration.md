# Integração da API — MatchCV

## Visão geral

O frontend se comunica com a API FastAPI por HTTP/HTTPS. A API coordena autenticação, validação de entrada, casos de uso e acesso aos repositórios; o frontend não acessa diretamente o SQL Server nem os provedores de IA.

## Fluxo de análise

```text
Frontend
  |
  | POST /analysis/resume (autenticado)
  v
API / AnalysisRouter
  |
  | valida texto ou arquivo + descrição da vaga
  v
AnalyzeResumeUseCase
  |
  | cria e enfileira a análise
  v
SQL Server / fila
  |
  v
Worker
  |
  +--> Parser / IA
  |
  v
Persistência do estado e do resultado
  |
  v
GET /analysis/{analysis_id} (proprietário autenticado)
```

A rota de submissão aceita a descrição da vaga e exatamente uma das opções: texto do currículo ou arquivo. A resposta de sucesso é HTTP `202 Accepted` com o identificador e o estado inicial. A consulta posterior retorna o estado e, quando disponível, o resultado.

Os caminhos completos podem incluir prefixos configurados na aplicação. Consulte o Swagger ativo ou `MatchCV.Api/main.py`; não presuma o prefixo `/api/v1` sem verificá-lo na configuração atual.

## Autenticação

As rotas de autenticação estão sob o prefixo `/auth`. O login retorna um token de acesso; rotas protegidas recebem o token Bearer. O frontend deve tratar erros de autenticação e autorização sem expor tokens ou detalhes internos.

## Camadas

- **API:** schemas HTTP, códigos de resposta e dependências.
- **Application:** casos de uso e coordenação do fluxo.
- **Domain:** regras e entidades de negócio.
- **Parser:** validação e extração de texto dos documentos.
- **AI:** integração com provedores externos.
- **Infrastructure:** SQL Server e repositórios.
- **Worker:** processamento assíncrono da fila.

As dependências concretas devem ser conectadas por configurações e injeção de dependência; regras de negócio não devem ficar duplicadas no frontend.

## Banco e fila

A persistência utiliza SQL Server e `pyodbc`. A fila e as migrations correspondentes precisam estar aplicadas no banco usado pelo ambiente. A configuração da API e do worker deve apontar para a mesma base e usar os mesmos parâmetros necessários para ler e processar tarefas.

Quando o processamento assíncrono depende de uma variável de ambiente, confirme seu valor no serviço em execução antes de esperar que a API processe tarefas localmente.

## Segurança e privacidade

- A consulta de análise deve respeitar o usuário proprietário.
- Currículo e descrição da vaga são dados não confiáveis.
- Não registrar conteúdo integral de currículo, tokens ou credenciais.
- Não persistir permanentemente o arquivo original sem necessidade e política aprovada.
- Não usar banco de teste para dados de produção.

## Diagnóstico

Ao investigar uma falha, verifique separadamente: resposta HTTP, logs sanitizados da API, disponibilidade do banco, estado da fila, logs do worker e resposta do provedor de IA. Não conclua que uma análise foi concluída apenas porque a submissão retornou 202.
