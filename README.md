# Expense Tracker - Cloud-Native Serverless Application

## Project Overview

A fully functional, cloud-native expense tracker with:

- **Backend**: Django API deployed on GCP Cloud Run
- **Frontend**: React app deployed on Firebase Hosting
- **Authentication**: AWS Cognito for secure user management
- **Database**: AWS DynamoDB for expense storage
- **File Storage**: AWS S3 for receipt uploads
- **CI/CD**: GitHub Actions with automated testing and deployment

## 🚀 Live Demo

- **Frontend**: https://expense-tracker-frontend-1a909.web.app
- **Backend API**: https://expense-tracker-backend-876160330159.us-central1.run.app

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   Django API    │    │   AWS Services  │
│  (Firebase)     │◄──►│  (Cloud Run)    │◄──►│  (Cognito,      │
│                 │    │                 │    │   DynamoDB, S3) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Node.js 20+
- AWS CLI configured
- Google Cloud CLI (for deployment)
- Firebase CLI (for frontend deployment)

## 🛠️ Local Development Setup

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

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html --cov-report=term-missing

# Run specific test file
python -m pytest auth_app/tests.py -v
```

### Frontend Testing

```bash
cd expense-tracker-frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run tests in watch mode
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

## 📡 API Documentation

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
  "access_token": "eyJ...",
  "id_token": "eyJ...",
  "refresh_token": "eyJ...",
  "status": "success"
}
```

### 2. Add Expense

**Endpoint:** `POST /api/expenses/`

**Headers:** `Authorization: Bearer YOUR_ACCESS_TOKEN`

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

**Headers:** `Authorization: Bearer YOUR_ACCESS_TOKEN`

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

### 4. Upload Receipt

**Endpoint:** `POST /api/receipts/upload/`

**Headers:** `Authorization: Bearer YOUR_ACCESS_TOKEN`

**Request:**

```json
{
  "file": "base64-encoded-file-content",
  "filename": "receipt.jpg"
}
```

**Response:**

```json
{
  "message": "Receipt uploaded successfully",
  "file_url": "https://s3.amazonaws.com/bucket/filename.jpg",
  "status": "success"
}
```

## 🚀 Deployment

### Backend (GCP Cloud Run)

The backend is automatically deployed via GitHub Actions when code is pushed to main branch.

**Manual Deployment:**

```bash
cd expense-tracker-backend
gcloud builds submit --tag gcr.io/PROJECT_ID/expense-tracker-backend
gcloud run deploy expense-tracker-backend \
  --image gcr.io/PROJECT_ID/expense-tracker-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend (Firebase Hosting)

The frontend is automatically deployed via GitHub Actions.

**Manual Deployment:**

```bash
cd expense-tracker-frontend
npm run build
firebase deploy
```

## 🔧 Configuration

### Environment Variables Reference

#### Backend (.env)

| Variable                | Description               | Required | Example               |
| ----------------------- | ------------------------- | -------- | --------------------- |
| `DJANGO_SECRET_KEY`     | Django secret key         | Yes      | `django-insecure-...` |
| `COGNITO_CLIENT_ID`     | AWS Cognito client ID     | Yes      | `1234567890abcdef`    |
| `COGNITO_CLIENT_SECRET` | AWS Cognito client secret | Yes      | `secret-key-here`     |
| `AWS_ACCESS_KEY_ID`     | AWS access key            | Yes      | `AKIA...`             |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key            | Yes      | `secret-key-here`     |
| `AWS_REGION`            | AWS region                | Yes      | `us-east-1`           |
| `DYNAMODB_TABLE_NAME`   | DynamoDB table name       | Yes      | `expenses-table`      |
| `S3_BUCKET_NAME`        | S3 bucket name            | Yes      | `my-receipts-bucket`  |
| `S3_REGION`             | S3 region                 | Yes      | `us-east-1`           |

#### Frontend (.env)

| Variable                     | Description          | Required | Example                 |
| ---------------------------- | -------------------- | -------- | ----------------------- |
| `REACT_APP_BACKEND_URL`      | Backend API URL      | Yes      | `http://localhost:8000` |
| `REACT_APP_AWS_REGION`       | AWS region           | Yes      | `us-east-1`             |
| `REACT_APP_AWS_USER_POOL_ID` | Cognito user pool ID | Yes      | `us-east-1_abcdef`      |
| `REACT_APP_AWS_CLIENT_ID`    | Cognito client ID    | Yes      | `1234567890abcdef`      |

## 🐳 Docker Development

### Backend

```bash
cd expense-tracker-backend
docker build -t expense-tracker-backend:dev .
docker run -p 8000:8000 --env-file .env expense-tracker-backend:dev
```

## 📊 Code Quality Standards

### Backend (Python/Django)

- **Linting**: flake8 with max line length 100
- **Testing**: pytest with 70% coverage threshold
- **Code Style**: PEP 8 compliant
- **Documentation**: Docstrings for all functions and classes

### Frontend (React/JavaScript)

- **Linting**: ESLint with React and accessibility rules
- **Testing**: Jest with React Testing Library
- **Code Style**: Single quotes, semicolons, 2-space indentation
- **Coverage**: 70% threshold for statements, branches, functions, lines

## 🔍 Troubleshooting

### Common Backend Issues

1. **Import errors in tests**

   - Ensure you're running tests from the correct directory
   - Check that `PYTHONPATH` includes the project root

2. **AWS credentials not found**

   - Verify `.env` file exists and has correct values
   - Check AWS CLI configuration: `aws configure list`

3. **DynamoDB table not found**
   - Run setup script: `python scripts/setup_all.py`
   - Verify table name in environment variables

### Common Frontend Issues

1. **ESLint errors**

   - Run `npm run lint:fix` to auto-fix issues
   - Check `.eslintrc.js` for rule configuration

2. **Test failures**

   - Ensure all mocks are properly set up
   - Check that test environment variables are set

3. **Build failures**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check for syntax errors in React components

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

## 🖥️ Frontend UI Status

- The React frontend is intentionally minimal, clean, and responsive.
- Uses the "Minimal Neutrals" color palette:
  - **Primary:** #4B5563 (Slate Gray)
  - **Secondary:** #9CA3AF (Light Gray)
  - **Accent:** #2563EB (Blue)
  - **Background:** #F9FAFB (Lightest Gray)
  - **Success:** #10B981 (Emerald Green)
  - **Error:** #EF4444 (Red)
- All CSS files are organized under `src/styles/` for maintainability.
- The UI is fully responsive and works well on mobile, tablet, and desktop.
- **Advanced UI/UX features are planned for future iterations.**

## [Chore] Frontend Structure & Documentation

- All frontend CSS files are now organized under `src/styles/` for better maintainability and separation of concerns.
- The redundant frontend `README.md` has been removed; this is now the single source of project documentation.
