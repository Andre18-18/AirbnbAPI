import { Component } from '@angular/core';

@Component({
  selector: 'app-admin-pricing',
  template: `
    <main class="page admin-layout">
      <h1>Pricing</h1>
      <section class="panel form">
        <label>Property<select><option>Douro's Heart Stay</option></select></label>
        <label>Start date<input type="date" /></label>
        <label>End date<input type="date" /></label>
        <label>Nightly price<input type="number" /></label>
        <button class="button">Save override</button>
        <button class="button secondary">Remove override</button>
      </section>
    </main>
  `,
  styles: [`.form { display: grid; gap: 1rem; max-width: 680px; } label { display: grid; gap: 0.35rem; font-weight: 700; } input, select { min-height: 42px; padding: 0.5rem; }`]
})
export class AdminPricingComponent {}
