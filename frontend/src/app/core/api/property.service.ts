import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PropertySummary, RentalProperty } from '../../models/property.model';

@Injectable({ providedIn: 'root' })
export class PropertyService {
  private readonly baseUrl = environment.apiBaseUrl;

  constructor(private readonly http: HttpClient) {}

  list(): Observable<PropertySummary[]> {
    return this.http.get<PropertySummary[]>(`${this.baseUrl}/properties`);
  }

  getBySlug(slug: string): Observable<RentalProperty> {
    return this.http.get<RentalProperty>(`${this.baseUrl}/properties/${slug}`);
  }
}
