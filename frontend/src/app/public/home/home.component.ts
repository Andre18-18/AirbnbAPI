import { AsyncPipe, NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { map, Observable } from 'rxjs';
import { PropertyService } from '../../core/api/property.service';
import { PropertySummary } from '../../models/property.model';

@Component({
  selector: 'app-home',
  imports: [AsyncPipe, NgIf, RouterLink],
  template: `
    <main>
      <section class="hero" aria-label="Douro's Heart Stay apartment balcony"></section>

      <section class="page intro" *ngIf="property$ | async as property">
        <article>
          <p class="eyebrow dark">{{ property.city }}, {{ property.country }}</p>
          <h1>{{ property.name }}</h1>
          <p class="lead">{{ property.short_description }}</p>

          <div class="facts">
            <span>{{ property.max_guests }} guests</span>
            <span>{{ property.bedrooms }} bedrooms</span>
            <span>{{ property.bathrooms }} bathrooms</span>
            <span>From EUR {{ property.default_nightly_price }}</span>
          </div>

          <p>
            A comfortable base in the Douro wine region, close to the Wine Museum and the centre of Sao Joao da Pesqueira.
            Bright rooms, practical amenities, and a balcony make it easy to settle in after a day of viewpoints, river roads,
            and wine country.
          </p>

          <div class="actions">
            <a class="button" routerLink="/booking" [queryParams]="{ property: property.id }">Check availability</a>
            <a class="button secondary" [routerLink]="['/properties', property.slug]">View apartment</a>
          </div>
          <aside>
          <strong>Included</strong>
          <span>Wi-Fi</span>
          <span>Parking</span>
          <span>Air conditioning</span>
          <span>Balcony</span>
          <span>Equipped kitchen</span>
          </aside>
        </article>
      </section>
    </main>
  `,
  styles: [`
    .hero {
      background:
        linear-gradient(180deg, rgba(8, 35, 60, 0.04), rgba(8, 35, 60, 0.18)),
        url('/images/682035686.jpg') center/cover;
      min-height: min(68vh, 620px);
    }
    .intro {
      display: block;
    }
    article {
      max-width: 820px;
    }
    h1 {
      color: #123a5a;
      font-family: Georgia, serif;
      font-size: clamp(3rem, 7vw, 5.8rem);
      line-height: 0.98;
      margin: 0.25rem 0 1rem;
    }
    .lead {
      color: #38546a;
      font-size: 1.25rem;
      line-height: 1.55;
    }
    p {
      color: #496077;
      line-height: 1.7;
    }
    .eyebrow {
      color: #9a6a18;
      font-size: 0.82rem;
      font-weight: 800;
      letter-spacing: 0;
      text-transform: uppercase;
    }
    .facts,
    .actions,
    aside {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }
    .facts {
      margin: 1.5rem 0;
    }
    .facts span,
    aside span {
      background: #f8edd5;
      border: 1px solid #e6ce8a;
      border-radius: 999px;
      color: #5d4314;
      font-weight: 800;
      padding: 0.65rem 0.9rem;
    }
    .actions {
      margin-top: 1.5rem;
    }
    aside {
      margin-top: 2rem;
      background: white;
      border: 1px solid #d8e5ee;
      border-radius: 8px;
      box-shadow: 0 18px 55px rgba(18, 58, 90, 0.1);
      padding: 1.15rem;
    }
    aside strong {
      color: #123a5a;
      flex-basis: 100%;
      font-family: Georgia, serif;
      font-size: 1.45rem;
    }
    @media (max-width: 820px) {
      .hero {
        min-height: 48vh;
      }
      .intro {
        display: block;
      }
    }
  `]
})
export class HomeComponent {
  private readonly propertyService = inject(PropertyService);
  readonly properties$: Observable<PropertySummary[]> = this.propertyService.list();
  readonly property$: Observable<PropertySummary | undefined> = this.properties$.pipe(map((properties) => properties[0]));
}
