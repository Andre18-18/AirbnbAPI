import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

export interface CalendarSource {
  id: string;
  property_id: string;
  provider: string;
  import_url: string;
  export_enabled: boolean;
  active: boolean;
  last_sync_at?: string;
  last_sync_status?: string;
}

@Injectable({ providedIn: 'root' })
export class CalendarService {
  constructor(private readonly http: HttpClient) {}

  sources() {
    return this.http.get<CalendarSource[]>(`${environment.apiBaseUrl}/admin/calendar-sources`);
  }

  sync(sourceId: string) {
    return this.http.post<CalendarSource>(`${environment.apiBaseUrl}/admin/calendar-sources/${sourceId}/sync`, {});
  }

  exportUrl(propertyId: string): string {
    return `${environment.backendBaseUrl}/calendar/${propertyId}.ics`;
  }
}
