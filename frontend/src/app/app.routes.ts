import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';
import { AdminBookingsComponent } from './admin/bookings/admin-bookings.component';
import { AdminCalendarComponent } from './admin/calendar/admin-calendar.component';
import { AdminDashboardComponent } from './admin/dashboard/admin-dashboard.component';
import { AdminIntegrationsComponent } from './admin/integrations/admin-integrations.component';
import { AdminLoginComponent } from './admin/login/admin-login.component';
import { AdminPricingComponent } from './admin/pricing/admin-pricing.component';
import { AdminPropertiesComponent } from './admin/properties/admin-properties.component';
import { BookingFlowComponent } from './booking/booking-flow/booking-flow.component';
import { BookingSuccessComponent } from './booking/booking-success/booking-success.component';
import { HomeComponent } from './public/home/home.component';
import { PropertyPageComponent } from './public/property-page/property-page.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'properties/:slug', component: PropertyPageComponent },
  { path: 'booking', component: BookingFlowComponent },
  { path: 'booking/success', component: BookingSuccessComponent },
  { path: 'admin/login', component: AdminLoginComponent },
  { path: 'admin', component: AdminDashboardComponent, canActivate: [authGuard] },
  { path: 'admin/calendar', component: AdminCalendarComponent, canActivate: [authGuard] },
  { path: 'admin/bookings', component: AdminBookingsComponent, canActivate: [authGuard] },
  { path: 'admin/properties', component: AdminPropertiesComponent, canActivate: [authGuard] },
  { path: 'admin/pricing', component: AdminPricingComponent, canActivate: [authGuard] },
  { path: 'admin/integrations', component: AdminIntegrationsComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: '' }
];
