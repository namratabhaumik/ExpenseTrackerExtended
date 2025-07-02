# Development Guide

This guide covers local development setup, testing, and linting for the Expense Tracker project.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for backend containerization)
- AWS CLI configured (for AWS services)

## Backend Development

### Setup

1. **Install Python dependencies:**

   ```bash
   cd expense-tracker-backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in `expense-tracker-backend/` with:

   ```env
   DJANGO_SECRET_KEY=your-secret-key
   COGNITO_CLIENT_ID=your-cognito-client-id
   COGNITO_CLIENT_SECRET=your-cognito-client-secret
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_REGION=us-east-1
   DYNAMODB_TABLE_NAME=expenses-table
   S3_BUCKET_NAME=my-finance-tracker-receipts
   S3_REGION=us-east-1
   ```

3. **Set up AWS resources:**

   ```bash
   cd expense-tracker-backend
   python scripts/setup_all.py
   ```

4. **Run Django server:**
   ```bash
   cd expense-tracker-backend/expense_tracker
   python manage.py runserver
   ```

### Testing

1. **Run all tests:**

   ```bash
   cd expense-tracker-backend/expense_tracker
   python -m pytest
   ```

2. **Run tests with coverage:**

   ```bash
   python -m pytest --cov=. --cov-report=html --cov-report=term-missing
   ```

3. **Run specific test file:**

   ```bash
   python -m pytest auth_app/tests.py -v
   ```

4. **Run tests with specific markers:**
   ```bash
   python -m pytest -m unit
   python -m pytest -m integration
   ```

### Linting

1. **Run flake8 linting:**

   ```bash
   cd expense-tracker-backend
   flake8 expense_tracker
   ```

2. **Run with specific rules:**
   ```bash
   flake8 expense_tracker --count --select=E9,F63,F7,F82 --show-source --statistics
   ```

## Frontend Development

### Setup

1. **Install Node.js dependencies:**

   ```bash
   cd expense-tracker-frontend
   npm install
   ```

2. **Set up environment variables:**
   Create a `.env` file in `expense-tracker-frontend/` with:

   ```env
   REACT_APP_BACKEND_URL=http://localhost:8000
   REACT_APP_AWS_REGION=us-east-1
   REACT_APP_AWS_USER_POOL_ID=your-user-pool-id
   REACT_APP_AWS_CLIENT_ID=your-client-id
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

### Testing

1. **Run all tests:**

   ```bash
   npm test
   ```

2. **Run tests with coverage:**

   ```bash
   npm run test:coverage
   ```

3. **Run tests in watch mode:**

   ```bash
   npm test -- --watch
   ```

4. **Run specific test file:**
   ```bash
   npm test -- App.test.js
   ```

### Linting

1. **Run ESLint:**

   ```bash
   npm run lint
   ```

2. **Fix linting issues automatically:**
   ```bash
   npm run lint:fix
   ```

## Docker Development

### Backend

1. **Build Docker image:**

   ```bash
   cd expense-tracker-backend
   docker build -t expense-tracker-backend:dev .
   ```

2. **Run container:**
   ```bash
   docker run -p 8000:8000 --env-file .env expense-tracker-backend:dev
   ```

## CI/CD Pipeline

The GitHub Actions workflow automatically runs:

### Backend Pipeline

- ✅ Install dependencies
- ✅ Run flake8 linting
- ✅ Run Django checks
- ✅ Run pytest with coverage (70% threshold)
- ✅ Build Docker image
- ✅ Deploy to GCP Cloud Run

### Frontend Pipeline

- ✅ Install dependencies
- ✅ Run ESLint
- ✅ Run Jest tests with coverage
- ✅ Build React app
- ✅ Deploy to Firebase Hosting

## Code Quality Standards

### Python (Backend)

- **Linting:** flake8 with max line length 100
- **Testing:** pytest with 70% coverage threshold
- **Code Style:** PEP 8 compliant
- **Documentation:** Docstrings for all functions and classes

### JavaScript/React (Frontend)

- **Linting:** ESLint with React and accessibility rules
- **Testing:** Jest with React Testing Library
- **Code Style:** Single quotes, semicolons, 2-space indentation
- **Coverage:** 70% threshold for statements, branches, functions, lines

## Common Issues and Solutions

### Backend Issues

1. **Import errors in tests:**

   - Ensure you're running tests from the correct directory
   - Check that `PYTHONPATH` includes the project root

2. **AWS credentials not found:**

   - Verify `.env` file exists and has correct values
   - Check AWS CLI configuration: `aws configure list`

3. **DynamoDB table not found:**
   - Run setup script: `python scripts/setup_all.py`
   - Verify table name in environment variables

### Frontend Issues

1. **ESLint errors:**

   - Run `npm run lint:fix` to auto-fix issues
   - Check `.eslintrc.js` for rule configuration

2. **Test failures:**

   - Ensure all mocks are properly set up
   - Check that test environment variables are set

3. **Build failures:**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check for syntax errors in React components

## Contributing

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test locally:**

   - Run backend tests: `python -m pytest`
   - Run frontend tests: `npm test`
   - Run linting: `flake8` and `npm run lint`

3. **Commit with descriptive message:**

   ```bash
   git commit -m "feat: add new expense category feature"
   ```

4. **Push and create pull request:**
   - Ensure CI/CD pipeline passes
   - Request code review

## Environment Variables Reference

### Backend (.env)

| Variable                | Description               | Required |
| ----------------------- | ------------------------- | -------- |
| `DJANGO_SECRET_KEY`     | Django secret key         | Yes      |
| `COGNITO_CLIENT_ID`     | AWS Cognito client ID     | Yes      |
| `COGNITO_CLIENT_SECRET` | AWS Cognito client secret | Yes      |
| `AWS_ACCESS_KEY_ID`     | AWS access key            | Yes      |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key            | Yes      |
| `AWS_REGION`            | AWS region                | Yes      |
| `DYNAMODB_TABLE_NAME`   | DynamoDB table name       | Yes      |
| `S3_BUCKET_NAME`        | S3 bucket name            | Yes      |
| `S3_REGION`             | S3 region                 | Yes      |

### Frontend (.env)

| Variable                     | Description          | Required |
| ---------------------------- | -------------------- | -------- |
| `REACT_APP_BACKEND_URL`      | Backend API URL      | Yes      |
| `REACT_APP_AWS_REGION`       | AWS region           | Yes      |
| `REACT_APP_AWS_USER_POOL_ID` | Cognito user pool ID | Yes      |
| `REACT_APP_AWS_CLIENT_ID`    | Cognito client ID    | Yes      |
