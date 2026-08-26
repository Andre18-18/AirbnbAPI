import { AsyncPipe, NgFor } from '@angular/common';
import { Component, inject } from '@angular/core';
import { CalendarService } from '../../core/api/calendar.service';

@Component({
  selector: 'app-admin-integrations',
  imports: [AsyncPipe, NgFor],
  template: `
    <main class="page admin-layout">
      <h1>Calendar integrations</h1>
      <section class="panel" *ngFor="let source of sources$ | async">
        <h2>{{ source.provider }}</h2>
        <p>{{ source.import_url }}</p>
        <p>Last sync: {{ source.last_sync_at || 'Never' }} · {{ source.last_sync_status || 'Pending' }}</p>
        <p>Export URL: {{ calendar.exportUrl(source.property_id) }}</p>
        <button class="button" (click)="sync(source.id)">Sync now</button>
      </section>
    </main>
  `
})
export class AdminIntegrationsComponent {
  readonly calendar = inject(CalendarService);
  readonly sources$ = this.calendar.sources();

  sync(sourceId: string): void {
    this.calendar.sync(sourceId).subscribe(() => location.reload());
  }
}
