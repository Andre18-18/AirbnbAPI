import { NgClass, NgFor, NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { combineLatest, switchMap, tap } from 'rxjs';
import { AvailabilityService } from '../../core/api/availability.service';
import { BookingService } from '../../core/api/booking.service';
import { PricingService } from '../../core/api/pricing.service';
import { PropertyService } from '../../core/api/property.service';
import { PriceQuote } from '../../models/booking.model';
import { PropertySummary } from '../../models/property.model';

type DateTarget = 'check_in' | 'check_out';

interface CalendarCell {
  label: number;
  date: string;
  muted: boolean;
}

@Component({
  selector: 'app-booking-flow',
  imports: [NgClass, NgFor, NgIf, ReactiveFormsModule],
  template: `
    <main class="booking-page">
      <section class="booking-hero">
        <p class="eyebrow">Direct booking</p>
        <h1>Check your Douro dates</h1>
        <p>First choose dates and guests. Personal details only come after the apartment is available.</p>
      </section>

      <section class="booking-shell">
        <form class="booking-form" [formGroup]="form" (ngSubmit)="submit()">
          <section class="form-section full">
            <div>
              <p class="step">Step 1</p>
              <h2>Dates and guests</h2>
            </div>

            <div class="field">
              <label>Apartment</label>
              <select formControlName="property_id">
                <option value="">Choose property</option>
                <option *ngFor="let property of properties" [value]="property.id">{{ property.name }}</option>
              </select>
            </div>

            <div class="date-row">
              <button class="date-pick" type="button" (click)="openCalendar('check_in')" [class.active]="activeCalendar === 'check_in'">
                <span>Check-in</span>
                <strong>{{ form.value.check_in || 'Select date' }}</strong>
              </button>
              <button class="date-pick" type="button" (click)="openCalendar('check_out')" [class.active]="activeCalendar === 'check_out'">
                <span>Check-out</span>
                <strong>{{ form.value.check_out || 'Select date' }}</strong>
              </button>
            </div>

            <section class="date-calendar" *ngIf="activeCalendar">
              <header>
                <button type="button" aria-label="Previous month" (click)="previousMonth()">&lt;</button>
                <h3>{{ monthLabel }}</h3>
                <button type="button" aria-label="Next month" (click)="nextMonth()">&gt;</button>
              </header>
              <div class="weekdays">
                <span *ngFor="let day of weekdays">{{ day }}</span>
              </div>
              <div class="month-grid">
                <button
                  type="button"
                  *ngFor="let day of calendarDays"
                  [disabled]="day.muted"
                  [ngClass]="{
                    muted: day.muted,
                    selected: isSelected(day.date),
                    range: isInRange(day.date)
                  }"
                  (click)="selectDate(day.date)">
                  {{ day.label }}
                </button>
              </div>
            </section>

            <div class="field compact">
              <label>Guests</label>
              <input type="number" min="1" formControlName="number_of_guests" />
            </div>

            <div class="actions">
              <button class="button secondary" type="button" (click)="check()" [disabled]="!canCheckDates">Check availability</button>
            </div>
          </section>

          <section class="form-section full" *ngIf="available">
            <div>
              <p class="step">Step 2</p>
              <h2>Your details</h2>
            </div>
            <div class="guest-fields">
              <div class="field">
                <label>Name</label>
                <input formControlName="guest_name" />
              </div>
              <div class="field">
                <label>Email</label>
                <input type="email" formControlName="guest_email" />
              </div>
              <div class="field">
                <label>Phone</label>
                <input formControlName="guest_phone" />
              </div>
            </div>
            <button class="button" type="submit" [disabled]="form.invalid">Proceed to checkout</button>
          </section>

          <p class="message full" [class.good]="available" *ngIf="message">{{ message }}</p>
        </form>

        <aside class="summary">
          <img src="/images/682035686.jpg" alt="Douro balcony with wine glasses" />
          <div *ngIf="!quote" class="empty">
            <h2>Your estimate</h2>
            <p>Select dates to see availability, nightly prices, cleaning fee, and total.</p>
          </div>
          <div *ngIf="quote">
            <h2>Price summary</h2>
            <div class="night" *ngFor="let night of quote.nightly_prices">
              <span>{{ night.date }}</span>
              <strong>EUR {{ night.price }}</strong>
            </div>
            <hr />
            <p>{{ quote.nights }} nights <strong>EUR {{ quote.subtotal }}</strong></p>
            <p>Cleaning <strong>EUR {{ quote.cleaning_fee }}</strong></p>
            <h3>Total EUR {{ quote.total }}</h3>
          </div>
        </aside>
      </section>
    </main>
  `,
  styles: [`
    .booking-page {
      padding: clamp(1.25rem, 4vw, 3rem);
    }
    .booking-hero {
      background:
        linear-gradient(90deg, rgba(8, 35, 60, 0.8), rgba(8, 35, 60, 0.2)),
        url('/images/682035968.jpg') center/cover;
      border-radius: 8px;
      color: white;
      margin-bottom: 1rem;
      min-height: 300px;
      padding: clamp(1.5rem, 5vw, 3rem);
    }
    .booking-hero h1,
    .form-section h2,
    .summary h2 {
      font-family: Georgia, serif;
    }
    .booking-hero h1 {
      font-size: clamp(2.5rem, 5vw, 4.5rem);
      line-height: 1;
      margin: 0.4rem 0 0.8rem;
      max-width: 720px;
    }
    .booking-hero p {
      max-width: 560px;
    }
    .eyebrow,
    .step {
      color: #f1c76f;
      font-size: 0.82rem;
      font-weight: 900;
      margin: 0;
      text-transform: uppercase;
    }
    .step {
      color: #9a6a18;
    }
    .booking-shell {
      align-items: start;
      display: grid;
      gap: 1rem;
      grid-template-columns: minmax(0, 1fr) 360px;
    }
    .booking-form,
    .summary {
      background: white;
      border: 1px solid #d8e5ee;
      border-radius: 8px;
      box-shadow: 0 14px 44px rgba(18, 58, 90, 0.1);
    }
    .booking-form {
      display: grid;
      gap: 1rem;
      padding: 1rem;
    }
    .form-section {
      border: 1px solid #edf3f7;
      border-radius: 8px;
      display: grid;
      gap: 1rem;
      padding: 1rem;
    }
    .form-section h2 {
      color: #123a5a;
      font-size: 1.75rem;
      margin: 0.15rem 0 0;
    }
    .field {
      display: grid;
      gap: 0.35rem;
    }
    .field.compact {
      max-width: 180px;
    }
    label {
      color: #39556c;
      font-weight: 800;
    }
    input,
    select {
      background: #fbfdff;
      border: 1px solid #cddce7;
      border-radius: 6px;
      min-height: 46px;
      padding: 0.7rem;
    }
    input:focus,
    select:focus {
      border-color: #0e5a8a;
      outline: 3px solid rgba(14, 90, 138, 0.15);
    }
    .date-row,
    .guest-fields,
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }
    .date-pick {
      background: #fbfdff;
      border: 1px solid #cddce7;
      border-radius: 8px;
      color: #183147;
      display: grid;
      flex: 1 1 220px;
      gap: 0.25rem;
      min-height: 76px;
      padding: 0.85rem;
      text-align: left;
    }
    .date-pick span {
      color: #6a7890;
      font-size: 0.8rem;
      font-weight: 900;
      text-transform: uppercase;
    }
    .date-pick strong {
      font-size: 1.1rem;
    }
    .date-pick.active {
      border-color: #0e5a8a;
      box-shadow: 0 0 0 3px rgba(14, 90, 138, 0.12);
    }
    .date-calendar {
      background: linear-gradient(180deg, #ffffff, #f7fbfe);
      border: 1px solid #d8e5ee;
      border-radius: 8px;
      box-shadow: 0 18px 45px rgba(18, 58, 90, 0.12);
      max-width: 520px;
      overflow: hidden;
    }
    .date-calendar header {
      align-items: center;
      background: linear-gradient(90deg, #0d314f, #0e5a8a);
      color: white;
      display: flex;
      justify-content: space-between;
      padding: 0.8rem;
    }
    .date-calendar header button {
      background: rgba(255, 255, 255, 0.14);
      border: 1px solid rgba(255, 255, 255, 0.24);
      border-radius: 999px;
      color: white;
      font-size: 1.45rem;
      height: 36px;
      line-height: 1;
      width: 36px;
    }
    .date-calendar h3 {
      font-family: Georgia, serif;
      margin: 0;
    }
    .weekdays,
    .month-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
    }
    .weekdays {
      color: #6a7890;
      font-size: 0.72rem;
      font-weight: 900;
      padding: 0.75rem 0.75rem 0;
      text-align: center;
      text-transform: uppercase;
    }
    .month-grid {
      gap: 0.35rem;
      padding: 0.75rem;
    }
    .month-grid button {
      aspect-ratio: 1;
      background: white;
      border: 1px solid transparent;
      border-radius: 999px;
      color: #183147;
      font-weight: 800;
      min-width: 0;
    }
    .month-grid button:hover:not(:disabled) {
      background: #edf6fb;
      border-color: #b9d8eb;
    }
    .month-grid button.muted {
      color: #b6c2cc;
    }
    .month-grid button.range {
      background: #edf6fb;
      border-radius: 6px;
      color: #0e5a8a;
    }
    .month-grid button.selected {
      background: #f1c76f;
      color: #3d2a08;
    }
    .message {
      background: #fff2f0;
      border-radius: 6px;
      color: #9a342d;
      font-weight: 800;
      margin: 0;
      padding: 0.75rem;
    }
    .message.good {
      background: #e8f6ee;
      color: #15643a;
    }
    .summary {
      overflow: hidden;
      position: sticky;
      top: 88px;
    }
    .summary img {
      aspect-ratio: 4 / 3;
      object-fit: cover;
      width: 100%;
    }
    .summary > div {
      padding: 1rem;
    }
    .summary h2 {
      color: #123a5a;
      margin-top: 0;
    }
    .night,
    .summary p {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
    }
    .summary h3 {
      color: #0e5a8a;
      font-size: 1.5rem;
    }
    @media (max-width: 860px) {
      .booking-shell {
        grid-template-columns: 1fr;
      }
      .summary {
        position: static;
      }
    }
  `]
})
export class BookingFlowComponent {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly propertiesApi = inject(PropertyService);
  private readonly availabilityApi = inject(AvailabilityService);
  private readonly pricingApi = inject(PricingService);
  private readonly bookingApi = inject(BookingService);

  readonly weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  activeCalendar: DateTarget | null = null;
  calendarMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1);
  properties: PropertySummary[] = [];
  quote?: PriceQuote;
  available = false;
  message = '';

  readonly form = this.fb.nonNullable.group({
    property_id: ['', Validators.required],
    check_in: ['', Validators.required],
    check_out: ['', Validators.required],
    number_of_guests: [2, [Validators.required, Validators.min(1)]],
    guest_name: ['', Validators.required],
    guest_email: ['', [Validators.required, Validators.email]],
    guest_phone: ['']
  });

  constructor() {
    this.propertiesApi.list().subscribe((properties) => {
      this.properties = properties;
      this.form.patchValue({ property_id: this.route.snapshot.queryParamMap.get('property') || properties[0]?.id || '' });
      if (!properties.length) {
        this.message = 'No active properties are available yet.';
      }
    });
  }

  get monthLabel(): string {
    return this.calendarMonth.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
  }

  get calendarDays(): CalendarCell[] {
    const year = this.calendarMonth.getFullYear();
    const month = this.calendarMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const offset = (firstDay.getDay() + 6) % 7;
    const start = new Date(year, month, 1 - offset);
    return Array.from({ length: 42 }, (_item, index) => {
      const date = new Date(start);
      date.setDate(start.getDate() + index);
      return {
        label: date.getDate(),
        date: this.toIsoDate(date),
        muted: date.getMonth() !== month
      };
    });
  }

  get canCheckDates(): boolean {
    const value = this.form.getRawValue();
    return Boolean(value.property_id && value.check_in && value.check_out);
  }

  openCalendar(target: DateTarget): void {
    this.activeCalendar = this.activeCalendar === target ? null : target;
    const selected = this.form.controls[target].value;
    if (selected) {
      const selectedDate = this.fromIsoDate(selected);
      this.calendarMonth = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1);
    }
  }

  previousMonth(): void {
    this.calendarMonth = new Date(this.calendarMonth.getFullYear(), this.calendarMonth.getMonth() - 1, 1);
  }

  nextMonth(): void {
    this.calendarMonth = new Date(this.calendarMonth.getFullYear(), this.calendarMonth.getMonth() + 1, 1);
  }

  selectDate(date: string): void {
    if (!this.activeCalendar) {
      return;
    }
    this.form.controls[this.activeCalendar].setValue(date);
    if (this.activeCalendar === 'check_in') {
      const checkOut = this.form.controls.check_out.value;
      if (checkOut && checkOut <= date) {
        this.form.controls.check_out.setValue('');
      }
      this.activeCalendar = 'check_out';
      return;
    }
    this.activeCalendar = null;
  }

  isSelected(date: string): boolean {
    return this.form.controls.check_in.value === date || this.form.controls.check_out.value === date;
  }

  isInRange(date: string): boolean {
    const checkIn = this.form.controls.check_in.value;
    const checkOut = this.form.controls.check_out.value;
    return Boolean(checkIn && checkOut && date > checkIn && date < checkOut);
  }

  check(): void {
    const value = this.form.getRawValue();
    this.message = '';
    this.quote = undefined;
    this.available = false;
    if (!value.property_id) {
      this.message = 'Choose a property first.';
      return;
    }
    if (!value.check_in || !value.check_out) {
      this.message = 'Choose check-in and check-out dates.';
      return;
    }
    if (value.check_out <= value.check_in) {
      this.message = 'Check-out must be after check-in.';
      return;
    }
    combineLatest([
      this.availabilityApi.check(value.property_id, value.check_in, value.check_out),
      this.pricingApi.quote(value.property_id, value.check_in, value.check_out, value.number_of_guests)
    ]).subscribe({
      next: ([availability, quote]) => {
        this.available = availability.available;
        this.quote = quote;
        this.message = availability.available ? 'Dates are available. You can now add your details.' : 'Those dates are unavailable.';
      },
      error: () => (this.message = 'Could not validate those dates.')
    });
  }

  submit(): void {
    this.bookingApi.create(this.form.getRawValue()).pipe(
      switchMap((booking) => this.bookingApi.checkout(booking.id)),
      tap((checkout) => (window.location.href = checkout.checkout_url))
    ).subscribe({ error: () => (this.message = 'Booking could not be created. Please try different dates.') });
  }

  private toIsoDate(date: Date): string {
    const year = date.getFullYear();
    const month = `${date.getMonth() + 1}`.padStart(2, '0');
    const day = `${date.getDate()}`.padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private fromIsoDate(value: string): Date {
    const [year, month, day] = value.split('-').map(Number);
    return new Date(year, month - 1, day);
  }
}
