
import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { ChangePasswordComponent } from './change-password';
import { AuthService } from '../../core/services/auth.service';

describe('ChangePasswordComponent', () => {
  let authService: {
    changePassword: ReturnType<typeof vi.fn>;
  };
  let router: Router;

  beforeEach(async () => {
    authService = {
      changePassword: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [ChangePasswordComponent],
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: authService,
        },
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
  });

  function createComponent() {
    const fixture = TestBed.createComponent(
      ChangePasswordComponent,
    );

    fixture.detectChanges();

    return {
      fixture,
      component: fixture.componentInstance,
    };
  }

  function fillValidForm(
    component: ChangePasswordComponent,
  ): void {
    component.currentPassword = 'SenhaAtual123!';
    component.newPassword = 'SenhaNova456!';
    component.confirmPassword = 'SenhaNova456!';
  }

  it('deve criar o componente', () => {
    const { component } = createComponent();

    expect(component).toBeTruthy();
  });

  it('deve rejeitar campos vazios', () => {
    const { component } = createComponent();

    component.submit();

    expect(component.errorMessage).toBe('Preencha todos os campos.');
    expect(authService.changePassword).not.toHaveBeenCalled();
  });

  it('deve rejeitar nova senha diferente da confirmação', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.confirmPassword = 'OutraSenha789!';

    component.submit();

    expect(component.errorMessage).toContain(
      'confirmação',
    );
    expect(authService.changePassword).not.toHaveBeenCalled();
  });

  it('deve exigir pelo menos oito caracteres', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.newPassword = 'Ab1!';
    component.confirmPassword = 'Ab1!';

    component.submit();

    expect(component.errorMessage).toContain('8 caracteres');
    expect(authService.changePassword).not.toHaveBeenCalled();
  });

  it('deve exigir letra maiúscula', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.newPassword = 'senha123!';
    component.confirmPassword = 'senha123!';

    component.submit();

    expect(component.errorMessage).toContain('maiúscula');
    expect(authService.changePassword).not.toHaveBeenCalled();
  });

  it('deve exigir letra minúscula', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.newPassword = 'SENHA123!';
    component.confirmPassword = 'SENHA123!';

    component.submit();

    expect(component.errorMessage).toContain('minúscula');
    expect(authService.changePassword).not.toHaveBeenCalled();
  });

  it('deve exigir número', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.newPassword = 'SenhaTeste!';
    component.confirmPassword = 'SenhaTeste!';

    component.submit();

    expect(component.errorMessage).toContain('número');
    expect(authService.changePassword).not.toHaveBeenCalled();
  });

  it('deve exigir caractere especial', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.newPassword = 'SenhaNova456';
    component.confirmPassword = 'SenhaNova456';

    component.submit();

    expect(component.errorMessage).toContain(
      'caractere especial',
    );
    expect(authService.changePassword).not.toHaveBeenCalled();
  });

  it('deve chamar o serviço e limpar os campos após sucesso', () => {
    const { component } = createComponent();

    authService.changePassword.mockReturnValue(of({}));
    fillValidForm(component);

    component.submit();

    expect(authService.changePassword).toHaveBeenCalledWith(
      'SenhaAtual123!',
      'SenhaNova456!',
      'SenhaNova456!',
    );

    expect(component.successMessage).toBe(
      'Senha alterada com sucesso.',
    );
    expect(component.currentPassword).toBe('');
    expect(component.newPassword).toBe('');
    expect(component.confirmPassword).toBe('');
    expect(component.isSubmitting).toBe(false);
    expect(component.errorMessage).toBe('');
  });

  it('deve apresentar o detalhe devolvido pela API', () => {
    const { component } = createComponent();

    authService.changePassword.mockReturnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 400,
            error: {
              detail: 'A senha atual está incorreta.',
            },
          }),
      ),
    );

    fillValidForm(component);
    component.submit();

    expect(component.errorMessage).toBe(
      'A senha atual está incorreta.',
    );
    expect(component.isSubmitting).toBe(false);
  });

  it('deve apresentar mensagem de sessão expirada quando HTTP 401 não tiver detalhe', () => {
    const { component } = createComponent();

    authService.changePassword.mockReturnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 401,
            statusText: 'Unauthorized',
          }),
      ),
    );

    fillValidForm(component);
    component.submit();

    expect(component.errorMessage).toContain(
      'Sua sessão expirou',
    );
    expect(component.isSubmitting).toBe(false);
  });

  it('deve apresentar mensagem genérica para erro sem detalhe', () => {
    const { component } = createComponent();

    authService.changePassword.mockReturnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 500,
            statusText: 'Internal Server Error',
          }),
      ),
    );

    fillValidForm(component);
    component.submit();

    expect(component.errorMessage).toContain(
      'Não foi possível alterar a senha',
    );
    expect(component.isSubmitting).toBe(false);
  });

  it('deve navegar para análise ao solicitar retorno', () => {
    const { component } = createComponent();
    const navigateSpy = vi.spyOn(router, 'navigate');

    component.goToAnalysis();

    expect(navigateSpy).toHaveBeenCalledWith(['/analysis']);
  });
});
