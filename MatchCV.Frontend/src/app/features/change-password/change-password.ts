import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './change-password.html',
  styleUrl: './change-password.scss',
})
export class ChangePasswordComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  currentPassword = '';
  newPassword = '';
  confirmPassword = '';
  errorMessage = '';
  successMessage = '';
  isSubmitting = false;

  submit(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.currentPassword || !this.newPassword || !this.confirmPassword) {
      this.errorMessage = 'Preencha todos os campos.';
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage = 'A confirmação não corresponde à nova senha.';
      return;
    }

    if (
      this.newPassword.length < 8 ||
      !/[A-Z]/.test(this.newPassword) ||
      !/[a-z]/.test(this.newPassword) ||
      !/[0-9]/.test(this.newPassword) ||
      !/[^A-Za-z0-9]/.test(this.newPassword)
    ) {
      this.errorMessage =
        'Use pelo menos 8 caracteres, com maiúscula, minúscula, número e caractere especial.';
      return;
    }

    this.isSubmitting = true;

    this.authService
      .changePassword(
        this.currentPassword,
        this.newPassword,
        this.confirmPassword,
      )
      .subscribe({
        next: () => {
          this.successMessage = 'Senha alterada com sucesso.';
          this.currentPassword = '';
          this.newPassword = '';
          this.confirmPassword = '';
          this.isSubmitting = false;
        },
        error: (error: unknown) => {
          this.isSubmitting = false;

          if (error instanceof HttpErrorResponse) {
            const detail = error.error?.detail;

            if (typeof detail === 'string' && detail.trim()) {
              this.errorMessage = detail;
              return;
            }

            if (error.status === 401) {
              this.errorMessage =
                'Sua sessão expirou. Entre novamente para continuar.';
              return;
            }
          }

          this.errorMessage =
            'Não foi possível alterar a senha. Tente novamente.';
        },
      });
  }

  goToAnalysis(): void {
    void this.router.navigate(['/analysis']);
  }
}
