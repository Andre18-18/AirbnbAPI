import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PriceQuote } from '../../models/booking.model';

@Injectable({ providedIn: 'root' })
export class PricingService {
  constructor(private readonly http: HttpClient) {}

  quote(propertyId: string, checkIn: string, checkOut: string, guests: number): Observable<PriceQuote> {
    const params = new HttpParams().set('check_in', checkIn).set('check_out', checkOut).set('guests', guests);
    return this.http.get<PriceQuote>(`${environment.apiBaseUrl}/properties/${propertyId}/pricing`, { params });
  }
}
