import { NgClass, NgFor, NgIf } from '@angular/common';
import { Component } from '@angular/core';

interface CalendarDay {
  number: number;
  muted?: boolean;
  events: { label: string; type: 'direct' | 'airbnb' | 'booking' | 'manual' | 'block' }[];
}

@Component({
  selector: 'app-admin-calendar',
  imports: [NgClass, NgFor, NgIf],
  template: `
    <main class="page admin-layout">
      <section class="calendar-header">
        <div>
          <p class="eyebrow">Douro's Heart Stay</p>
          <h1>Calendar</h1>
        </div>
        <div class="calendar-actions">
          <button class="button secondary">Block dates</button>
          <button class="button">Manual booking</button>
        </div>
      </section>

      <section class="legend">
        <span class="direct">DIRECT</span>
        <span class="airbnb">AIRBNB</span>
        <span class="booking">BOOKING</span>
        <span class="manual">MANUAL</span>
        <span class="block">BLOCK</span>
      </section>

      <section class="calendar-card">
        <header>
          <button aria-label="Previous month">‹</button>
          <h2>August 2026</h2>
          <button aria-label="Next month">›</button>
        </header>
        <div class="weekdays">
          <span *ngFor="let weekday of weekdays">{{ weekday }}</span>
        </div>
        <div class="calendar-grid">
          <article class="day" [ngClass]="{ muted: day.muted, today: day.number === 12 }" *ngFor="let day of days">
            <strong>{{ day.number }}</strong>
            <div class="events" *ngIf="day.events.length">
              <span *ngFor="let event of day.events" [ngClass]="event.type">{{ event.label }}</span>
            </div>
          </article>
        </div>
      </section>
    </main>
  `,
  styles: [`
    .calendar-header {
      align-items: center;
      display: flex;
      gap: 1rem;
      justify-content: space-between;
      margin-bottom: 1rem;
    }
    .calendar-header h1,
    .calendar-card h2 {
      color: #123a5a;
      font-family: Georgia, serif;
      margin: 0;
    }
    .calendar-header h1 {
      font-size: clamp(2.2rem, 4vw, 3.5rem);
    }
    .eyebrow {
      color: #9a6a18;
      font-size: 0.82rem;
      font-weight: 800;
      margin: 0 0 0.25rem;
      text-transform: uppercase;
    }
    .calendar-actions,
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 0.65rem;
    }
    .legend {
      margin-bottom: 1rem;
    }
    .legend span,
    .events span {
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 900;
      padding: 0.28rem 0.5rem;
    }
    .calendar-card {
      background: white;
      border: 1px solid #d8e5ee;
      border-radius: 8px;
      box-shadow: 0 14px 44px rgba(18, 58, 90, 0.1);
      overflow: hidden;
    }
    .calendar-card header {
      align-items: center;
      background: linear-gradient(90deg, #0d314f, #0e5a8a);
      color: white;
      display: flex;
      justify-content: space-between;
      padding: 1rem;
    }
    .calendar-card h2 {
      color: white;
      font-size: 1.6rem;
    }
    .calendar-card header button {
      background: rgba(255, 255, 255, 0.14);
      border: 1px solid rgba(255, 255, 255, 0.24);
      border-radius: 999px;
      color: white;
      font-size: 1.7rem;
      height: 42px;
      line-height: 1;
      width: 42px;
    }
    .weekdays,
    .calendar-grid {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
    }
    .weekdays {
      background: #f5f9fc;
      color: #5b7082;
      font-size: 0.78rem;
      font-weight: 900;
      text-transform: uppercase;
    }
    .weekdays span {
      padding: 0.75rem;
      text-align: center;
    }
    .day {
      border-right: 1px solid #e4edf3;
      border-top: 1px solid #e4edf3;
      min-height: 118px;
      padding: 0.7rem;
    }
    .day:nth-child(7n) {
      border-right: 0;
    }
    .day strong {
      color: #123a5a;
      display: inline-grid;
      place-items: center;
      width: 28px;
    }
    .day.today strong {
      background: #f1c76f;
      border-radius: 999px;
      color: #3d2a08;
      height: 28px;
    }
    .day.muted {
      background: #f8fafc;
      color: #9aa8b3;
    }
    .events {
      display: grid;
      gap: 0.35rem;
      margin-top: 0.55rem;
    }
    .direct { background: #e4f3ff; color: #0e5a8a; }
    .airbnb { background: #ffe7ea; color: #a9253d; }
    .booking { background: #e9edff; color: #3442a0; }
    .manual { background: #f8edd5; color: #7a5010; }
    .block { background: #edf0f2; color: #4f5e68; }
    @media (max-width: 760px) {
      .calendar-header {
        align-items: stretch;
        flex-direction: column;
      }
      .weekdays {
        display: none;
      }
      .calendar-grid {
        grid-template-columns: 1fr;
      }
      .day {
        border-right: 0;
        min-height: 88px;
      }
    }
  `]
})
export class AdminCalendarComponent {
  readonly weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  readonly days: CalendarDay[] = Array.from({ length: 35 }, (_, index) => {
    const number = index < 5 ? 27 + index : index - 4;
    return { number, muted: index < 5, events: this.eventsFor(number, index < 5) };
  });

  private eventsFor(day: number, muted: boolean): CalendarDay['events'] {
    if (muted) {
      return [];
    }
    const events: Record<number, CalendarDay['events']> = {
      8: [{ label: 'Owner prep', type: 'manual' }],
      10: [{ label: 'DIRECT', type: 'direct' }],
      11: [{ label: 'DIRECT', type: 'direct' }],
      12: [{ label: 'DIRECT', type: 'direct' }],
      18: [{ label: 'AIRBNB', type: 'airbnb' }],
      19: [{ label: 'AIRBNB', type: 'airbnb' }],
      24: [{ label: 'Maintenance', type: 'block' }],
      25: [{ label: 'Maintenance', type: 'block' }],
      29: [{ label: 'BOOKING', type: 'booking' }]
    };
    return events[day] || [];
  }
}
