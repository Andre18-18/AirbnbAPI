import { AsyncPipe, NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { filter, map, switchMap } from 'rxjs';
import { BookingService } from '../../core/api/booking.service';

@Component({
  selector: 'app-booking-success',
  imports: [AsyncPipe, NgIf],
  template: `
    <main class="page">
      <section class="panel" *ngIf="booking$ | async as booking">
        <h1>Booking received</h1>
        <p>Status: <strong>{{ booking.status }}</strong></p>
        <p>Payment: <strong>{{ booking.payment_status }}</strong></p>
        <p>We verify payment through the backend webhook, not from this success page.</p>
      </section>
    </main>
  `
})
export class BookingSuccessComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly bookingApi = inject(BookingService);
  readonly booking$ = this.route.queryParamMap.pipe(
    map((params) => params.get('booking_id')),
    filter((id): id is string => !!id),
    switchMap((id) => this.bookingApi.status(id))
  );

}
