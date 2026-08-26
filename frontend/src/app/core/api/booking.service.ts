import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Booking, BookingCreate } from '../../models/booking.model';

@Injectable({ providedIn: 'root' })
export class BookingService {
  constructor(private readonly http: HttpClient) {}

  create(payload: BookingCreate): Observable<Booking> {
    return this.http.post<Booking>(`${environment.apiBaseUrl}/bookings`, payload);
  }

  checkout(bookingId: string): Observable<{ checkout_url: string; booking_id: string }> {
    return this.http.post<{ checkout_url: string; booking_id: string }>(`${environment.apiBaseUrl}/bookings/${bookingId}/checkout`, {});
  }

  status(bookingId: string): Observable<Booking> {
    return this.http.get<Booking>(`${environment.apiBaseUrl}/bookings/${bookingId}/status`);
  }
}
