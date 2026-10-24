import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { AuthUser, LoginRequest, LoginResponse } from '../models/auth';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/auth`;

  private readonly tokenKey = 'matchcv.access_token';
  private readonly userKey = 'matchcv.user';

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.apiUrl}/login`, credentials)
      .pipe(
        tap((response) => this.saveSession(response)),
      );
  }

  getToken(): string | null {
    return sessionStorage.getItem(this.tokenKey);
  }

  getUser(): AuthUser | null {
    const serializedUser = sessionStorage.getItem(this.userKey);

    if (!serializedUser) {
      return null;
    }

    try {
      return JSON.parse(serializedUser) as AuthUser;
    } catch {
      this.logout();
      return null;
    }
  }

  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  validateSession(): Observable<AuthUser> {
    return this.http.get<AuthUser>(`${this.apiUrl}/me`).pipe(
      tap((user) => {
        sessionStorage.setItem(this.userKey, JSON.stringify(user));
      }),
    );
  }

  changePassword(
    currentPassword: string,
    newPassword: string,
    confirmPassword: string,
  ): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.apiUrl}/change-password`, {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      })
      .pipe(
        tap((response) => this.saveSession(response)),
      );
  }

  logout(): void {
    sessionStorage.removeItem(this.tokenKey);
    sessionStorage.removeItem(this.userKey);
  }

  private saveSession(response: LoginResponse): void {
    sessionStorage.setItem(this.tokenKey, response.access_token);
    sessionStorage.setItem(this.userKey, JSON.stringify(response.user));
  }
}
