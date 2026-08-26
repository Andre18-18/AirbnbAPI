# Database Structure

The application uses PostgreSQL as the source of truth. Primary keys are UUIDs for business tables. Any defined set of values is normalized into its own lookup table and referenced by integer IDs.

## Lookup tables

These tables store fixed value sets used by other records.

| Table | Values |
| --- | --- |
| booking_sources | `DIRECT`, `AIRBNB`, `BOOKING`, `MANUAL`, `OTHER` |
| booking_statuses | `PENDING`, `CONFIRMED`, `CANCELLED`, `EXPIRED` |
| payment_statuses | `NOT_REQUIRED`, `PENDING`, `PAID`, `FAILED`, `REFUNDED` |
| payment_providers | `STRIPE` |
| calendar_providers | `AIRBNB`, `BOOKING`, `VRBO`, `OTHER` |

Each lookup table has:

| Column | Type | Notes |
| --- | --- | --- |
| id | integer | Primary key |
| name | string | Unique display/code value |

## properties

Stores each rentable unit.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| name | string | Public property name |
| slug | string | Unique URL slug |
| short_description | string | Summary for listings |
| description | text | Full public description |
| address, city, country | string | Location details |
| latitude, longitude | numeric | Optional map coordinates |
| max_guests, bedrooms | integer | Capacity facts |
| bathrooms | numeric | Supports values like `1.5` |
| check_in_time, check_out_time | time | Property-local times |
| default_nightly_price | numeric(10,2) | Default nightly price |
| minimum_stay | integer | Default minimum nights |
| cleaning_fee | numeric(10,2) | Added to quotes |
| active | boolean | Public visibility |
| created_at, updated_at | timestamptz | Audit timestamps |

## bookings

Stores direct, manual, and channel-origin booking records.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| property_id | UUID | FK to `properties.id` |
| source_id | integer | FK to `booking_sources.id` |
| external_reference | string | Optional channel reference |
| guest_name, guest_email, guest_phone | string | Guest contact details |
| check_in, check_out | date | Checkout date is non-occupied |
| number_of_guests | integer | Guest count |
| nightly_subtotal, cleaning_fee, total_price | numeric(10,2) | Decimal money fields |
| status_id | integer | FK to `booking_statuses.id` |
| payment_status_id | integer | FK to `payment_statuses.id` |
| hold_expires_at | timestamptz | Temporary direct-booking hold expiry |
| notes | text | Internal/admin notes |
| created_at, updated_at | timestamptz | Audit timestamps |

Important indexes: `property_id + check_in + check_out`, `property_id + status_id`, and `hold_expires_at`.

## payments

Stores payment records without card data.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| booking_id | UUID | FK to `bookings.id` |
| provider_id | integer | FK to `payment_providers.id` |
| external_payment_id | string | Stripe payment/session identifier |
| amount | numeric(10,2) | Paid amount |
| currency | string | Example `EUR` |
| status | string | Provider payment status |
| created_at, updated_at | timestamptz | Audit timestamps |

Unique constraint: `provider_id + external_payment_id`.

## calendar_sources

External iCal import configuration per property.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| property_id | UUID | FK to `properties.id` |
| provider_id | integer | FK to `calendar_providers.id` |
| import_url | string | External ICS URL |
| export_enabled | boolean | Whether system calendar should be exported |
| active | boolean | Whether imports should run |
| last_sync_at | timestamptz | Last sync timestamp |
| last_sync_status | string | Last sync result |
| created_at, updated_at | timestamptz | Audit timestamps |

## property_features and property_feature_links

`property_features` stores reusable apartment features such as Wi-Fi, parking, balcony, and air conditioning. `property_feature_links` is the many-to-many join table.

| Table | Key Columns | Notes |
| --- | --- | --- |
| property_features | id, name, icon, category | `name` is unique |
| property_feature_links | property_id, feature_id | Composite primary key |

## property_photos

Stores image URLs only. Binary image data is not stored in PostgreSQL.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| property_id | UUID | FK to `properties.id` |
| url | string | Public image URL or app asset path |
| alt_text | string | Accessibility text |
| sort_order | integer | Gallery ordering |
| is_cover | boolean | Listing cover image |
| created_at | timestamptz | Created timestamp |

## property_prices

Stores date-specific price overrides.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| property_id | UUID | FK to `properties.id` |
| date | date | Night being overridden |
| nightly_price | numeric(10,2) | Override price |
| minimum_stay | integer | Optional override minimum |
| created_at, updated_at | timestamptz | Audit timestamps |

Unique constraint: `property_id + date`.

## property_blocks

Manual unavailable ranges for maintenance, owner stays, or admin blocks.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| property_id | UUID | FK to `properties.id` |
| start_date, end_date | date | End date is non-occupied |
| reason | string | Admin-visible reason |
| created_at | timestamptz | Created timestamp |

## external_calendar_events

Imported iCal events. These affect availability but remain separate from native bookings.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| property_id | UUID | FK to `properties.id` |
| calendar_source_id | UUID | FK to `calendar_sources.id` |
| external_uid | string | ICS UID |
| start_date, end_date | date | Occupied range from ICS |
| summary | string | Limited external event description |
| last_seen_at | timestamptz | Last import occurrence |
| created_at, updated_at | timestamptz | Audit timestamps |

Unique constraint: `calendar_source_id + external_uid`.

## admin_users

Stores admin accounts.

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| email | string | Unique login email |
| password_hash | string | Hashed password only |
| active | boolean | Login enabled/disabled |
| created_at, updated_at | timestamptz | Audit timestamps |
