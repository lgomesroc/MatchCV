
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { ForgotPasswordComponent } from './forgot-password';

describe('ForgotPasswordComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ForgotPasswordComponent],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  function createComponent() {
    const fixture = TestBed.createComponent(
      ForgotPasswordComponent,
    );

    fixture.detectChanges();

    return {
      fixture,
      component: fixture.componentInstance,
    };
  }

  function fillValidForm(
    component: ForgotPasswordComponent,
  ): void {
    component.email = 'usuario@matchcv.com';
    component.password = 'Senha123!';
    component.confirmPassword = 'Senha123!';
  }

  it('deve criar o componente', () => {
    const { component } = createComponent();

    expect(component).toBeTruthy();
  });

  it('deve rejeitar e-mail inválido', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.email = 'email-invalido';

    expect(component.formIsValid).toBe(false);
  });

  it('deve aceitar e-mail com espaços externos', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.email = ' usuario@matchcv.com ';

    expect(component.formIsValid).toBe(true);
  });

  it('deve rejeitar senha com menos de oito caracteres', () => {
    const { component } = createComponent();

    component.password = 'Ab1!';
    component.confirmPassword = 'Ab1!';

    expect(component.passwordIsValid).toBe(false);
    expect(component.formIsValid).toBe(false);
  });

  it('deve exigir letra maiúscula', () => {
    const { component } = createComponent();

    component.password = 'senha123!';
    component.confirmPassword = component.password;

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve exigir letra minúscula', () => {
    const { component } = createComponent();

    component.password = 'SENHA123!';
    component.confirmPassword = component.password;

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve exigir número', () => {
    const { component } = createComponent();

    component.password = 'SenhaTeste!';
    component.confirmPassword = component.password;

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve exigir caractere especial', () => {
    const { component } = createComponent();

    component.password = 'Senha1234';
    component.confirmPassword = component.password;

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve rejeitar senhas diferentes', () => {
    const { component } = createComponent();

    component.email = 'usuario@matchcv.com';
    component.password = 'Senha123!';
    component.confirmPassword = 'Outra456!';

    expect(component.passwordsMatch).toBe(false);
    expect(component.formIsValid).toBe(false);
  });

  it('deve rejeitar confirmação vazia', () => {
    const { component } = createComponent();

    component.email = 'usuario@matchcv.com';
    component.password = 'Senha123!';
    component.confirmPassword = '';

    expect(component.passwordsMatch).toBe(false);
    expect(component.formIsValid).toBe(false);
  });

  it('deve aceitar os campos quando forem válidos', () => {
    const { component } = createComponent();

    fillValidForm(component);

    expect(component.passwordIsValid).toBe(true);
    expect(component.passwordsMatch).toBe(true);
    expect(component.formIsValid).toBe(true);
  });

  it('não deve alterar a mensagem quando o formulário for inválido', () => {
    const { component } = createComponent();

    component.email = 'email-invalido';
    component.password = 'senha';
    component.confirmPassword = 'diferente';
    component.message = '';

    component.submit();

    expect(component.message).toBe('');
  });

  it('deve informar que a recuperação ainda não está habilitada', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.submit();

    expect(component.message).toContain(
      'ainda não está habilitada',
    );
    expect(component.message).toContain(
      'verificação segura da sua identidade',
    );
  });

  it('não deve apresentar mensagem de sucesso de recuperação', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.submit();

    expect(component.message).not.toContain(
      'Senha alterada com sucesso',
    );
  });
});
