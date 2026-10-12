import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import {
  ChangeDetectorRef,
  Component,
  inject,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import {
  finalize,
  TimeoutError,
  timeout,
} from 'rxjs';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class LoginComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly changeDetector = inject(ChangeDetectorRef);

  email = '';
  password = '';
  errorMessage = '';
  isSubmitting = false;

  readonly registeredMessage =
    this.route.snapshot.queryParamMap.get('registered') === 'true';

  submit(): void {
    this.errorMessage = '';

    const email = this.email.trim();

    if (!email || !this.password) {
      this.errorMessage = 'Informe seu e-mail e sua senha.';
      return;
    }

    if (this.isSubmitting) {
      return;
    }

    this.isSubmitting = true;
    this.changeDetector.detectChanges();

    this.authService
      .login({
        email,
        password: this.password,
      })
      .pipe(
        timeout({ first: 15000 }),
        finalize(() => {
          this.isSubmitting = false;
          this.changeDetector.detectChanges();
        }),
      )
      .subscribe({
        next: () => {
          void this.router.navigate(['/analysis']);
        },
        error: (error: unknown) => {
          if (error instanceof TimeoutError) {
            this.errorMessage =
              'A API demorou mais de 15 segundos para responder. Tente novamente.';
          } else if (
            error instanceof HttpErrorResponse &&
            error.status === 401
          ) {
            this.errorMessage = 'E-mail ou senha inválidos.';
          } else if (
            error instanceof HttpErrorResponse &&
            error.status === 0
          ) {
            this.errorMessage =
              'Não foi possível conectar à API. Verifique se o backend está em execução.';
          } else {
            this.errorMessage =
              'Não foi possível realizar o login. Tente novamente.';
          }

          this.changeDetector.detectChanges();
        },
      });
  }
}
