import { AsyncPipe, NgFor, NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { switchMap } from 'rxjs';
import { PropertyService } from '../../core/api/property.service';

@Component({
  selector: 'app-property-page',
  imports: [AsyncPipe, NgFor, NgIf, RouterLink],
  template: `
    <main *ngIf="property$ | async as property">
      <section class="property-hero">
        <div>
          <p class="eyebrow">Apartment - {{ property.city }}</p>
          <h1>{{ property.name }}</h1>
          <p>{{ property.short_description }}</p>
        </div>
      </section>

      <section class="page gallery-section">
        <div>
          <p class="eyebrow dark">Photos</p>
          <h2>All apartment photos</h2>
        </div>
        <div class="gallery">
          <img *ngFor="let photo of property.photos" [src]="photo.url" [alt]="photo.alt_text || property.name" />
        </div>
      </section>

      <section class="page detail">
        <article>
          <div class="facts">
            <span>{{ property.max_guests }} guests</span>
            <span>{{ property.bedrooms }} bedrooms</span>
            <span>{{ property.bathrooms }} bathrooms</span>
            <span>Check-in {{ property.check_in_time }}</span>
          </div>

          <h2>In the heart of the Douro</h2>
          <p class="lead">{{ property.description }}</p>

          <div class="feature-grid">
            <section>
              <h3>For easy stays</h3>
              <p>Bright living space, kitchen, Wi-Fi, air conditioning, and parking for a practical stay in wine country.</p>
            </section>
            <section>
              <h3>For slow evenings</h3>
              <p>The balcony sets the tone: open the doors, pour a glass, and watch Sao Joao da Pesqueira settle into the evening.</p>
            </section>
          </div>

          <h2>Amenities</h2>
          <div class="amenities"><span *ngFor="let amenity of property.amenities">{{ amenity.name }}</span></div>

          <h2>Location</h2>
          <div class="map">
            <strong>Avenida Marques de Soveral 50</strong>
            <span>{{ property.city }}, {{ property.country }} - near the Wine Museum</span>
          </div>
        </article>

        <aside class="booking-panel">
          <p class="eyebrow dark">Direct booking</p>
          <h2>EUR {{ property.default_nightly_price }} <small>/ night</small></h2>
          <p>Cleaning fee EUR {{ property.cleaning_fee }} - minimum {{ property.minimum_stay }} nights</p>
          <a class="button" routerLink="/booking" [queryParams]="{ property: property.id }">Check availability</a>
        </aside>
      </section>
    </main>
  `,
  styles: [`
    .property-hero {
      align-items: end;
      background:
        linear-gradient(90deg, rgba(8, 35, 60, 0.78), rgba(8, 35, 60, 0.1)),
        url('/images/682035576.jpg') center/cover;
      color: white;
      display: grid;
      min-height: 48vh;
      padding: clamp(2rem, 7vw, 5rem);
    }
    .property-hero div {
      max-width: 820px;
    }
    h1,
    h2 {
      font-family: Georgia, serif;
      line-height: 1.05;
    }
    h1 {
      font-size: clamp(3rem, 7vw, 5.8rem);
      margin: 0 0 0.8rem;
    }
    h2 {
      color: #123a5a;
      font-size: clamp(1.8rem, 3vw, 2.8rem);
      margin: 2rem 0 0.75rem;
    }
    h3 {
      color: #123a5a;
      margin: 0 0 0.45rem;
    }
    .eyebrow {
      color: #f1c76f;
      font-size: 0.82rem;
      font-weight: 800;
      text-transform: uppercase;
    }
    .eyebrow.dark {
      color: #9a6a18;
    }
    .gallery-section h2 {
      margin-top: 0;
    }
    .gallery {
      display: grid;
      gap: 0.75rem;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .gallery img {
      aspect-ratio: 4 / 3;
      border-radius: 8px;
      object-fit: cover;
      width: 100%;
    }
    .gallery img:first-child {
      grid-column: span 2;
      grid-row: span 2;
    }
    .detail {
      align-items: start;
      display: grid;
      gap: 2rem;
      grid-template-columns: minmax(0, 1fr) 360px;
    }
    .lead {
      color: #496077;
      font-size: 1.08rem;
      max-width: 820px;
    }
    .facts,
    .amenities {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin: 0 0 1.25rem;
    }
    .facts span,
    .amenities span {
      background: #f8edd5;
      border: 1px solid #e6ce8a;
      border-radius: 999px;
      color: #5d4314;
      font-weight: 800;
      padding: 0.65rem 0.9rem;
    }
    .feature-grid {
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin-top: 1.25rem;
    }
    .feature-grid section,
    .booking-panel,
    .map {
      background: white;
      border: 1px solid #d8e5ee;
      border-radius: 8px;
      padding: 1.15rem;
    }
    .booking-panel {
      box-shadow: 0 18px 55px rgba(18, 58, 90, 0.14);
      position: sticky;
      top: 88px;
    }
    .booking-panel h2 {
      color: #0e5a8a;
      margin-top: 0;
    }
    .booking-panel small {
      color: #60768a;
      font-family: Inter, sans-serif;
      font-size: 1rem;
    }
    .map {
      background: linear-gradient(135deg, #d9edf8, #fff7e6);
      display: grid;
      gap: 0.3rem;
      min-height: 180px;
    }
    @media (max-width: 860px) {
      .detail,
      .gallery,
      .feature-grid {
        grid-template-columns: 1fr;
      }
      .gallery img:first-child {
        grid-column: auto;
        grid-row: auto;
      }
      .booking-panel {
        position: static;
      }
    }
  `]
})
export class PropertyPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly propertyService = inject(PropertyService);
  readonly property$ = this.route.paramMap.pipe(
    switchMap((params) => this.propertyService.getBySlug(params.get('slug') || ''))
  );
}
