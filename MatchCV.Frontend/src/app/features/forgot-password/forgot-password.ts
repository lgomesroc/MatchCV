import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.scss',
})
export class ForgotPasswordComponent {
  email = '';
  password = '';
  confirmPassword = '';
  message = '';

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
    return (
      this.password.length > 0 &&
      this.password === this.confirmPassword
    );
  }

  get formIsValid(): boolean {
    return (
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email.trim()) &&
      this.passwordIsValid &&
      this.passwordsMatch
    );
  }

  submit(): void {
    if (!this.formIsValid) {
      return;
    }

    this.message =
      'A recuperação de senha ainda não está habilitada. A troca só poderá ser concluída após configurarmos a verificação segura da sua identidade.';
  }
}
