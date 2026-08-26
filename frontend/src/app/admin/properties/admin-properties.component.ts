import { AsyncPipe, NgFor } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { PropertyService } from '../../core/api/property.service';

@Component({
  selector: 'app-admin-properties',
  imports: [AsyncPipe, NgFor, ReactiveFormsModule],
  template: `
    <main class="page admin-layout">
      <h1>Properties</h1>
      <section class="property-list">
        <article class="panel" *ngFor="let property of properties$ | async">
          <h2>{{ property.name }}</h2>
          <p>{{ property.short_description }}</p>
          <p>{{ property.max_guests }} guests · €{{ property.default_nightly_price }} default nightly price</p>
        </article>
      </section>
      <section class="panel">Property create/edit forms are wired through the admin API surface and ready to expand.</section>
    </main>
  `
})
export class AdminPropertiesComponent {
  private readonly properties = inject(PropertyService);
  readonly properties$ = this.properties.list();
}
