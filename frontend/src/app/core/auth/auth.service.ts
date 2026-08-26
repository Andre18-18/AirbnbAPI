import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { catchError, map, of, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

interface AuthStatusResponse {
  authenticated: boolean;
  user: { id: string; email: string; active: boolean } | null;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly authenticated = signal(false);
  readonly userEmail = signal<string | null>(null);

  constructor(private readonly http: HttpClient) {}

  login(email: string, password: string) {
    return this.http.post<AuthStatusResponse>(`${environment.apiBaseUrl}/admin/auth/login`, { email, password }, { withCredentials: true }).pipe(
      tap((response) => this.setState(response))
    );
  }

  refresh() {
    return this.http.post<AuthStatusResponse>(`${environment.apiBaseUrl}/admin/auth/refresh`, {}, { withCredentials: true }).pipe(
      tap((response) => this.setState(response))
    );
  }

  loadSession() {
    return this.http.get<AuthStatusResponse>(`${environment.apiBaseUrl}/admin/auth/me`, { withCredentials: true }).pipe(
      tap((response) => this.setState(response)),
      map((response) => response.authenticated),
      catchError(() => {
        this.clearState();
        return of(false);
      })
    );
  }

  logout() {
    return this.http.post<AuthStatusResponse>(`${environment.apiBaseUrl}/admin/auth/logout`, {}, { withCredentials: true }).pipe(
      tap(() => this.clearState())
    );
  }

  private setState(response: AuthStatusResponse): void {
    this.authenticated.set(response.authenticated);
    this.userEmail.set(response.user?.email || null);
  }

  private clearState(): void {
    this.authenticated.set(false);
    this.userEmail.set(null);
  }
}
