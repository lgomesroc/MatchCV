import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { AuthService } from './auth.service';
import {
  AuthUser,
  LoginRequest,
  LoginResponse,
} from '../models/auth';
import { environment } from '../../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  const apiUrl = `${environment.apiUrl}/auth`;

  const user: AuthUser = {
    id: 'user-123',
    name: 'Usuário de Teste',
    email: 'usuario@matchcv.com',
    role: 'USER',
  };

  const loginResponse: LoginResponse = {
    access_token: 'token-de-teste',
    token_type: 'bearer',
    user,
  };

  beforeEach(() => {
    sessionStorage.clear();

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        AuthService,
      ],
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    sessionStorage.clear();
  });

  it('deve ser criado', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    it('deve enviar as credenciais para a API e salvar a sessão', () => {
      const credentials: LoginRequest = {
        email: 'usuario@matchcv.com',
        password: 'Senha123!',
      };

      let receivedResponse: LoginResponse | undefined;

      service.login(credentials).subscribe((response) => {
        receivedResponse = response;
      });

      const request = httpMock.expectOne(`${apiUrl}/login`);

      expect(request.request.method).toBe('POST');
      expect(request.request.body).toEqual(credentials);

      request.flush(loginResponse);

      expect(receivedResponse).toEqual(loginResponse);
      expect(service.getToken()).toBe('token-de-teste');
      expect(service.getUser()).toEqual(user);
    });

    it('não deve salvar uma sessão quando o login falhar', () => {
      service.login({
        email: 'usuario@matchcv.com',
        password: 'senha-incorreta',
      }).subscribe({
        error: () => undefined,
      });

      const request = httpMock.expectOne(`${apiUrl}/login`);

      request.flush(
        { detail: 'Credenciais inválidas.' },
        { status: 401, statusText: 'Unauthorized' },
      );

      expect(service.getToken()).toBeNull();
      expect(service.getUser()).toBeNull();
    });
  });

  describe('getToken', () => {
    it('deve retornar null quando não houver token', () => {
      expect(service.getToken()).toBeNull();
    });

    it('deve retornar o token salvo na sessão', () => {
      sessionStorage.setItem('matchcv.access_token', 'token-salvo');

      expect(service.getToken()).toBe('token-salvo');
    });
  });

  describe('getUser', () => {
    it('deve retornar null quando não houver usuário salvo', () => {
      expect(service.getUser()).toBeNull();
    });

    it('deve retornar o usuário salvo na sessão', () => {
      sessionStorage.setItem(
        'matchcv.user',
        JSON.stringify(user),
      );

      expect(service.getUser()).toEqual(user);
    });

    it('deve limpar a sessão quando os dados do usuário forem inválidos', () => {
      sessionStorage.setItem(
        'matchcv.access_token',
        'token-invalido',
      );
      sessionStorage.setItem('matchcv.user', '{json inválido');

      expect(service.getUser()).toBeNull();
      expect(sessionStorage.getItem('matchcv.access_token')).toBeNull();
      expect(sessionStorage.getItem('matchcv.user')).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('deve retornar false quando não houver token', () => {
      expect(service.isAuthenticated()).toBe(false);
    });

    it('deve retornar true quando houver token', () => {
      sessionStorage.setItem(
        'matchcv.access_token',
        'token-de-teste',
      );

      expect(service.isAuthenticated()).toBe(true);
    });
  });

  describe('validateSession', () => {
    it('deve consultar o usuário atual e atualizar os dados da sessão', () => {
      let receivedUser: AuthUser | undefined;

      service.validateSession().subscribe((response) => {
        receivedUser = response;
      });

      const request = httpMock.expectOne(`${apiUrl}/me`);

      expect(request.request.method).toBe('GET');

      request.flush(user);

      expect(receivedUser).toEqual(user);
      expect(service.getUser()).toEqual(user);
    });

    it('deve propagar o erro quando a API rejeitar a sessão', () => {
      let receivedError: unknown;

      service.validateSession().subscribe({
        error: (error: unknown) => {
          receivedError = error;
        },
      });

      const request = httpMock.expectOne(`${apiUrl}/me`);

      request.flush(
        { detail: 'Token inválido.' },
        { status: 401, statusText: 'Unauthorized' },
      );

      expect(receivedError).toBeTruthy();
    });
  });

  describe('changePassword', () => {
    it('deve enviar os campos esperados e salvar a nova sessão', () => {
      const newResponse: LoginResponse = {
        ...loginResponse,
        access_token: 'novo-token',
      };

      let receivedResponse: LoginResponse | undefined;

      service.changePassword(
        'SenhaAntiga123!',
        'SenhaNova456!',
        'SenhaNova456!',
      ).subscribe((response) => {
        receivedResponse = response;
      });

      const request = httpMock.expectOne(
        `${apiUrl}/change-password`,
      );

      expect(request.request.method).toBe('POST');
      expect(request.request.body).toEqual({
        current_password: 'SenhaAntiga123!',
        new_password: 'SenhaNova456!',
        confirm_password: 'SenhaNova456!',
      });

      request.flush(newResponse);

      expect(receivedResponse).toEqual(newResponse);
      expect(service.getToken()).toBe('novo-token');
      expect(service.getUser()).toEqual(user);
    });

    it('deve propagar o erro quando a senha atual for rejeitada', () => {
      let receivedError: unknown;

      service.changePassword(
        'SenhaErrada123!',
        'SenhaNova456!',
        'SenhaNova456!',
      ).subscribe({
        error: (error: unknown) => {
          receivedError = error;
        },
      });

      const request = httpMock.expectOne(
        `${apiUrl}/change-password`,
      );

      request.flush(
        { detail: 'Senha atual incorreta.' },
        { status: 400, statusText: 'Bad Request' },
      );

      expect(receivedError).toBeTruthy();
    });
  });

  describe('logout', () => {
    it('deve remover o token e o usuário da sessão', () => {
      sessionStorage.setItem(
        'matchcv.access_token',
        'token-de-teste',
      );
      sessionStorage.setItem(
        'matchcv.user',
        JSON.stringify(user),
      );

      service.logout();

      expect(service.getToken()).toBeNull();
      expect(service.getUser()).toBeNull();
      expect(service.isAuthenticated()).toBe(false);
    });

    it('deve funcionar mesmo quando não existir sessão', () => {
      expect(() => service.logout()).not.toThrow();

      expect(service.getToken()).toBeNull();
      expect(service.getUser()).toBeNull();
    });
  });
});
