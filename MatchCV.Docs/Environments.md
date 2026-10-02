# Ambientes — MatchCV

## 1. Objetivo

Definir os ambientes utilizados no desenvolvimento, testes, homologação e produção do MatchCV.

## 2. Ambientes previstos

| Ambiente    | Finalidade                        |
| ----------- | --------------------------------- |
| Development | Desenvolvimento local             |
| Test        | Execução de testes automatizados  |
| Staging     | Validação antes da publicação     |
| Production  | Ambiente utilizado pelos usuários |

## 3. Development

Ambiente utilizado pelos desenvolvedores.

Componentes previstos:

* Python.
* Docker Desktop.
* SQL Server 2022.
* Driver ODBC 18.
* Git.
* Visual Studio Code ou IDE compatível.

O banco local poderá utilizar o container:

`matchcv-sqlserver`

Porta padrão:

`1433`

## 4. Test

Ambiente destinado à execução de testes unitários, de integração e de componentes.

Os testes não devem depender de dados reais de usuários.

Dados de teste devem ser artificiais e descartáveis.

## 5. Staging

Ambiente de homologação destinado à validação integrada da aplicação.

Deve utilizar configurações separadas de desenvolvimento e produção.

Não deve compartilhar credenciais ou banco de dados de produção.

## 6. Production

Ambiente de execução oficial.

Requisitos:

* Credenciais protegidas.
* Configuração segura.
* Logs sem dados pessoais desnecessários.
* Monitoramento de falhas.
* Política de backup.
* Controle de acesso.
* Estratégia de atualização e recuperação.

## 7. Variáveis de ambiente

Exemplo:

```env
APP_ENV=development

DATABASE_HOST=localhost
DATABASE_PORT=1433
DATABASE_NAME=MatchCV
DATABASE_USER=sa
DATABASE_PASSWORD=CHANGE_ME

AI_PRIMARY_PROVIDER=
AI_FALLBACK_PROVIDER=
```

Os nomes definitivos das variáveis devem acompanhar a implementação de `AppSettings.py` e `AISettings.py`.

## 8. Arquivos de configuração

* `.env.example`: modelo de configuração.
* `.env`: configuração local, não versionada.
* `docker-compose.yml`: serviços locais.
* `requirements.txt`: dependências Python.

## 9. Segurança das configurações

* Não armazenar segredos no Git.
* Não reutilizar senhas entre ambientes.
* Não incluir tokens em mensagens de erro.
* Não imprimir variáveis sensíveis em logs.
* Utilizar mecanismos de gerenciamento de segredos em produção.

## 10. Compatibilidade

O projeto deve considerar desenvolvimento em Windows e Linux.

Comandos específicos de ambiente devem ser documentados separadamente quando não forem compatíveis entre sistemas operacionais.

## 11. Situação

Os ambientes de desenvolvimento e testes estão previstos na arquitetura. Homologação e produção dependem da definição da infraestrutura de implantação.
