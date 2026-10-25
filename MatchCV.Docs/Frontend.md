# Frontend — MatchCV

## Tecnologias

O frontend está em `MatchCV.Frontend` e utiliza Angular e TypeScript. A versão do Angular CLI registrada no projeto é 22.2.0; use o `package-lock.json` como referência para as versões instaladas.

## Responsabilidades

- Coletar a descrição da vaga e o currículo do usuário.
- Validar campos obrigatórios antes do envio.
- Comunicar-se com a API por HTTP.
- Apresentar estados de envio e processamento.
- Consultar e exibir o resultado da análise.
- Exibir erros de validação, autenticação, autorização e limite de uso.
- Oferecer os fluxos de autenticação implementados na interface.

O frontend não deve acessar diretamente o SQL Server ou os provedores de IA.

## Execução local

```bash
cd MatchCV.Frontend
npm ci
npm start
```

O endereço local padrão do servidor de desenvolvimento Angular é `http://localhost:4200/`. Se o script `start` não estiver definido na versão local, consulte os scripts disponíveis com `npm run` e utilize o comando de desenvolvimento configurado no `package.json`.

## Testes e build

```bash
npm test
npm run build
```

O workflow de CI executa os testes e o build do frontend. Para reproduzir o ambiente de CI, utilize a versão de Node especificada em `.github/workflows/ci.yml` e instale dependências com `npm ci`.

## Integração com a API

A API FastAPI expõe os endpoints de autenticação e análise. Os caminhos e schemas atuais devem ser conferidos no Swagger, pois prefixos globais podem ser alterados pela configuração da aplicação.

A análise é assíncrona: uma resposta HTTP 202 indica que a solicitação foi aceita. A interface deve consultar o estado posterior e diferenciar processamento, conclusão e falha.

## Acessibilidade e privacidade

- Usar rótulos claros e mensagens de erro compreensíveis.
- Permitir navegação por teclado.
- Não persistir currículo ou dados sensíveis sem necessidade.
- Não registrar tokens ou conteúdo de currículo em logs do navegador.
- Tratar os dados apresentados pela IA como resultados sujeitos à validação e sem inventar qualificações.

## Referências

- [Guia de instalação](Getting-Started.md)
- [API](API.md)
- [Integração da API](API-Integration.md)
- [Testes](Testing.md)
