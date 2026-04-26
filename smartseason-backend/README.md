# SmartSeason Backend (Django + DRF + MySQL)

Production-ready REST API for the SmartSeason Field Monitoring System.

## Architecture

```
smartseason-backend/
├── manage.py
├── requirements.txt
├── .env.example
├── smartseason/            # project package
│   ├── settings/           # base / dev / prod split
│   ├── urls.py
│   ├── wsgi.py / asgi.py
└── apps/                   # one Django app per concern (SOLID)
    ├── core/               # cross-cutting: middleware, permissions
    ├── users/              # custom User, JWT auth, register/login/logout
    ├── fields/             # Field model + CRUD + assign + status service
    ├── updates/            # FieldUpdate (immutable observations)
    ├── dashboards/         # admin + agent aggregations
    └── audit/              # AuditLog + record() helper
```

Service-layer pattern: business logic (`apps/fields/services.py`,
`apps/audit/services.py`) is separated from views/serializers so it can be
unit-tested in isolation.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                       # edit DB creds + secret key

# Create the MySQL database (one time)
mysql -uroot -p -e "CREATE DATABASE smartseason CHARACTER SET utf8mb4;"

python manage.py migrate
python manage.py seed_demo                 # demo users + fields + updates
python manage.py runserver                 # http://127.0.0.1:8000
```

Swagger docs at `/api/docs/`.

## Demo credentials (after `seed_demo`)

| Role        | Email                       | Password    |
|-------------|-----------------------------|-------------|
| Admin       | admin@smartseason.test      | Admin123!   |
| Field Agent | agent1@smartseason.test     | Agent123!   |
| Field Agent | agent2@smartseason.test     | Agent123!   |

## API endpoints

| Method | Path                              | Who          |
|--------|-----------------------------------|--------------|
| POST   | `/api/auth/register/`             | public       |
| POST   | `/api/auth/login/`                | public       |
| POST   | `/api/auth/refresh/`              | public       |
| POST   | `/api/auth/logout/`               | auth         |
| GET    | `/api/users/me/`                  | auth         |
| GET    | `/api/users/agents/`              | admin        |
| GET    | `/api/fields/`                    | auth (scoped)|
| POST   | `/api/fields/`                    | admin        |
| GET/PUT/PATCH/DELETE | `/api/fields/{id}/`     | admin (mutate) |
| POST   | `/api/fields/{id}/assign/`        | admin        |
| GET    | `/api/updates/`                   | auth (scoped)|
| POST   | `/api/updates/`                   | agent        |
| GET    | `/api/dashboard/admin/`           | admin        |
| GET    | `/api/dashboard/agent/`           | agent        |

Field agents only see fields/updates assigned to them — enforced both at the
queryset level (`get_queryset`) and inside serializer `validate_field`.

## Computed Field Status

`apps/fields/services.compute_status(field)` returns one of:

- **completed** — `current_stage == harvested`
- **at_risk**   — latest update older than `AT_RISK_DAYS` (default 7), OR
                  no updates and field created more than `AT_RISK_DAYS` ago,
                  OR latest note contains a flagged keyword
                  (`pest`, `disease`, `drought`, `flood`, `blight`, `infestation`)
- **active**    — anything else

`AT_RISK_DAYS` is configurable via the env var of the same name.

## Logging

Rotating file handlers under `logs/`:

- `logs/app.log`   — every request, audit events, INFO+
- `logs/error.log` — exceptions and ERROR+

`apps.core.middleware.RequestLoggingMiddleware` logs every API call with
method / path / status / user / latency.
`apps.audit.services.record(...)` writes structured rows to the
`audit_auditlog` table for sensitive actions (login success/failure,
permission denials, field create/update/delete/assign, etc.).

## Security

- JWT (access 30 min, refresh 7 days, rotation + blacklist on rotate)
- Login + register endpoints are throttled (`10/min` and `5/min`)
- CORS restricted to `CORS_ALLOWED_ORIGINS` in prod
- Password validators enforce min length 8, no common/numeric passwords
- All write endpoints behind explicit permission classes
- Field agents cannot escalate privileges via signup (role is hard-defaulted
  to `field_agent` in `RegisterSerializer`)
- Sensitive actions audited

## Testing

```bash
python manage.py test
```

Covers: registration default role, JWT login, status logic (completed /
at_risk via stale data / at_risk via keyword / active default).

## Frontend integration

The companion React frontend expects:

```
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Login → store `access` + `refresh` → send `Authorization: Bearer <access>`
on every request → on 401, POST `refresh/` and retry.
