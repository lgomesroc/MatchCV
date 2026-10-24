import {
  HttpClient,
  provideHttpClient,
} from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';

import { environment } from '../../../environments/environment';
import { RegisterComponent } from './register';

describe('RegisterComponent', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let router: Router;
  const registerUrl = `${environment.apiUrl}/auth/register`;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegisterComponent],
      providers: [
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router);
  });

  afterEach(() => {
    httpMock.verify();
  });

  function createComponent() {
    const fixture = TestBed.createComponent(RegisterComponent);
    fixture.detectChanges();

    return {
      fixture,
      component: fixture.componentInstance,
    };
  }

  function fillValidForm(component: RegisterComponent): void {
    component.name = 'Usuário de Teste';
    component.email = 'usuario@matchcv.com';
    component.password = 'Senha123!';
    component.confirmPassword = 'Senha123!';
  }

  it('deve criar o componente', () => {
    const { component } = createComponent();

    expect(component).toBeTruthy();
  });

  it('deve validar todos os requisitos da senha', () => {
    const { component } = createComponent();

    component.password = 'Senha123!';

    expect(component.passwordRules.every((rule) => rule.valid)).toBe(true);
    expect(component.passwordIsValid).toBe(true);
  });

  it('deve rejeitar senha sem letra maiúscula', () => {
    const { component } = createComponent();

    component.password = 'senha123!';

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve rejeitar senha sem letra minúscula', () => {
    const { component } = createComponent();

    component.password = 'SENHA123!';

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve rejeitar senha sem número', () => {
    const { component } = createComponent();

    component.password = 'SenhaTeste!';

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve rejeitar senha sem caractere especial', () => {
    const { component } = createComponent();

    component.password = 'Senha1234';

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve rejeitar senha com menos de oito caracteres', () => {
    const { component } = createComponent();

    component.password = 'Ab1!';

    expect(component.passwordIsValid).toBe(false);
  });

  it('deve verificar se as senhas coincidem', () => {
    const { component } = createComponent();

    component.password = 'Senha123!';
    component.confirmPassword = 'Senha123';

    expect(component.passwordsMatch).toBe(false);

    component.confirmPassword = 'Senha123!';

    expect(component.passwordsMatch).toBe(true);
  });

  it('deve rejeitar nome com menos de dois caracteres', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.name = 'A';

    expect(component.formIsValid).toBe(false);
  });

  it('deve rejeitar e-mail inválido', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.email = 'email-invalido';

    expect(component.formIsValid).toBe(false);
  });

  it('deve aceitar formulário válido', () => {
    const { component } = createComponent();

    fillValidForm(component);

    expect(component.formIsValid).toBe(true);
  });

  it('não deve enviar cadastro quando o formulário for inválido', () => {
    const { component } = createComponent();

    component.submit();

    httpMock.expectNone(registerUrl);
  });

  it('deve enviar dados normalizados e navegar para login após cadastro', () => {
    const { component } = createComponent();
    const navigateSpy = vi.spyOn(router, 'navigate');

    fillValidForm(component);
    component.name = '  Usuário de Teste  ';
    component.email = ' usuario@matchcv.com ';

    component.submit();

    const request = httpMock.expectOne(registerUrl);

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      name: 'Usuário de Teste',
      email: 'usuario@matchcv.com',
      password: 'Senha123!',
    });

    request.flush({ id: 'user-123' });

    expect(navigateSpy).toHaveBeenCalledWith(['/login'], {
      queryParams: { registered: 'true' },
    });
    expect(component.isSubmitting).toBe(false);
  });

  it('deve apresentar mensagem quando o e-mail já estiver cadastrado', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.submit();

    const request = httpMock.expectOne(registerUrl);

    request.flush(
      { detail: 'E-mail já cadastrado.' },
      { status: 409, statusText: 'Conflict' },
    );

    expect(component.errorMessage).toContain(
      'verifique se o e-mail já está cadastrado',
    );
    expect(component.isSubmitting).toBe(false);
  });

  it('deve apresentar mensagem quando a API estiver indisponível', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.submit();

    const request = httpMock.expectOne(registerUrl);

    request.flush(
      { detail: 'Falha de conexão.' },
      { status: 0, statusText: 'Unknown Error' },
    );

    expect(component.errorMessage).toContain('conectar à API');
    expect(component.isSubmitting).toBe(false);
  });

  it('não deve permitir duas submissões simultâneas', () => {
    const { component } = createComponent();

    fillValidForm(component);
    component.isSubmitting = true;

    component.submit();

    httpMock.expectNone(registerUrl);
  });
});
