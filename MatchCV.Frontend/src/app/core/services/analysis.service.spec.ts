
import {
  HttpClient,
  HttpErrorResponse,
  provideHttpClient,
} from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { AnalysisService } from './analysis.service';

describe('AnalysisService', () => {
  let service: AnalysisService;
  let httpMock: HttpTestingController;

  const apiUrl = 'http://localhost:8000/api/v1/analysis/resume';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        AnalysisService,
      ],
    });

    service = TestBed.inject(AnalysisService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('deve ser criado', () => {
    expect(service).toBeTruthy();
  });

  it('deve enviar a descrição da vaga e o currículo em texto', () => {
    let receivedResponse: unknown;

    service.analyze(
      'Descrição de uma vaga de desenvolvimento com mais de trinta caracteres.',
      'Currículo de teste com experiência em desenvolvimento.',
      null,
    ).subscribe((response) => {
      receivedResponse = response;
    });

    const request = httpMock.expectOne(apiUrl);

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toBeInstanceOf(FormData);
    expect(
      request.request.body.get('job_description'),
    ).toBe(
      'Descrição de uma vaga de desenvolvimento com mais de trinta caracteres.',
    );
    expect(
      request.request.body.get('resume_text'),
    ).toBe(
      'Currículo de teste com experiência em desenvolvimento.',
    );
    expect(request.request.body.get('resume')).toBeNull();

    request.flush({ status: 'completed' });

    expect(receivedResponse).toEqual({ status: 'completed' });
  });

  it('deve enviar o arquivo em vez do texto do currículo', () => {
    const file = new File(
      ['conteúdo de teste'],
      'curriculo.pdf',
      { type: 'application/pdf' },
    );

    service.analyze(
      'Descrição de uma vaga de desenvolvimento com mais de trinta caracteres.',
      '',
      file,
    ).subscribe();

    const request = httpMock.expectOne(apiUrl);
    const body = request.request.body as FormData;

    expect(body.get('job_description')).toBe(
      'Descrição de uma vaga de desenvolvimento com mais de trinta caracteres.',
    );
    expect(body.get('resume_text')).toBeNull();
    expect(body.get('resume')).toMatchObject({
      name: file.name,
      type: file.type,
      size: file.size,
    });

    request.flush({ status: 'completed' });
  });

  it('deve retornar a mensagem padrão para erros que não sejam HTTP', () => {
    expect(service.getErrorMessage(new Error('Erro inesperado'))).toBe(
      'Não foi possível realizar a análise.',
    );
  });

  it('deve priorizar a mensagem detail retornada pela API', () => {
    const error = new HttpErrorResponse({
      status: 400,
      error: { detail: 'Descrição da vaga inválida.' },
    });

    expect(service.getErrorMessage(error)).toBe(
      'Descrição da vaga inválida.',
    );
  });

  it('deve informar falha de conexão quando o status for zero', () => {
    const error = new HttpErrorResponse({
      status: 0,
      statusText: 'Unknown Error',
    });

    expect(service.getErrorMessage(error)).toContain(
      'conectar à API do MatchCV',
    );
  });

  it('deve informar quando o arquivo ultrapassar o limite permitido', () => {
    const error = new HttpErrorResponse({
      status: 413,
      statusText: 'Payload Too Large',
    });

    expect(service.getErrorMessage(error)).toContain(
      'ultrapassa o limite de tamanho permitido',
    );
  });

  it('deve informar quando a API rejeitar os dados', () => {
    const error = new HttpErrorResponse({
      status: 422,
      statusText: 'Unprocessable Entity',
    });

    expect(service.getErrorMessage(error)).toContain(
      'Os dados enviados não foram aceitos pela API',
    );
  });

  it('deve informar excesso de solicitações', () => {
    const error = new HttpErrorResponse({
      status: 429,
      statusText: 'Too Many Requests',
    });

    expect(service.getErrorMessage(error)).toContain(
      'recebendo muitas solicitações',
    );
  });

  it('deve informar erro interno do servidor', () => {
    const error = new HttpErrorResponse({
      status: 500,
      statusText: 'Internal Server Error',
    });

    expect(service.getErrorMessage(error)).toContain(
      'erro no servidor',
    );
  });

  it('deve retornar mensagem genérica para outros erros HTTP', () => {
    const error = new HttpErrorResponse({
      status: 400,
      statusText: 'Bad Request',
    });

    expect(service.getErrorMessage(error)).toContain(
      'Confira os dados enviados e tente novamente',
    );
  });
});
