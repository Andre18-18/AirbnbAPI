import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-admin-login',
  imports: [ReactiveFormsModule],
  template: `
    <main class="page admin-layout login">
      <form class="panel" [formGroup]="form" (ngSubmit)="submit()">
        <h1>Admin login</h1>
        <label>Email<input type="email" formControlName="email" /></label>
        <label>Password<input type="password" formControlName="password" /></label>
        <button class="button" type="submit" [disabled]="form.invalid">Login</button>
        <p>{{ message }}</p>
      </form>
    </main>
  `,
  styles: [`
    .login { display: grid; place-items: center; }
    form { display: grid; gap: 1rem; max-width: 420px; width: 100%; }
    label { display: grid; gap: 0.35rem; font-weight: 700; }
    input { border: 1px solid #ccd2d8; border-radius: 6px; min-height: 44px; padding: 0.65rem; }
  `]
})
export class AdminLoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  message = '';
  readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required]
  });
  submit(): void {
    const value = this.form.getRawValue();
    this.auth.login(value.email, value.password).subscribe({
      next: () => this.router.navigateByUrl('/admin'),
      error: () => (this.message = 'Invalid credentials')
    });
  }
}
