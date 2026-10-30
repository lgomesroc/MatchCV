# Política operacional de retenção e exclusão de dados

**Status:** proposta operacional, ainda não aprovada nem integralmente implementada. Os prazos abaixo são metas sugeridas para revisão; não devem ser divulgados como garantias de retenção ou exclusão enquanto não forem aprovados, configurados e testados.

## Dados e prazos propostos

| Categoria | Retenção proposta | Tratamento desejado ao vencer o prazo |
|---|---|---|
| Arquivo original enviado | Somente durante a requisição/processamento | Ler o upload, fechar o objeto `UploadFile` após a leitura e não persistir o arquivo original em disco ou no SQL Server |
| Texto extraído e descrição da vaga na fila | Até a tarefa terminar; em falha operacional, até a recuperação/triagem concluir | Apagar o payload cifrado quando a tarefa for concluída ou marcada como falha |
| Resultado de análise concluída ou falha | 12 meses após a criação da análise | Excluir resultado e dados associados, salvo obrigação legal documentada ou solicitação válida de retenção |
| Metadados de fila concluída/falha | 30 dias após a finalização | Excluir o registro da fila, sem payload |
| Conta ativa | Até o titular solicitar exclusão ou existir outra base válida para retenção | Remover dados pessoais da conta por procedimento autorizado |
| Token de recuperação | 15 minutos de validade e uso único | Manter somente o hash; eliminar hashes vencidos/usados em até 24 horas por rotina de limpeza a implementar |
| Logs técnicos | 30 dias | Rotacionar e eliminar logs vencidos; nunca incluir conteúdo de currículo, senha, token, chave ou string de conexão |

Os prazos de 12 meses, 30 dias e 24 horas são propostas, não configurações comprovadas no código. O token de recuperação tem validade de 15 minutos e uso único implementados; a limpeza física dos registros vencidos/usados ainda depende de rotina operacional. A aplicação também não comprova, por si só, a retenção dos logs do host, proxy, APM, provedor de IA ou SMTP.

Antes de anunciar estes prazos como garantidos, o responsável pela operação deve aprovar a política, configurar a retenção de logs e implementar/agendar as rotinas de expurgo descritas neste documento. Backup e cópias do provedor devem ter prazo próprio documentado; excluir uma linha do banco não garante remoção imediata de backups.

## Arquivos temporários, memória e fila

A API lê o upload em memória e fecha o objeto `UploadFile` após a leitura, inclusive em caso de falha durante a leitura. Os bytes lidos são encaminhados ao fluxo de análise; o parser utiliza buffers em memória. O fechamento do `UploadFile` não significa que todas as cópias dos bytes sejam imediatamente removidas da memória do processo.

O fluxo atual não persiste o arquivo original em disco ou no SQL Server. Não introduza diretórios temporários persistentes sem diretório dedicado, permissões restritas e limpeza garantida. Em toda alteração do fluxo de upload, mantenha o fechamento do arquivo em `finally`.

O texto extraído e a descrição da vaga são necessários para o processamento assíncrono e são armazenados na fila em payload cifrado. O worker limpa o campo de payload cifrado ao marcar uma tarefa como concluída ou falha. Os metadados da fila permanecem no banco; não há, nesta implementação, comprovação de expurgo automático desses registros por idade.

Metadados e resultados da análise podem conter informações pessoais e continuam sujeitos à política de retenção que vier a ser aprovada e implementada.

## Logs e tratamento de erros

- Nunca registrar currículo, texto extraído, descrição da vaga, corpo completo de requisições, senhas, hashes de senha, tokens de sessão/recuperação, chaves de API, chaves de cifragem ou strings de conexão.
- Registrar somente tipo de exceção, estado da tarefa, identificador técnico da análise/tarefa quando necessário e mensagem fixa sanitizada.
- Não retornar stack trace, SQL, caminho interno ou detalhes de provedor ao cliente.
- Revisar também logs do host, proxy, APM, provedor de IA e SMTP. A aplicação não controla sozinha a retenção desses sistemas.
- Configurar e validar rotação e retenção nos ambientes publicados; a recomendação de 30 dias não comprova que essa configuração já exista.
- Alterações de logging devem ter testes com valores sentinela para provar que segredos e conteúdo não aparecem nos registros.

## Solicitação de exclusão pelo titular

Ainda não existe um fluxo de autoatendimento confirmado no frontend/API para exclusão da conta. Até sua implementação, a equipe operacional deve publicar e monitorar um canal de privacidade/suporte no site e executar o procedimento abaixo; o endereço/canal oficial precisa ser configurado pelo responsável do produto antes da publicação desta política.

1. Receber a solicitação sem pedir que o titular envie currículo ou senha por e-mail.
2. Verificar a identidade por um processo proporcional e separado da senha da conta; nunca pedir senha ou token de recuperação.
3. Identificar a conta e registrar um número de protocolo, sem copiar o conteúdo do currículo para o ticket.
4. Revogar tokens de recuperação ativos e impedir novos acessos à conta durante a exclusão.
5. Em transação, excluir os resultados e os registros de fila ligados às análises do usuário, as reservas/contabilizações de cota e as descrições de vaga sem compartilhamento, e por último os dados da conta, respeitando as chaves estrangeiras e a política de backup.
6. Confirmar ao titular a conclusão e informar qualquer dado que precise ser mantido, a base e o prazo de retenção aplicável.
7. Verificar logs, exportações e backups sujeitos a ciclos de retenção separados; registrar a execução sem incluir os dados apagados.

**Não execute exclusão manual diretamente em produção sem backup validado, revisão das relações de chave estrangeira e autorização operacional.** Como o endpoint automatizado ainda não está implementado, a equipe não deve afirmar que o titular consegue excluir a conta diretamente pela interface.

## Resultados antigos e fila

- A conclusão ou falha da tarefa limpa o payload cifrado da fila, mas o registro de fila permanece até eventual expurgo operacional.
- O resultado da análise é mantido no SQL Server; o prazo de 12 meses ainda é uma proposta, não um expurgo automático implementado.
- Tarefas pendentes/em processamento não devem ser apagadas sem primeiro cancelar ou reconciliar a análise e liberar a reserva de cota.
- O expurgo deve excluir em ordem compatível com as chaves estrangeiras e ser idempotente, auditável e testado em banco isolado.
- A implementação futura deve incluir modo de simulação, contagens antes/depois e alertas de falha; nunca executar contra produção por padrão em ambiente de teste.

## Checklist antes de declarar concluído

- [ ] Aprovar os prazos com o responsável pela privacidade e avaliar obrigações legais aplicáveis.
- [ ] Configurar o canal oficial de solicitação e publicar a política revisada.
- [ ] Implementar e agendar o expurgo de análises, metadados da fila e tokens vencidos/usados.
- [ ] Implementar endpoint autenticado ou fluxo operacional seguro de exclusão da conta.
- [ ] Definir retenção de backups e confirmar exclusão nos provedores externos.
- [ ] Configurar retenção e rotação de logs no host e nos serviços externos.
- [ ] Testar limpeza de uploads, ausência de dados sensíveis nos logs e exclusão em banco de teste.
- [ ] Verificar métricas e logs de produção após implantação, sem consultar nem registrar currículos reais.
