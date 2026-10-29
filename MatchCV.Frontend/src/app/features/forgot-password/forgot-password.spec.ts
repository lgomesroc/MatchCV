import { of, throwError } from 'rxjs';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, provideRouter } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';
import { ForgotPasswordComponent } from './forgot-password';

describe('ForgotPasswordComponent', () => {
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    authService = jasmine.createSpyObj<AuthService>('AuthService', [
      'requestPasswordReset',
      'confirmPasswordReset',
    ]);
    authService.requestPasswordReset.and.returnValue(
      of({ message: 'Se houver uma conta elegível, enviaremos instruções.' }),
    );
    authService.confirmPasswordReset.and.returnValue(of(void 0));
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [ForgotPasswordComponent],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: router },
        {
          provide: ActivatedRoute,
          useValue: { fragment: of(null) },
        },
      ],
    }).compileComponents();
  });

  function createComponent() {
    const fixture = TestBed.createComponent(ForgotPasswordComponent);
    fixture.detectChanges();
    return { fixture, component: fixture.componentInstance };
  }

  it('deve criar o componente', () => {
    expect(createComponent().component).toBeTruthy();
  });

  it('valida e-mail no modo de solicitação', () => {
    const { component } = createComponent();
    component.email = 'email-invalido';
    expect(component.formIsValid).toBeFalse();
    component.email = ' usuario@example.com ';
    expect(component.formIsValid).toBeTrue();
  });

  it('envia pedido e mostra mensagem genérica sem revelar existência da conta', () => {
    const { component } = createComponent();
    component.email = 'usuario@example.com';
    component.submit();

    expect(authService.requestPasswordReset).toHaveBeenCalledWith('usuario@example.com');
    expect(component.message).toContain('Se houver uma conta elegível');
  });

  it('valida complexidade e confirmação da nova senha', () => {
    const { component } = createComponent();
    component.token = 'token-de-teste-com-tamanho-suficiente-123456';
    component.password = 'Senha123!';
    component.confirmPassword = 'Outra123!';
    expect(component.formIsValid).toBeFalse();
    component.confirmPassword = 'Senha123!';
    expect(component.formIsValid).toBeTrue();
  });

  it('envia token e nova senha e redireciona ao login', () => {
    const { component } = createComponent();
    component.token = 'token-de-teste-com-tamanho-suficiente-123456';
    component.password = 'Senha123!';
    component.confirmPassword = 'Senha123!';
    component.submit();

    expect(authService.confirmPasswordReset).toHaveBeenCalledWith(
      component.token,
      'Senha123!',
      'Senha123!',
    );
    expect(router.navigate).toHaveBeenCalledWith(['/login'], jasmine.any(Object));
  });

  it('mostra mensagem segura quando token é inválido, expirado ou reutilizado', () => {
    authService.confirmPasswordReset.and.returnValue(
      throwError(() => ({ status: 400 })),
    );
    const { component } = createComponent();
    component.token = 'token-de-teste-com-tamanho-suficiente-123456';
    component.password = 'Senha123!';
    component.confirmPassword = 'Senha123!';
    component.submit();

    expect(component.errorMessage).toContain('inválido, expirou ou já foi utilizado');
  });
});
