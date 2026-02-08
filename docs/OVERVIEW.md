# Architecture Overview

## System Architecture

The Expense Tracker supports two deployment modes with identical functionality.

### Local Mode

```
┌─────────────────────────────┐
│    Developer's Machine      │
│                             │
│  React App (Port 3000)      │
│       ↓                     │
│  Django API (Port 8000)     │
│       ↓                     │
│  SQLite Database            │
└─────────────────────────────┘
```

### Cloud Mode

```
┌─────────────────────────────────────────┐
│         Production (Cloud)              │
│                                         │
│  Firebase Hosting                       │
│       ↓                                 │
│  GCP Cloud Run (Django API)             │
│       ↓                                 │
│  ┌──────────────────────────────────┐  │
│  │ Supabase (PostgreSQL)            │  │
│  │ AWS Cognito (Auth)               │  │
│  │ AWS S3 (File Storage)            │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Component Overview

| Component | Local | Cloud |
|-----------|-------|-------|
| **Frontend** | React (localhost:3000) | Firebase Hosting |
| **Backend** | Django (localhost:8000) | GCP Cloud Run |
| **Database** | SQLite | PostgreSQL (Supabase) |
| **Auth** | Mock JWT | AWS Cognito |
| **Storage** | Mock URLs | AWS S3 |

## Data Flow

```
User Action
    ↓
React Frontend
    ↓
HTTP Request to Backend
    ↓
Django API
    ↓
Database Query
    ↓
Response back to Frontend
    ↓
UI Update
```
