# Cloud Production Mode

Guide for deploying the Expense Tracker to production using AWS, GCP, and Firebase.

**Note:** Cloud mode uses **AWS Cognito** for authentication, while local development mode uses **Django sessions with CSRF protection**. See [AUTH_FLOW.md](./AUTH_FLOW.md) for a comparison of both authentication mechanisms.

## Cloud Mode Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   PRODUCTION (Cloud)                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  User's Browser                                    │ │
│  │  (Internet)                                        │ │
│  └──────────────────────┬─────────────────────────────┘ │
│                         │                                 │
│                         │ HTTPS                           │
│                         ↓                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Firebase Hosting (Frontend)                     │   │
│  │  ├─ React App (optimized build)                  │   │
│  │  ├─ Tailwind CSS (minified)                      │   │
│  │  ├─ static assets (CDN cached)                   │   │
│  │  └─ https://your-domain.firebaseapp.com          │   │
│  └──────────────────────┬─────────────────────────────┘ │
│                         │                                 │
│                         │ HTTP/REST API                   │
│                         ↓                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  GCP Cloud Run (Backend)                         │   │
│  │  ├─ Django REST API (containerized)              │   │
│  │  ├─ Auto-scaling                                 │   │
│  │  ├─ Environment variables (secrets)              │   │
│  │  └─ https://expense-tracker.run.app              │   │
│  └──────────────────────┬─────────────────────────────┘ │
│                         │                                 │
│          ┌──────────────┼──────────────┐                 │
│          │              │              │                 │
│          ↓              ↓              ↓                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Supabase     │ │AWS Cognito   │ │AWS S3        │    │
│  │(PostgreSQL)  │ │(Auth)        │ │(Storage)     │    │
│  │              │ │              │ │              │    │
│  │users & exp   │ │JWT tokens    │ │receipts      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  GitHub Actions (CI/CD)                          │   │
│  │  ├─ Test on push                                 │   │
│  │  ├─ Build Docker image                           │   │
│  │  ├─ Push to Cloud Run                            │   │
│  │  └─ Auto-deploy on main branch                   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Cloud Deployment Workflow

### Prerequisites

1. **Google Cloud Account**
   - Cloud Run enabled
   - Service account with appropriate permissions

2. **AWS Account**
   - Cognito User Pool configured
   - S3 bucket for receipts
   - DynamoDB table (optional)

3. **Supabase Account**
   - PostgreSQL database created
   - Database URL and credentials

4. **Firebase Account**
   - Firebase project created
   - Hosting enabled

5. **GitHub Repository**
   - Code pushed to main branch
   - Secrets configured (AWS creds, DB URL, etc)

### Deployment Steps

```
┌─────────────────────────────────────────────────┐
│  1. Setup Cloud Resources                       │
│  ├─ Create Supabase PostgreSQL database         │
│  ├─ Configure AWS Cognito User Pool             │
│  ├─ Create AWS S3 bucket for receipts           │
│  └─ Create GCP Cloud Run service                │
└─────────────┬───────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────┐
│  2. Configure Environment Variables             │
│  ├─ CLOUD_RUN=true                              │
│  ├─ DATABASE_URL=<Supabase PostgreSQL URL>      │
│  ├─ COGNITO_USER_POOL_ID=<AWS pool ID>          │
│  ├─ AWS_ACCESS_KEY_ID=<AWS key>                 │
│  ├─ AWS_SECRET_ACCESS_KEY=<AWS secret>          │
│  └─ S3_BUCKET_NAME=<S3 bucket name>             │
└─────────────┬───────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────┐
│  3. Setup GitHub Actions Secrets                │
│  └─ Configure CI/CD pipeline for auto-deploy    │
└─────────────┬───────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────┐
│  4. Push Code                                   │
│  ├─ Commit changes                              │
│  ├─ Push to main branch                         │
│  └─ GitHub Actions triggers automatically       │
└─────────────┬───────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────┐
│  5. CI/CD Pipeline                              │
│  ├─ Run tests                                   │
│  ├─ Build Docker image                          │
│  ├─ Push to Cloud Run                           │
│  └─ Deploy to production                        │
└─────────────┬───────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────┐
│  6. Verify Deployment                           │
│  ├─ Check Cloud Run URL                         │
│  ├─ Test API endpoints                          │
│  ├─ Verify database connection                  │
│  └─ Monitor logs                                │
└─────────────────────────────────────────────────┘
```

## Authentication Flow (Cloud Mode)

```
┌──────────────────────────────────────────────┐
│  User enters credentials in Frontend         │
│  (email/password)                            │
└──────────────────┬──────────────────────────┘
                   │
                   ↓
         ┌─────────────────────┐
         │  Frontend validates │
         │  input locally      │
         └──────────┬──────────┘
                    │
                    ↓
         ┌──────────────────────────────────┐
         │  POST /api/login/                │
         │  {email, password}               │
         └──────────┬───────────────────────┘
                    │
                    ↓
         ┌──────────────────────────────────┐
         │  Backend Receives Request        │
         │  ├─ Calculate secret hash        │
         │  ├─ Call AWS Cognito             │
         │  └─ Validate credentials         │
         └──────────┬───────────────────────┘
                    │
                    ├─ Valid ─┐
                    │         │
                    ↓         ↓
         ┌──────────────┐  ┌──────────────┐
         │ Cognito OK   │  │ Invalid Cred │
         │ Get tokens   │  │ Return error │
         └──────┬───────┘  └──────────────┘
                │
                ↓
         ┌──────────────────────────────────┐
         │  Backend Returns:                │
         │  ├─ id_token                     │
         │  ├─ refresh_token                │
         │  └─ Sets HttpOnly cookie         │
         │     with access_token            │
         └──────────┬───────────────────────┘
                    │
                    ↓
         ┌──────────────────────────────────┐
         │  Frontend Updates:               │
         │  ├─ Stores refresh_token         │
         │  ├─ Cookie has access_token      │
         │  └─ User Authenticated           │
         └──────────────────────────────────┘
```

## Database Configuration

### Supabase PostgreSQL Setup

```sql
-- Tables created by Django migrations
CREATE TABLE auth_app_expense (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    amount DECIMAL(10, 2),
    category VARCHAR(100),
    description TEXT,
    receipt_url VARCHAR(500),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_user_id ON auth_app_expense(user_id);
CREATE INDEX idx_timestamp ON auth_app_expense(timestamp DESC);
```

### Environment Variables for Cloud

```bash
# Database
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres

# AWS Cognito
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_CLIENT_ID=xxxxx
COGNITO_CLIENT_SECRET=xxxxx

# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# S3 Storage
S3_BUCKET_NAME=expense-tracker-receipts
S3_REGION=us-east-1

# Django
DJANGO_SECRET_KEY=your-secret-key-here
CLOUD_RUN=true
```

