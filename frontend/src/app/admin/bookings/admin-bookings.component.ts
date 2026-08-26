import { AsyncPipe, NgFor } from '@angular/common';
import { Component, inject } from '@angular/core';
import { AdminBookingService } from '../../core/api/admin-booking.service';

@Component({
  selector: 'app-admin-bookings',
  imports: [AsyncPipe, NgFor],
  template: `
    <main class="page admin-layout">
      <h1>Bookings</h1>
      <section class="panel filters">
        <input placeholder="Property" /><input placeholder="Source" /><input placeholder="Status" /><input type="date" />
      </section>
      <table class="panel">
        <thead><tr><th>Guest</th><th>Dates</th><th>Guests</th><th>Price</th><th>Status</th><th>Payment</th></tr></thead>
        <tbody>
          <tr *ngFor="let booking of bookings$ | async">
            <td>{{ booking.guest_name }}</td><td>{{ booking.check_in }} → {{ booking.check_out }}</td><td>{{ booking.number_of_guests }}</td><td>€{{ booking.total_price }}</td><td>{{ booking.status }}</td><td>{{ booking.payment_status }}</td>
          </tr>
        </tbody>
      </table>
    </main>
  `,
  styles: [`
    table { border-collapse: collapse; width: 100%; }
    th, td { border-bottom: 1px solid #dce1e5; padding: 0.75rem; text-align: left; }
    .filters { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1rem; }
    input { border: 1px solid #ccd2d8; border-radius: 6px; min-height: 40px; padding: 0.5rem; }
  `]
})
export class AdminBookingsComponent {
  private readonly bookings = inject(AdminBookingService);
  readonly bookings$ = this.bookings.list();
}
