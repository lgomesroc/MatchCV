
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';
import { ForgotPasswordComponent } from './forgot-password';

describe('ForgotPasswordComponent', () => {
  let authService: {
    requestPasswordReset: ReturnType<typeof vi.fn>;
    confirmPasswordReset: ReturnType<typeof vi.fn>;
  };

  let router: Router;

  beforeEach(async () => {
    authService = {
      requestPasswordReset: vi.fn().mockReturnValue(
        of({
          message: 'Se houver uma conta elegível, enviaremos instruções.',
        }),
      ),
      confirmPasswordReset: vi.fn().mockReturnValue(of(void 0)),
    };

    await TestBed.configureTestingModule({
      imports: [ForgotPasswordComponent],
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: authService,
        },
        {
          provide: ActivatedRoute,
          useValue: {
            fragment: of(null),
          },
        },
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
  });

  function createComponent() {
    const fixture = TestBed.createComponent(ForgotPasswordComponent);
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

  it('valida e-mail no modo de solicitação', () => {
    const { component } = createComponent();

    component.email = 'email-invalido';
    expect(component.formIsValid).toBe(false);

    component.email = ' usuario@example.com ';
    expect(component.formIsValid).toBe(true);
  });

  it('envia pedido e mostra mensagem genérica sem revelar existência da conta', () => {
    const { component } = createComponent();

    component.email = 'usuario@example.com';
    component.submit();

    expect(authService.requestPasswordReset).toHaveBeenCalledWith(
      'usuario@example.com',
    );

    expect(component.message).toContain(
      'Se houver uma conta elegível',
    );
  });

  it('valida complexidade e confirmação da nova senha', () => {
    const { component } = createComponent();

    component.token = 'token-de-teste-com-tamanho-suficiente-123456';
    component.password = 'Senha123!';
    component.confirmPassword = 'Outra123!';

    expect(component.formIsValid).toBe(false);

    component.confirmPassword = 'Senha123!';

    expect(component.formIsValid).toBe(true);
  });

  it('envia token e nova senha e redireciona ao login', () => {
    const { component } = createComponent();
    const navigateSpy = vi
      .spyOn(router, 'navigate')
      .mockResolvedValue(true);

    const token = 'token-de-teste-com-tamanho-suficiente-123456';

    component.token = token;
    component.password = 'Senha123!';
    component.confirmPassword = 'Senha123!';

    component.submit();

    expect(authService.confirmPasswordReset).toHaveBeenCalledWith(
      token,
      'Senha123!',
      'Senha123!',
    );

    expect(navigateSpy).toHaveBeenCalledWith(
      ['/login'],
      expect.objectContaining({
        state: {
          passwordResetMessage:
            'Sua senha foi alterada. Você já pode entrar com a nova senha.',
        },
      }),
    );

    expect(component.token).toBe('');
  });

  it('mostra mensagem segura quando token é inválido, expirado ou reutilizado', () => {
    authService.confirmPasswordReset.mockReturnValue(
      throwError(() => ({ status: 400 })),
    );

    const { component } = createComponent();

    component.token = 'token-de-teste-com-tamanho-suficiente-123456';
    component.password = 'Senha123!';
    component.confirmPassword = 'Senha123!';

    component.submit();

    expect(component.errorMessage).toContain(
      'inválido, expirou ou já foi utilizado',
    );
  });
});
