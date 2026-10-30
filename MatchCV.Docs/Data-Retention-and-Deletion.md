# Política operacional de retenção e exclusão de dados

**Status:** política proposta para revisão antes de ativação em produção. Os prazos abaixo são regras operacionais desejadas; não significam que exista hoje um job automático de expurgo.

## Dados e prazos

| Categoria | Retenção operacional proposta | Tratamento ao vencer o prazo |
|---|---|---|
| Arquivo original enviado | Somente durante a requisição/processamento | Fechar o upload e liberar o conteúdo em memória ao terminar; não persistir o arquivo em disco ou no SQL Server |
| Texto extraído e descrição da vaga na fila | Até a tarefa terminar; em falha, até a rotina de recuperação/triagem decidir | Apagar o payload cifrado quando a tarefa for concluída ou marcada como falha |
| Resultado de análise concluída ou falha | 12 meses após a criação da análise | Excluir resultado e dados associados, salvo obrigação legal documentada ou solicitação de retenção válida |
| Metadados de fila concluída/falha | 30 dias após a finalização | Excluir o registro da fila; não manter payload |
| Conta ativa | Até o titular solicitar exclusão ou existir outra base válida para retenção | Remover dados pessoais da conta no procedimento de exclusão |
| Token de recuperação | 15 minutos e uso único | Token original nunca é armazenado; hashes vencidos/usados devem ser eliminados em até 24 horas por limpeza operacional |
| Logs técnicos | 30 dias, com acesso restrito | Rotacionar e eliminar logs vencidos; nunca incluir conteúdo de currículo, senha, token, chave ou string de conexão |

Antes de anunciar estes prazos como garantidos, o responsável pela operação deve aprovar a política, configurar a retenção de logs e implementar/agendar as rotinas de expurgo descritas neste documento. Backup e cópias do provedor devem ter prazo próprio documentado; excluir uma linha do banco não garante remoção imediata de backups.

## Arquivos temporários e memória

A API lê o upload em memória para validar e processar o conteúdo e fecha o objeto `UploadFile` após a leitura. O parser usa buffers em memória. Não introduza diretórios temporários persistentes sem diretório dedicado, permissões restritas e limpeza garantida. Em toda alteração do fluxo de upload, mantenha o fechamento do arquivo em `finally`.

O texto extraído e a descrição da vaga são necessários na fila assíncrona, armazenados em payload cifrado. O worker deve apagar o payload ao concluir ou falhar uma tarefa. Metadados e resultados da análise podem conter informações pessoais e continuam sujeitos aos prazos acima.

## Logs e tratamento de erros

- Nunca registrar currículo, texto extraído, descrição da vaga, corpo completo de requisições, senhas, hashes de senha, tokens de sessão/recuperação, chaves de API, chaves de cifragem ou strings de conexão.
- Registrar somente tipo de exceção, estado da tarefa, identificador técnico da análise/tarefa quando necessário e mensagem fixa sanitizada.
- Não retornar stack trace, SQL, caminho interno ou detalhes de provedor ao cliente.
- Revisar também logs do host, proxy, APM, provedor de IA e SMTP. A aplicação não controla sozinha a retenção desses sistemas.
- Alterações de logging devem ter testes com valores sentinela para provar que segredos e conteúdo não aparecem nos registros.

## Solicitação de exclusão pelo titular

Ainda não existe um fluxo de autoatendimento confirmado no frontend/API. Até sua implementação, a equipe operacional deve publicar e monitorar um canal de privacidade/suporte no site e executar o procedimento abaixo; o endereço/canal oficial precisa ser configurado pelo responsável do produto antes da publicação desta política.

1. Receber a solicitação sem pedir que o titular envie currículo ou senha por e-mail.
2. Verificar a identidade por um processo proporcional e separado da senha da conta; nunca pedir senha ou token de recuperação.
3. Identificar a conta e registrar um número de protocolo, sem copiar o conteúdo do currículo para o ticket.
4. Revogar tokens de recuperação ativos e impedir novos acessos à conta durante a exclusão.
5. Em transação, excluir os resultados e os registros de fila ligados às análises do usuário, as reservas/contabilizações de cota e as descrições de vaga sem compartilhamento, e por último os dados da conta, respeitando as chaves estrangeiras e a política de backup.
6. Confirmar ao titular a conclusão e informar qualquer dado que precise ser mantido, a base e o prazo de retenção aplicável.
7. Verificar logs, exportações e backups sujeitos a ciclos de retenção separados; registrar a execução sem incluir os dados apagados.

**Não execute exclusão manual diretamente em produção sem backup validado, revisão das relações de chave estrangeira e autorização operacional.** Como o endpoint automatizado ainda não está implementado, a equipe não deve afirmar que o titular consegue excluir a conta diretamente pela interface.

## Resultados antigos e fila

- A conclusão/falha da tarefa limpa o payload cifrado da fila, mas o registro de fila permanece até o expurgo de metadados.
- O resultado da análise é mantido no SQL Server até o prazo definido ou até a exclusão autorizada.
- Tarefas pendentes/em processamento não devem ser apagadas sem primeiro cancelar ou reconciliar a análise e liberar a reserva de cota.
- O expurgo deve excluir em ordem compatível com as chaves estrangeiras e ser idempotente, auditável e testado em banco isolado.
- A implementação futura deve incluir modo de simulação, contagens antes/depois e alertas de falha; nunca executar contra produção por padrão em ambiente de teste.

## Checklist antes de declarar concluído

- [ ] Aprovar os prazos com o responsável pela privacidade e avaliar obrigações legais aplicáveis.
- [ ] Configurar o canal oficial de solicitação e publicar a política revisada.
- [ ] Implementar e agendar o expurgo de análises, metadados da fila e tokens vencidos/usados.
- [ ] Implementar endpoint autenticado ou fluxo operacional seguro de exclusão da conta.
- [ ] Definir retenção de backups e confirmar exclusão nos provedores externos.
- [ ] Testar limpeza de uploads, ausência de dados sensíveis nos logs e exclusão em banco de teste.
- [ ] Verificar métricas e logs de produção após implantação, sem consultar nem registrar currículos reais.
