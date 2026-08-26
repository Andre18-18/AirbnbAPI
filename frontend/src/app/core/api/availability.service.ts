import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AvailabilityResult } from '../../models/booking.model';

@Injectable({ providedIn: 'root' })
export class AvailabilityService {
  constructor(private readonly http: HttpClient) {}

  check(propertyId: string, checkIn: string, checkOut: string): Observable<AvailabilityResult> {
    const params = new HttpParams().set('check_in', checkIn).set('check_out', checkOut);
    return this.http.get<AvailabilityResult>(`${environment.apiBaseUrl}/properties/${propertyId}/availability`, { params });
  }
}
