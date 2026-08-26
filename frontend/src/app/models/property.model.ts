export interface PropertyFeature {
  id: string;
  name: string;
  icon?: string;
  category?: string;
}

export interface PropertyPhoto {
  id: string;
  url: string;
  alt_text?: string;
  sort_order: number;
  is_cover: boolean;
}

export interface RentalProperty {
  id: string;
  name: string;
  slug: string;
  short_description: string;
  description: string;
  city?: string;
  country?: string;
  max_guests: number;
  bedrooms: number;
  bathrooms: string;
  check_in_time: string;
  check_out_time: string;
  default_nightly_price: string;
  minimum_stay: number;
  cleaning_fee: string;
  photos: PropertyPhoto[];
  amenities: PropertyFeature[];
}

export interface PropertySummary {
  id: string;
  name: string;
  slug: string;
  short_description: string;
  city?: string;
  country?: string;
  max_guests: number;
  bedrooms: number;
  bathrooms: string;
  default_nightly_price: string;
  cover_photo_url?: string;
}
