# Local Development Mode

## Workflow Diagram

```
┌─────────────────────────────────────┐
│     Developer's Machine             │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  npm start                   │  │
│  │  React App (Port 3000)       │  │
│  └──────┬───────────────────────┘  │
│         │                           │
│         │ HTTP Requests             │
│         ↓                           │
│  ┌──────────────────────────────┐  │
│  │  python manage.py runserver  │  │
│  │  Django (Port 8000)          │  │
│  │  - local_auth.py (mock JWT)  │  │
│  │  - Database operations       │  │
│  └──────┬───────────────────────┘  │
│         │                           │
│         ↓                           │
│  ┌──────────────────────────────┐  │
│  │  SQLite Database             │  │
│  │  (db.sqlite3)                │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

## Setup

### Backend

```bash
cd expense-tracker-backend/expense_tracker
pip install -r ../requirements.txt
cp ../.env.local ../.env
python manage.py migrate
python manage.py createsuperuser --username admin
python manage.py runserver
```

**URLs:**
- API: http://localhost:8000
- Admin: http://localhost:8000/admin (username: `admin`, password: `admin`)

### Frontend

```bash
cd expense-tracker-frontend
npm install
cp .env.local .env
npm start
```

**URL:** http://localhost:3000

## Authentication (Local Mode)

```
User enters email/password
    ↓
Backend accepts any credentials
    ↓
Generate mock JWT token (base64)
    ↓
Set HttpOnly cookie
    ↓
User authenticated
```

Any email/password combination works for testing.

## Database

Located at: `expense-tracker-backend/expense_tracker/db.sqlite3`

To reset:
```bash
rm db.sqlite3
python manage.py migrate
```

## Testing

1. Login with any email/password
2. Add expenses from the UI
3. View in dashboard
4. Check admin panel to see database records
