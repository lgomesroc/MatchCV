
import {
  HttpClient,
  HttpErrorResponse,
  provideHttpClient,
  withInterceptors,
} from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';

import { authInterceptor } from './auth.interceptor';
import { AuthService } from '../services/auth.service';

describe('authInterceptor', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let router: Router;

  let authService: {
    getToken: ReturnType<typeof vi.fn>;
    logout: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    authService = {
      getToken: vi.fn(),
      logout: vi.fn(),
    };

    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(
          withInterceptors([authInterceptor]),
        ),
        provideHttpClientTesting(),
        {
          provide: AuthService,
          useValue: authService,
        },
      ],
    });

    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('deve adicionar o token Bearer quando houver token salvo', () => {
    authService.getToken.mockReturnValue('token-de-teste');

    let receivedResponse: unknown;

    http.get('/api/teste').subscribe((response) => {
      receivedResponse = response;
    });

    const request = httpMock.expectOne('/api/teste');

    expect(request.request.headers.get('Authorization')).toBe(
      'Bearer token-de-teste',
    );

    request.flush({ ok: true });

    expect(receivedResponse).toEqual({ ok: true });
  });

  it('não deve adicionar Authorization quando não houver token', () => {
    authService.getToken.mockReturnValue(null);

    let receivedResponse: unknown;

    http.get('/api/publico').subscribe((response) => {
      receivedResponse = response;
    });

    const request = httpMock.expectOne('/api/publico');

    expect(request.request.headers.has('Authorization')).toBe(false);

    request.flush({ ok: true });

    expect(receivedResponse).toEqual({ ok: true });
  });

  it('deve limpar a sessão e redirecionar para login em resposta 401 protegida', () => {
    authService.getToken.mockReturnValue('token-expirado');

    const navigateSpy = vi.spyOn(router, 'navigate');

    let receivedError: unknown;

    http.get('/api/protegida').subscribe({
      error: (error: unknown) => {
        receivedError = error;
      },
    });

    const request = httpMock.expectOne('/api/protegida');

    request.flush(
      { detail: 'Token inválido' },
      { status: 401, statusText: 'Unauthorized' },
    );

    expect(receivedError).toBeInstanceOf(HttpErrorResponse);
    expect(authService.logout).toHaveBeenCalledTimes(1);
    expect(navigateSpy).toHaveBeenCalledWith(['/login']);
  });

  it('não deve limpar a sessão automaticamente para erro 403', () => {
    authService.getToken.mockReturnValue('token-valido');

    let receivedError: unknown;

    http.get('/api/protegida').subscribe({
      error: (error: unknown) => {
        receivedError = error;
      },
    });

    const request = httpMock.expectOne('/api/protegida');

    request.flush(
      { detail: 'Acesso negado' },
      { status: 403, statusText: 'Forbidden' },
    );

    expect(receivedError).toBeInstanceOf(HttpErrorResponse);
    expect(authService.logout).not.toHaveBeenCalled();
  });

  it('não deve limpar a sessão quando o login retornar 401', () => {
    authService.getToken.mockReturnValue('token-antigo');

    let receivedError: unknown;

    http.post('/api/v1/auth/login', {
      email: 'usuario@matchcv.com',
      password: 'senha-incorreta',
    }).subscribe({
      error: (error: unknown) => {
        receivedError = error;
      },
    });

    const request = httpMock.expectOne('/api/v1/auth/login');

    expect(request.request.headers.get('Authorization')).toBe(
      'Bearer token-antigo',
    );

    request.flush(
      { detail: 'Credenciais inválidas' },
      { status: 401, statusText: 'Unauthorized' },
    );

    expect(receivedError).toBeInstanceOf(HttpErrorResponse);
    expect(authService.logout).not.toHaveBeenCalled();
  });
});
