# Expense Tracker

A fully functional expense tracker application built with Django backend and React frontend.

## Project Overview

- **Backend**: Django REST API
- **Frontend**: React with Tailwind CSS
- **Database**: SQLite (local) or PostgreSQL via Supabase (cloud)
- **Authentication**: Django sessions with CSRF protection (local) or AWS Cognito (cloud)
- **File Storage**: Mock URLs (local) or AWS S3 (cloud)

## Demo

[![Expense Tracker Demo](https://img.youtube.com/vi/lm1Z1apoY2s/hqdefault.jpg)](https://youtu.be/lm1Z1apoY2s)

## Running the Application

This project supports **two deployment modes**:

### Local Development (Recommended for Testing/Demo)

Run the app locally without any cloud resources:

**Terminal 1 - Backend:**
```bash
cd expense-tracker-backend/expense_tracker
pip install -r ../requirements.txt
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd expense-tracker-frontend
npm install
npm start
```

**Access the app:**
- Frontend: http://localhost:3000
- Admin panel: http://localhost:8000/admin (username: `admin`, password: `admin`)
- Any email/password combination works for login

**Features available locally:**
- Full authentication flow (mocked)
- Create, read expenses with SQLite
- Upload receipts (returns mock URLs)
- Dark mode toggle
- Fully responsive UI

---

### Cloud Deployment (Archived)

Cloud deployment files are archived in the [archive/](./archive/) folder (Dockerfile, entrypoint.sh, cloud scripts).

To deploy to production using GCP Cloud Run with AWS services:

**Services:**
- **Frontend**: Firebase Hosting
- **Backend**: GCP Cloud Run
- **Database**: Cloud SQL (PostgreSQL)
- **Authentication**: AWS Cognito
- **File Storage**: AWS S3

**Note:** Cloud deployment is not currently active. All development focuses on local mode with SQLite.

---

## Project Structure

```
ExpenseTrackerExtended/
├── expense-tracker-backend/     # Django API
│   ├── expense_tracker/         # Django project
│   │   ├── auth_app/           # Authentication & expenses API (shared)
│   │   ├── local_app/          # Local implementations
│   │   ├── cloud_app/          # Cloud implementations
│   │   └── settings/           # Django configuration (base, local, cloud)
│   └── requirements.txt         # Python dependencies
├── expense-tracker-frontend/    # React app
│   ├── src/                    # React components
│   ├── package.json            # Node dependencies
│   └── public/                 # Static files
├── sample-receipts/            # Receipt generator for testing
├── archive/                    # Cloud-specific files (Dockerfile, scripts, etc.)
└── README.md                   # This file
```

## Features

- Add and view expenses by category
- Filter and sort expenses by date and amount
- Dashboard with expense summary
- Upload receipt attachments
- Dark mode / Light mode toggle
- Responsive design (mobile, tablet, desktop)
- Secure authentication
- User profiles and settings

## Documentation

Refer docs available in the [docs/](./docs/) folder

## Sample Receipts

Generate random text-based receipts for testing in [sample-receipts/](./sample-receipts/)

Run the generator to create a random receipt:
```bash
cd sample-receipts
python3 receipt-generator.py
```

Copy the output and paste it in the app's receipt upload field.

## License

MIT License - see LICENSE file for details
