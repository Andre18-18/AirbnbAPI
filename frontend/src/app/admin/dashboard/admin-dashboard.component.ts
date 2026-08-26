import { AsyncPipe, NgFor } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AdminBookingService } from '../../core/api/admin-booking.service';

@Component({
  selector: 'app-admin-dashboard',
  imports: [AsyncPipe, NgFor, RouterLink],
  template: `
    <main class="page admin-layout">
      <nav class="admin-nav">
        <a routerLink="/admin/calendar">Calendar</a>
        <a routerLink="/admin/bookings">Bookings</a>
        <a routerLink="/admin/properties">Properties</a>
        <a routerLink="/admin/pricing">Pricing</a>
        <a routerLink="/admin/integrations">Integrations</a>
      </nav>
      <h1>Dashboard</h1>
      <section class="stats">
        <div class="panel"><span>Upcoming check-ins</span><strong>Review bookings</strong></div>
        <div class="panel"><span>This month</span><strong>Revenue and occupancy ready</strong></div>
        <div class="panel"><span>Calendar sync</span><strong>iCal prepared</strong></div>
      </section>
      <section class="panel">
        <h2>Recent bookings</h2>
        <p *ngFor="let booking of bookings$ | async">{{ booking.guest_name }} · {{ booking.check_in }} → {{ booking.check_out }} · {{ booking.status }}</p>
      </section>
    </main>
  `,
  styles: [`
    .admin-nav, .stats { display: flex; flex-wrap: wrap; gap: 1rem; }
    .admin-nav a { color: #1f4f69; font-weight: 800; }
    .stats .panel { flex: 1 1 220px; }
    span { color: #66737d; display: block; }
  `]
})
export class AdminDashboardComponent {
  private readonly bookings = inject(AdminBookingService);
  readonly bookings$ = this.bookings.list();
}
