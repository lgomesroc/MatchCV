
import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import {
  ActivatedRoute,
  convertToParamMap,
  provideRouter,
  Router,
} from '@angular/router';
import { of, throwError } from 'rxjs';

import { LoginComponent } from './login';
import { AuthService } from '../../core/services/auth.service';

describe('LoginComponent', () => {
  let authService: {
    login: ReturnType<typeof vi.fn>;
  };
  let router: Router;
  let registeredQueryParam: string | null;

  beforeEach(async () => {
    authService = {
      login: vi.fn(),
    };

    registeredQueryParam = null;

    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: authService,
        },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              get queryParamMap() {
                return convertToParamMap(
                  registeredQueryParam === null
                    ? {}
                    : { registered: registeredQueryParam },
                );
              },
            },
          },
        },
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
  });

  function createComponent() {
    const fixture = TestBed.createComponent(LoginComponent);
    fixture.detectChanges();

    return {
      fixture,
      component: fixture.componentInstance,
    };
  }

  it('deve criar o componente', () => {
    const { component } = createComponent();

    expect(component).toBeTruthy();
  });

  it('deve rejeitar envio quando e-mail ou senha estiverem vazios', () => {
    const { component } = createComponent();

    component.email = ' ';
    component.password = '';

    component.submit();

    expect(component.errorMessage).toBe(
      'Informe seu e-mail e sua senha.',
    );
    expect(authService.login).not.toHaveBeenCalled();
  });

  it('deve remover espaços externos do e-mail', () => {
    const { component } = createComponent();

    authService.login.mockReturnValue(of({}));

    component.email = ' usuario@matchcv.com ';
    component.password = 'Senha123!';

    component.submit();

    expect(authService.login).toHaveBeenCalledWith({
      email: 'usuario@matchcv.com',
      password: 'Senha123!',
    });
  });

  it('deve navegar para análise após login bem-sucedido', () => {
    const { component } = createComponent();
    const navigateSpy = vi.spyOn(router, 'navigate');

    authService.login.mockReturnValue(of({}));

    component.email = 'usuario@matchcv.com';
    component.password = 'Senha123!';

    component.submit();

    expect(navigateSpy).toHaveBeenCalledWith(['/analysis']);
    expect(component.isSubmitting).toBe(false);
    expect(component.errorMessage).toBe('');
  });

  it('deve informar credenciais inválidas para HTTP 401', () => {
    const { component } = createComponent();

    authService.login.mockReturnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 401,
            statusText: 'Unauthorized',
          }),
      ),
    );

    component.email = 'usuario@matchcv.com';
    component.password = 'SenhaErrada123!';

    component.submit();

    expect(component.errorMessage).toContain('inválidos');
    expect(component.isSubmitting).toBe(false);
  });

  it('deve informar falha de conexão quando o status for zero', () => {
    const { component } = createComponent();

    authService.login.mockReturnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 0,
            statusText: 'Unknown Error',
          }),
      ),
    );

    component.email = 'usuario@matchcv.com';
    component.password = 'Senha123!';

    component.submit();

    expect(component.errorMessage).toContain('conectar à API');
    expect(component.isSubmitting).toBe(false);
  });

  it('deve apresentar mensagem genérica para outros erros', () => {
    const { component } = createComponent();

    authService.login.mockReturnValue(
      throwError(() => new Error('Erro inesperado')),
    );

    component.email = 'usuario@matchcv.com';
    component.password = 'Senha123!';

    component.submit();

    expect(component.errorMessage).toContain(
      'Não foi possível realizar o login',
    );
    expect(component.isSubmitting).toBe(false);
  });

  it('não deve enviar nova requisição enquanto estiver processando', () => {
    const { component } = createComponent();

    component.email = 'usuario@matchcv.com';
    component.password = 'Senha123!';
    component.isSubmitting = true;

    component.submit();

    expect(authService.login).not.toHaveBeenCalled();
  });

  it('deve indicar que o cadastro foi concluído quando registered=true', () => {
    registeredQueryParam = 'true';

    const { component } = createComponent();

    expect(component.registeredMessage).toBe(true);
  });

  it('não deve indicar cadastro concluído quando o parâmetro estiver ausente', () => {
    const { component } = createComponent();

    expect(component.registeredMessage).toBe(false);
  });
});
