import {
  HttpErrorResponse,
  provideHttpClient,
} from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { AnalysisService, AnalysisPollingTimeoutError } from './analysis.service';
import { environment } from '../../../environments/environment';

describe('AnalysisService', () => {
  let service: AnalysisService;
  let httpMock: HttpTestingController;

  const apiUrl = `${environment.apiUrl}/analysis/resume`;

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
    httpMock.verify({ ignoreCancelled: true });
    vi.useRealTimers();
  });

  it('deve ser criado', () => {
    expect(service).toBeTruthy();
  });

  it('deve enviar a descrição da vaga e o currículo em texto', () => {
    vi.useFakeTimers();
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
    expect(request.request.body.get('job_description')).toBe(
      'Descrição de uma vaga de desenvolvimento com mais de trinta caracteres.',
    );
    expect(request.request.body.get('resume_text')).toBe(
      'Currículo de teste com experiência em desenvolvimento.',
    );
    expect(request.request.body.get('resume')).toBeNull();

    request.flush({ status: 'pending', analysis_id: 'analysis-123' });
    vi.advanceTimersByTime(0);

    const statusRequest = httpMock.expectOne(
      `${environment.apiUrl}/analysis/analysis-123`,
    );
    expect(statusRequest.request.method).toBe('GET');
    statusRequest.flush({
      status: 'completed',
      analysis_id: 'analysis-123',
      evidenced_requirements: [],
      unevidenced_requirements: [],
      gaps: [],
      resume_issues: [],
      suggestions: [],
    });

    expect(receivedResponse).toMatchObject({
      status: 'completed',
      analysis_id: 'analysis-123',
    });
  });

  it('deve enviar o arquivo em vez do texto do currículo', () => {
    vi.useFakeTimers();
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

    request.flush({ status: 'pending', analysis_id: 'analysis-456' });
    vi.advanceTimersByTime(0);
    const statusRequest = httpMock.expectOne(
      `${environment.apiUrl}/analysis/analysis-456`,
    );
    statusRequest.flush({ status: 'completed', analysis_id: 'analysis-456' });
    vi.advanceTimersByTime(0);
  });

  it('deve encerrar o polling após cinco minutos sem criar outra análise', () => {
    vi.useFakeTimers();
    let receivedError: unknown;
    let completed = false;

    service.analyze(
      'Descrição de uma vaga de desenvolvimento com mais de trinta caracteres.',
      'Currículo de teste com experiência em desenvolvimento.',
      null,
    ).subscribe({
      error: (error: unknown) => {
        receivedError = error;
      },
      complete: () => {
        completed = true;
      },
    });

    const createRequest = httpMock.expectOne(apiUrl);
    expect(createRequest.request.method).toBe('POST');
    createRequest.flush({ status: 'pending', analysis_id: 'analysis-timeout' });

    vi.advanceTimersByTime(0);
    expect(
      httpMock.expectOne(`${environment.apiUrl}/analysis/analysis-timeout`).request.method,
    ).toBe('GET');

    vi.advanceTimersByTime(AnalysisService.ANALYSIS_POLLING_TIMEOUT_MS);

    expect(receivedError).toBeInstanceOf(AnalysisPollingTimeoutError);
    expect(completed).toBe(false);
    expect(service.getErrorMessage(receivedError)).toContain(
      'Ela pode continuar sendo processada no servidor',
    );
    expect(service.getErrorMessage(receivedError)).toContain(
      'Não criamos outra análise automaticamente',
    );
    httpMock.expectNone(apiUrl);
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
