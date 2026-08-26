import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';
import { Booking } from '../../models/booking.model';

@Injectable({ providedIn: 'root' })
export class AdminBookingService {
  constructor(private readonly http: HttpClient) {}

  list() {
    return this.http.get<Booking[]>(`${environment.apiBaseUrl}/admin/bookings`);
  }
}
