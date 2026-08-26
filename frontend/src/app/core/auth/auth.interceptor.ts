import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

const STATE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const isApiRequest = req.url.startsWith(environment.apiBaseUrl);
  let request = isApiRequest ? req.clone({ withCredentials: true }) : req;
  const csrfToken = readCookie('XSRF-TOKEN');
  if (isApiRequest && STATE_METHODS.has(req.method) && csrfToken) {
    request = request.clone({ setHeaders: { 'X-CSRF-Token': csrfToken } });
  }
  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      const isAuthEndpoint = request.url.includes('/admin/auth/login') || request.url.includes('/admin/auth/refresh');
      if (error.status !== 401 || isAuthEndpoint || !request.url.includes('/admin/')) {
        return throwError(() => error);
      }
      return auth.refresh().pipe(
        switchMap(() => next(request)),
        catchError((refreshError) => {
          router.navigateByUrl('/admin/login');
          return throwError(() => refreshError);
        })
      );
    })
  );
};
