# Expense Tracker

A fully functional expense tracker application built with Django backend and React frontend.

## Project Overview

- **Backend**: Django REST API
- **Frontend**: React with Tailwind CSS
- **Database**: SQLite (local) or PostgreSQL via Supabase (cloud)
- **Authentication**: Mock auth (local) or AWS Cognito (cloud)
- **File Storage**: Mock uploads (local) or AWS S3 (cloud)

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

### Cloud Deployment (Production)

Deploy to production using AWS, GCP, and Firebase:

**Services:**
- **Frontend**: Firebase Hosting
- **Backend**: GCP Cloud Run
- **Database**: Supabase PostgreSQL
- **Authentication**: AWS Cognito
- **File Storage**: AWS S3

**Deployment steps:**
1. Configure AWS credentials (Cognito, S3, DynamoDB)
2. Set up Supabase PostgreSQL database
3. Push code to `master` or `main` branch
4. GitHub Actions CI/CD will deploy automatically to Cloud Run
5. Set environment variables in Cloud Run settings

---

## Project Structure

```
ExpenseTrackerExtended/
├── expense-tracker-backend/     # Django API
│   ├── expense_tracker/         # Django project
│   │   ├── auth_app/           # Authentication & expenses API
│   │   └── settings.py          # Django configuration
│   ├── requirements.txt         # Python dependencies
│   └── scripts/                # Setup and utility scripts
├── expense-tracker-frontend/    # React app
│   ├── src/                    # React components
│   ├── package.json            # Node dependencies
│   └── public/                 # Static files
├── sample-receipts/            # Sample receipt files for testing
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

Sample receipts to upload available in [sample-receipts/](./sample-receipts/)

You can also run the `receipt-generator.py` script to create additional sample receipt files for testing.

## License

MIT License - see LICENSE file for details
