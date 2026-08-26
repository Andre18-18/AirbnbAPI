export interface AvailabilityResult {
  property_id: string;
  check_in: string;
  check_out: string;
  available: boolean;
  reasons: string[];
}

export interface PriceQuote {
  property_id: string;
  check_in: string;
  check_out: string;
  nights: number;
  nightly_prices: { date: string; price: string }[];
  subtotal: string;
  cleaning_fee: string;
  total: string;
}

export interface BookingCreate {
  property_id: string;
  guest_name: string;
  guest_email: string;
  guest_phone?: string;
  check_in: string;
  check_out: string;
  number_of_guests: number;
  notes?: string;
}

export interface Booking {
  id: string;
  property_id: string;
  source: string;
  guest_name: string;
  guest_email: string;
  check_in: string;
  check_out: string;
  number_of_guests: number;
  total_price: string;
  status: string;
  payment_status: string;
  hold_expires_at?: string;
}
