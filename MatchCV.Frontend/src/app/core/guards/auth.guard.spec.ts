
import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  Router,
  RouterStateSnapshot,
  provideRouter,
} from '@angular/router';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { of, throwError } from 'rxjs';

import { authGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';
import { AuthUser } from '../models/auth';

describe('authGuard', () => {
  let authService: {
    getToken: ReturnType<typeof vi.fn>;
    validateSession: ReturnType<typeof vi.fn>;
    logout: ReturnType<typeof vi.fn>;
  };
  let router: Router;

  const user: AuthUser = {
    id: 'user-123',
    name: 'Usuário de Teste',
    email: 'usuario@matchcv.com',
    role: 'USER',
  };

  beforeEach(() => {
    authService = {
      getToken: vi.fn(),
      validateSession: vi.fn(),
      logout: vi.fn(),
    };

    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: AuthService,
          useValue: authService,
        },
      ],
    });

    router = TestBed.inject(Router);
  });

  function executeGuard() {
    return TestBed.runInInjectionContext(() =>
      authGuard(
        {} as ActivatedRouteSnapshot,
        {} as RouterStateSnapshot,
      ),
    );
  }

  it('deve redirecionar para login quando não houver token', () => {
    authService.getToken.mockReturnValue(null);

    const result = executeGuard();

    expect(result).toEqual(router.parseUrl('/login'));
    expect(authService.validateSession).not.toHaveBeenCalled();
  });

  it('deve permitir acesso quando a sessão for válida', () => {
    authService.getToken.mockReturnValue('token-valido');
    authService.validateSession.mockReturnValue(of(user));

    const result = executeGuard();

    let guardResult: unknown;

    if (result && typeof result !== 'boolean' && 'subscribe' in result) {
      result.subscribe((value) => {
        guardResult = value;
      });
    } else {
      guardResult = result;
    }

    expect(guardResult).toBe(true);
    expect(authService.validateSession).toHaveBeenCalledTimes(1);
    expect(authService.logout).not.toHaveBeenCalled();
  });

  it('deve limpar a sessão e redirecionar para login quando a validação falhar', () => {
    authService.getToken.mockReturnValue('token-expirado');
    authService.validateSession.mockReturnValue(
      throwError(() => new Error('Sessão inválida')),
    );

    const result = executeGuard();

    let guardResult: unknown;

    if (result && typeof result !== 'boolean' && 'subscribe' in result) {
      result.subscribe((value) => {
        guardResult = value;
      });
    } else {
      guardResult = result;
    }

    expect(authService.logout).toHaveBeenCalledTimes(1);
    expect(guardResult).toEqual(router.parseUrl('/login'));
  });
});
