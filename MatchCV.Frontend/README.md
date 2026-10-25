# MatchCV Frontend

Frontend do MatchCV desenvolvido com Angular e TypeScript. A versão do Angular CLI indicada pelo projeto é 22.2.0; as versões instaladas devem ser conferidas no `package.json` e no `package-lock.json`.

## Pré-requisitos

- Node.js compatível com `.github/workflows/ci.yml`.
- npm compatível com a configuração do CI.

## Instalar dependências

Na raiz do repositório:

```bash
cd MatchCV.Frontend
npm ci
```

## Desenvolvimento local

```bash
npm start
```

O endereço local padrão do servidor de desenvolvimento Angular é `http://localhost:4200/`. Se o script `start` não estiver disponível, execute `npm run` e use o script de desenvolvimento listado no `package.json`.

## Testes e build

```bash
npm test
npm run build
```

O workflow de CI executa os testes e o build do frontend. Use a versão de Node definida no workflow e instale dependências com `npm ci` para reproduzir o ambiente automatizado.

## Integração com a API

O frontend comunica-se com a API FastAPI por HTTP/HTTPS. Confira a configuração do endereço base da API no código/configuração do frontend e no ambiente em execução; não presuma que o endereço local e o de produção sejam iguais.

O envio de análise é assíncrono: HTTP 202 significa que a solicitação foi aceita. A interface deve acompanhar o estado posterior e apresentar conclusão ou falha. Erros 401 e 403 devem ser tratados sem revelar tokens ou dados internos.

## Boas práticas

- Não colocar credenciais, tokens ou chaves de IA no código do frontend.
- Não registrar currículos completos no console do navegador.
- Tratar o conteúdo enviado e os resultados de IA como dados não confiáveis.
- Manter mensagens de validação compreensíveis e navegação acessível.
- Atualizar este README quando os scripts, versões ou fluxos mudarem.

## Referências

- [README principal](../README.md)
- [Guia de instalação](../MatchCV.Docs/Getting-Started.md)
- [API](../MatchCV.Docs/API.md)
- [Integração da API](../MatchCV.Docs/API-Integration.md)
- [Testes](../MatchCV.Docs/Testing.md)
