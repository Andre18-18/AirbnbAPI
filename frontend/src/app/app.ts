import { Location } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterOutlet],
  template: `
    <header class="site-shell">
      <div class="brand-row">
        <button class="back-button" type="button" (click)="goBack()" aria-label="Go back">&lt;</button>
        <a routerLink="/" class="brand">Douro's Heart Stay</a>
      </div>
      <nav>
        <a routerLink="/">Apartment</a>
        <a routerLink="/booking">Book</a>
      </nav>
    </header>
    <router-outlet />
  `,
  styles: [`
    .site-shell {
      align-items: center;
      backdrop-filter: blur(16px);
      background: rgba(255, 255, 255, 0.88);
      border-bottom: 1px solid rgba(18, 58, 90, 0.12);
      display: flex;
      justify-content: space-between;
      padding: 0.85rem clamp(1rem, 4vw, 3rem);
      position: sticky;
      top: 0;
      z-index: 20;
    }
    .brand-row {
      align-items: center;
      display: flex;
      gap: 0.75rem;
      min-width: 0;
    }
    .back-button {
      align-items: center;
      background: #edf6fb;
      border: 1px solid #d8e5ee;
      border-radius: 999px;
      color: #123a5a;
      display: inline-flex;
      font-size: 1.45rem;
      font-weight: 800;
      height: 38px;
      justify-content: center;
      line-height: 1;
      width: 38px;
    }
    .back-button:hover {
      background: #f8edd5;
    }
    .brand {
      color: #123a5a;
      font-family: Georgia, serif;
      font-size: 1.35rem;
      font-weight: 700;
      text-decoration: none;
    }
    nav {
      display: flex;
      gap: 0.35rem;
    }
    nav a {
      color: #38546a;
      border-radius: 999px;
      font-size: 0.95rem;
      font-weight: 700;
      padding: 0.55rem 0.8rem;
      text-decoration: none;
    }
    nav a:hover {
      background: #edf6fb;
      color: #0e5a8a;
    }
  `]
})
export class App {
  private readonly location = inject(Location);

  goBack(): void {
    this.location.back();
  }
}
