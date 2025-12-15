# Credit Point Management API

Django + Django REST Framework API to manage household tasks, members, and credit points for completed work.

## Setup
1. Create and activate the virtualenv:
   ```bash
   cd "/home/vaishnavp/Desktop/cursor test"
   python3 -m virtualenv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure database:
- For local SQLite (default): nothing to change.
- For Neon/Postgres: set `DATABASE_URL` in your environment (e.g. `export DATABASE_URL=postgres://...`) and ensure `psycopg2-binary` is installed (already in requirements).

4. Run migrations and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## API Overview
- `POST /api/tasks/` create a task (`title`, `description`, `credit_points`, `is_active`, `assigned_to`) — admin only
- `GET /api/tasks/` list tasks (admins see all; users see only their tasks)
- `PATCH /api/tasks/{id}/` user can mark their own task as `user_completed`
- `POST /api/tasks/{id}/approve/` admin approves (`status=approved`)
- `POST /api/tasks/{id}/reject/` admin rejects (`status=rejected`)
- `GET /api/users/` (admin) list users with totals; `/api/users/{id}/summary/` for stats

The Django admin UI is available at `/admin/` for the same data.

