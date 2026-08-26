# Security

## Authentication

Admin authentication uses email/password. Passwords are normalized by lowercasing and trimming email addresses, then hashed with Argon2id through Passlib. Public reservation customers do not have accounts.

Admin sessions use:

- `admin_access_token`: short-lived JWT in an HttpOnly cookie, default 15 minutes.
- `admin_refresh_token`: opaque server-side session token in an HttpOnly cookie, default 14 days.
- `XSRF-TOKEN`: random CSRF token in a readable cookie so Angular can echo it in `X-CSRF-Token`.

Refresh tokens are stored only as SHA-256 hashes in `admin_sessions`. Refresh rotates the session and logout revokes the active refresh session. Production cookies are Secure when `ENVIRONMENT=production`.

## CSRF

State-changing admin requests require the `X-CSRF-Token` header to match the `XSRF-TOKEN` cookie and the server-side session hash. SameSite is used as a secondary defense, not the only defense.

## Authorization

Property administration is authorized through `user_properties`.

Roles:

- `OWNER`: full property administration.
- `MANAGER`: bookings, pricing, availability, calendar sources, and operational property updates.
- `STAFF`: limited read/operational access.

FastAPI dependencies authenticate the user, verify the session is active, verify property membership, then verify the minimum role. The frontend route guard is only for user experience.

## CORS And Cookies

`CORS_ORIGINS` must be an explicit comma-separated list. Do not use `*` for authenticated APIs. Production should set:

```env
ENVIRONMENT=production
FRONTEND_URL=https://www.your-domain.example
BACKEND_URL=https://api.your-domain.example
CORS_ORIGINS=https://www.your-domain.example
JWT_SECRET_KEY=<strong random value>
```

## Stripe

The frontend is never trusted as proof of payment. Payment confirmation must come through the Stripe webhook with a valid signature. Webhook handling is idempotent by unique provider/payment ID, and the webhook amount must match the server-side booking total.

## iCal

External iCal URLs are untrusted. Sync rejects localhost, private/internal/link-local/reserved destinations, disables redirects, applies a timeout, and caps response size. Only authorized property administrators can configure or sync calendar sources.

## Uploads

Image upload is not implemented. If added later, require MIME and content validation, strict size limits, generated server-side filenames, object storage, and path traversal protection.

## Backups

For production PostgreSQL, enable automated daily backups with at least 14-30 days retention. Also schedule periodic logical dumps before high-risk releases:

```bash
pg_dump "$DATABASE_URL" > backup.sql
```

Restore test procedure:

1. Create an empty staging database.
2. Restore with `psql "$STAGING_DATABASE_URL" < backup.sql`.
3. Run `alembic upgrade head`.
4. Smoke test admin login, property listing, availability, and booking status.

Do not assume provider backups are sufficient until restoration has been tested.
