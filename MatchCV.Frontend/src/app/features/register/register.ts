import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class RegisterComponent {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  name = '';
  email = '';
  password = '';
  confirmPassword = '';

  errorMessage = '';
  isSubmitting = false;

  get passwordRules(): {
    label: string;
    valid: boolean;
  }[] {
    return [
      { label: 'Pelo menos 8 caracteres', valid: this.password.length >= 8 },
      { label: 'Uma letra maiúscula', valid: /[A-Z]/.test(this.password) },
      { label: 'Uma letra minúscula', valid: /[a-z]/.test(this.password) },
      { label: 'Um número', valid: /\d/.test(this.password) },
      {
        label: 'Um caractere especial',
        valid: /[^A-Za-z0-9]/.test(this.password),
      },
    ];
  }

  get passwordIsValid(): boolean {
    return this.passwordRules.every((rule) => rule.valid);
  }

  get passwordsMatch(): boolean {
    return (
      this.password.length > 0 &&
      this.password === this.confirmPassword
    );
  }

  get formIsValid(): boolean {
    return (
      this.name.trim().length >= 2 &&
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email.trim()) &&
      this.passwordIsValid &&
      this.passwordsMatch
    );
  }

  submit(): void {
    this.errorMessage = '';

    if (!this.formIsValid || this.isSubmitting) {
      return;
    }

    this.isSubmitting = true;

    this.http.post(
      'http://localhost:8000/api/v1/auth/register',
      {
        name: this.name.trim(),
        email: this.email.trim(),
        password: this.password,
      },
    ).subscribe({
      next: () => {
        this.isSubmitting = false;

        void this.router.navigate(['/login'], {
          queryParams: { registered: 'true' },
        });
      },
      error: (error: unknown) => {
        this.isSubmitting = false;

        const httpError = error as HttpErrorResponse;

        if (httpError.status === 400 || httpError.status === 409) {
          this.errorMessage =
            'Não foi possível criar a conta. Confira os dados e verifique se o e-mail já está cadastrado.';
        } else if (httpError.status === 0) {
          this.errorMessage =
            'Não foi possível conectar à API. Verifique se o backend está em execução.';
        } else {
          this.errorMessage =
            'O cadastro não foi concluído. Tente novamente.';
        }
      },
    });
  }
}
