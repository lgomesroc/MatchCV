import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.scss',
})
export class ForgotPasswordComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  email = '';
  password = '';
  confirmPassword = '';
  token = '';
  message = '';
  errorMessage = '';
  isSubmitting = false;

  ngOnInit(): void {
    this.route.fragment.subscribe((fragment) => {
      const params = new URLSearchParams(fragment ?? '');
      this.token = params.get('token') ?? '';
    });
  }

  get isResetMode(): boolean {
    return this.token.length > 0;
  }

  get passwordIsValid(): boolean {
    return (
      this.password.length >= 8 &&
      /[A-Z]/.test(this.password) &&
      /[a-z]/.test(this.password) &&
      /\d/.test(this.password) &&
      /[^A-Za-z0-9]/.test(this.password)
    );
  }

  get passwordsMatch(): boolean {
    return this.password.length > 0 && this.password === this.confirmPassword;
  }

  get formIsValid(): boolean {
    if (this.isResetMode) {
      return this.passwordIsValid && this.passwordsMatch;
    }

    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email.trim());
  }

  submit(): void {
    if (!this.formIsValid || this.isSubmitting) {
      return;
    }

    this.message = '';
    this.errorMessage = '';
    this.isSubmitting = true;

    const operation = this.isResetMode
      ? this.authService.confirmPasswordReset(
          this.token,
          this.password,
          this.confirmPassword,
        )
      : this.authService.requestPasswordReset(this.email.trim());

    operation
      .pipe(finalize(() => (this.isSubmitting = false)))
      .subscribe({
        next: () => {
          if (this.isResetMode) {
            this.message = 'Sua senha foi alterada. Você já pode entrar com a nova senha.';
            this.token = '';
            this.password = '';
            this.confirmPassword = '';
            void this.router.navigate(['/login'], {
              state: { passwordResetMessage: this.message },
            });
            return;
          }

          this.message =
            'Se houver uma conta elegível para esse e-mail, você receberá instruções de recuperação.';
        },
        error: (error: HttpErrorResponse) => {
          if (this.isResetMode && (error.status === 400 || error.status === 422)) {
            this.errorMessage =
              'O link de recuperação é inválido, expirou ou já foi utilizado. Solicite um novo link.';
            return;
          }

          this.errorMessage =
            'Não foi possível concluir a solicitação agora. Tente novamente mais tarde.';
        },
      });
  }
}
