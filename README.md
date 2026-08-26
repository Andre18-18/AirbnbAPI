# Vacation Rental Management and Booking

Production-oriented monorepo for a multi-property vacation rental website.

## Architecture

- `frontend/`: Angular 20, standalone components, Angular Router, Reactive Forms, SCSS.
- `backend/`: FastAPI, async SQLAlchemy 2.x, Pydantic, Alembic, PostgreSQL.
- `docker-compose.yml`: local PostgreSQL, backend, and frontend.

The backend keeps PostgreSQL as the source of truth. Availability, pricing, payment confirmation, and external calendar data are validated server-side. Stripe and iCal are isolated behind services so they can later be replaced or complemented by Booking.com APIs or a channel manager.

## Local Setup

1. Copy `.env.example` to `.env`.
2. Adjust development credentials and secrets.
3. Run:

```bash
docker compose up --build
```

Backend: `http://localhost:8000`
Frontend: `http://localhost:4200`
API docs: `http://localhost:8000/docs`

If Docker builds fail with a self-signed certificate error while installing packages, the local Dockerfiles relax package-manager SSL checks for PyPI/npm downloads. This is only a development convenience. On a managed network, the stronger production fix is to add your organization root CA certificate to Docker Desktop or the image trust store.

## Backend

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m app.utils.seed
uvicorn app.main:app --reload
pytest
```

Admin credentials are read from `ADMIN_EMAIL` and `ADMIN_PASSWORD` during seeding.

## Frontend

```bash
cd frontend
npm install
npm start
npm run build
```

API URLs live in `src/environments`.

## Stripe

Checkout creation is routed through `StripeService`. In development, if `STRIPE_SECRET_KEY` is empty, checkout returns a mock success URL. Real payment confirmation must come from `POST /api/webhooks/stripe`; frontend success pages are never trusted as proof of payment.

For local Stripe testing, forward events to:

```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

## iCal

Admin calendar sources store external iCal URLs per property. Imported events are stored separately from native bookings and affect availability. The app exports confirmed direct/manual bookings at:

```text
/calendar/{property_id}.ics
```

## Deployment Strategy

- Angular can deploy to Cloudflare Pages.
- FastAPI can deploy to Railway with the same environment variables.
- PostgreSQL can use Railway PostgreSQL.

Because the app uses Docker, environment variables, Alembic, and a normal PostgreSQL connection string, the backend and database can later move to a self-hosted Linux server without rewriting application code.

## Production Security

See `SECURITY.md` and `PRODUCTION_CHECKLIST.md` before deployment.

Required production variables:

```env
ENVIRONMENT=production
DATABASE_URL=
JWT_SECRET_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
FRONTEND_URL=https://www.your-domain.example
BACKEND_URL=https://api.your-domain.example
CORS_ORIGINS=https://www.your-domain.example
ADMIN_EMAIL=
ADMIN_PASSWORD=
```

Initial target architecture:

```text
Internet
|
Cloudflare
|
+-- www.<domain>  -> Angular / Cloudflare Pages
+-- api.<domain>  -> FastAPI / Railway
                     |
                     +-- PostgreSQL / Railway private networking
```

Run database migrations during backend deploy:

```bash
alembic upgrade head
python -m app.utils.seed
```

Admin auth uses HttpOnly cookies, short-lived JWT access tokens, rotating opaque refresh sessions, and CSRF validation for authenticated state-changing requests.
