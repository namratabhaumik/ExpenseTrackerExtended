# Expense Tracker - Cloud-Native Serverless Application

## Project Overview

A fully functional, cloud-native expense tracker with:

- **Backend**: Django API deployed on GCP Cloud Run
- **Database**: Supabase (PostgreSQL) for persistent data storage
- **Frontend**: React app deployed on Firebase Hosting
- **Authentication**: AWS Cognito for secure user management
- **File Storage**: AWS S3 for receipt uploads
- **CI/CD**: GitHub Actions with automated testing and deployment

> **Note:** This README is the single source of documentation for both backend and frontend. The previous frontend/README.md has been merged here for clarity and maintainability.

## 🚀 Running the Application

This project supports **two deployment modes** with feature parity:

### Option 1: Local Development (Recommended for Testing/Demo)

Run the app locally **without any cloud resources**:

```bash
# Terminal 1 - Backend
cd expense-tracker-backend/expense_tracker
python manage.py runserver

# Terminal 2 - Frontend
cd expense-tracker-frontend
npm start
```

**Credentials:**
- Any email/password (mock auth)
- Admin panel: http://localhost:8000/admin (username: `admin`, password: `admin`)

**What works locally:**
- ✅ Full authentication flow (mocked)
- ✅ CRUD operations on expenses (SQLite)
- ✅ File upload (returns mock URLs)
- ✅ Dark mode, responsive UI, all features

**No cost, no setup, perfect for development/demo!**

---

### Option 2: Cloud Deployment (Production)

Deploy to production using AWS, GCP, and Firebase:

- **Frontend**: Firebase Hosting
- **Backend**: GCP Cloud Run
- **Database**: Supabase PostgreSQL
- **Authentication**: AWS Cognito
- **Storage**: AWS S3

> **Note:** The original cloud deployment (https://expense-tracker-frontend-1a909.firebaseapp.com/) is currently offline for cost optimization.

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌───────────────┐
│   React App  │<──>│  Django API  │<──>│   AWS Services   │<──>│  Supabase DB  │
│  (Firebase)  │    │ (Cloud Run)  │    │ (Cognito, S3)    │    │  (PostgreSQL) │
└──────────────┘    └──────────────┘    └──────────────────┘    └───────────────┘
```

## 🖥️ Frontend Features & UI/UX

- **Modern AuthForm**: Tabbed login/signup with real-time validation, show/hide password, error/success feedback, and persistent dark/light mode toggle (global, accessible, localStorage-persisted).
- **Responsive Navbar**: Custom, production-ready Navbar with Dashboard, Expenses, Categories, Profile, and Logout. Hamburger menu for mobile, sticky with shadow, accessible, and styled with Tailwind CSS using the Minimal Neutrals palette.
- **Dashboard**: Summary cards (total expenses, transaction count, average per transaction), recent expenses table (sortable, responsive), and modern empty state illustration/spinner.
- **Expenses**: Add, list, and filter expenses by category; sort by date/amount; upload receipts; toast notifications for feedback; loading spinners; all UI fully responsive and accessible.
- **Categories & Profile**: Polished placeholder UIs for category management and account settings, with loading indicators and consistent card visuals.
- **Toast Notifications**: Success/error toasts via react-toastify, styled to match the app, accessible, and auto-dismissed.
- **Accessibility**: Full keyboard navigation, ARIA labels, focus rings, and screen reader support throughout.
- **Dark Mode**: Persistent, global toggle with smooth transitions and full support across all screens.
- **Visual Polish**: Centered layout, max-width containers, modern color palette, smooth transitions, sticky navbar, and improved table/card design.
- **Bug Fixes & Improvements**: Always fetches latest expenses, consistent color palette, improved dashboard/card/table stacking on mobile, and more.

## 📦 Backend Configuration

### Database Setup

- **Development**: SQLite (default)
- **Production**: Supabase (PostgreSQL) - automatically used when `CLOUD_RUN` environment variable is set

### Environment Variables

Create a `.env` file in the `expense-tracker-backend` directory with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=.run.app

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=expenses-table
S3_BUCKET_NAME=my-finance-tracker-receipts
S3_REGION=us-east-1

# Supabase Database (for production)
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres
```

## 🚀 Deployment

### Prerequisites

- Google Cloud Account with Cloud Run enabled
- Supabase account with a new project created
- AWS Account with Cognito, S3, and DynamoDB configured

### Backend Deployment

1. Push your code to the `main` branch
2. GitHub Actions will automatically build and deploy to Cloud Run
3. Set up the required environment variables in Cloud Run:
   - `DATABASE_URL`: Your Supabase connection string
   - `DJANGO_SECRET_KEY`: A secure secret key for Django
   - AWS credentials and other required variables

## 📝 Feature Status

| Feature Area        | Status     | Notes                                     |
| ------------------- | ---------- | ----------------------------------------- |
| Add Expense         | ✅ Present | Amount, category (free-text), description |
| List Expenses       | ✅ Present | Table view, sort/filter by date/category  |
| Edit/Delete Expense | ❌ Missing | Not yet supported                         |
| Category Management | 🚧 Partial | UI present, backend integration pending   |
| Filtering/Sorting   | ✅ Present | By date, amount, and category             |
| Dashboard           | ✅ Present | Summary cards, recent transactions        |
| Profile/Settings    | ✅ Present | UI for account info, password change      |
| Logout              | ✅ Present | Button in Navbar                          |
| Receipt Upload      | ✅ Present | Via form                                  |
| Budgeting/Analytics | ❌ Missing | Not present                               |
| Responsive Layout   | ✅ Present | Fully responsive, mobile/tablet/desktop   |

## 🧑‍💻 Prerequisites

- Python 3.11+
- Node.js 20+
- AWS CLI configured
- Google Cloud CLI (for deployment)
- Firebase CLI (for frontend deployment)

## ⚙️ Local Development Setup

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd ExpenseTrackerExtended
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd expense-tracker-backend
pip install -r requirements.txt
```

#### Environment Variables

Create `.env` file in `expense-tracker-backend/`:

```env
DJANGO_SECRET_KEY=your-secret-key-here
COGNITO_CLIENT_ID=your-cognito-client-id
COGNITO_CLIENT_SECRET=your-cognito-client-secret
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=expenses-table
S3_BUCKET_NAME=my-finance-tracker-receipts
S3_REGION=us-east-1
```

#### Setup AWS Resources

```bash
cd expense-tracker-backend
python scripts/setup_all.py
```

#### Run Django Server

```bash
cd expense_tracker
python manage.py runserver
```

### 3. Frontend Setup

#### Install Dependencies

```bash
cd expense-tracker-frontend
npm install
```

#### Environment Variables

Create `.env` file in `expense-tracker-frontend/`:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_AWS_REGION=us-east-1
REACT_APP_AWS_USER_POOL_ID=your-user-pool-id
REACT_APP_AWS_CLIENT_ID=your-client-id
```

#### Start Development Server

```bash
npm start
```

## 🧪 Testing

### Backend Testing

```bash
cd expense-tracker-backend/expense_tracker
python -m pytest
python -m pytest --cov=. --cov-report=html --cov-report=term-missing
python -m pytest auth_app/tests.py -v
```

### Frontend Testing

```bash
cd expense-tracker-frontend
npm test
npm run test:coverage
npm test -- --watch
```

### Code Quality

#### Backend Linting

```bash
cd expense-tracker-backend
flake8 expense_tracker
```

#### Frontend Linting

```bash
cd expense-tracker-frontend
npm run lint
npm run lint:fix  # Auto-fix issues
```

## 📖 API Documentation

### Authentication

All protected endpoints require a Bearer token from AWS Cognito login.

### 1. Login

**Endpoint:** `POST /api/login/`

**Request:**

```json
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

**Response:**

```json
{
  "message": "Login successful",
  "id_token": "eyJ...",
  "refresh_token": "eyJ...",
  "status": "success"
}
```

### 2. Add Expense

**Endpoint:** `POST /api/expenses/`

**Authentication:** Uses a secure, HttpOnly cookie set during login.

**Request:**

```json
{
  "amount": 25.5,
  "category": "Food",
  "description": "Lunch expense"
}
```

**Response:**

```json
{
  "message": "Expense added successfully",
  "expense_id": "uuid-here",
  "expense": {
    "id": "uuid-here",
    "user_id": "user-id",
    "amount": "25.50",
    "category": "Food",
    "description": "Lunch expense",
    "timestamp": "2024-01-01T12:00:00"
  },
  "status": "success"
}
```

### 3. Get Expenses

**Endpoint:** `GET /api/expenses/list/`

**Authentication:** Uses a secure, HttpOnly cookie set during login.

**Response:**

```json
{
  "message": "Expenses retrieved successfully",
  "expenses": [
    {
      "id": "uuid-here",
      "user_id": "user-id",
      "amount": "25.50",
      "category": "Food",
      "description": "Lunch expense",
      "timestamp": "2024-01-01T12:00:00",
      "receipt_url": "https://..."
    }
  ],
  "count": 1,
  "status": "success"
}
```

### Password Reset Flow (Frontend)

The password reset modal uses a three-step process:

1. **Enter Email:** User enters their email to request a reset code.
2. **Enter Code:** User enters the code sent to their email. The code is verified before proceeding.
3. **Enter New Password:** If the code is valid, the user can set a new password (with real-time validation and requirements).

Only one message (error or success) is shown at a time for clarity.

## 🔄 Changelog

### Latest Updates

- **Modern UI/UX:** Frontend now features a modern, responsive UI with a global dark/light theme toggle, sticky Navbar, dashboard summary, sorting/filtering, toast notifications, and accessibility improvements.
- **Password Reset Feature:** Complete password reset flow (backend and frontend), with real-time validation and error handling.
- **Frontend README merged:** All frontend documentation is now in this file.
- **Bug Fixes:** Improved dashboard, card, and table stacking on mobile; always fetches latest expenses; consistent color palette.

## 🧩 Known Gaps & Roadmap

- **Edit/Delete Expense:** Not yet supported.
- **Category Management:** UI present, backend integration pending.
- **Budgeting/Analytics:** Not present.
- **Further UI polish and advanced analytics planned.**

## 🤝 Contributing

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make changes and test locally**
   - Run backend tests: `python -m pytest`
   - Run frontend tests: `npm test`
   - Run linting: `flake8` and `npm run lint`
3. **Commit with descriptive message**
   ```bash
   git commit -m "feat: add new expense category feature"
   ```
4. **Push and create pull request**
   - Ensure CI/CD pipeline passes
   - Request code review

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Cognito for authentication
- AWS DynamoDB for database
- AWS S3 for file storage
- GCP Cloud Run for backend hosting
- Firebase for frontend hosting
- GitHub Actions for CI/CD
