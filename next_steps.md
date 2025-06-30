# Next Steps: Backend-First Roadmap for Expense Tracker

## 1. Backend (Django) - Immediate Priorities

- **Move Secrets to Environment Variables**

  - Remove hardcoded Cognito client ID/secret and Django SECRET_KEY from code.
  - Use `os.environ.get()` in settings and views.
  - Document required environment variables in this file or README.

- **Implement Core Expense Endpoints**

  - Add endpoints for:
    - Add Expense (POST)
    - Get Expenses (GET, filter by user)
    - Upload Receipt (POST, file upload)
  - Use Django REST Framework for serialization and validation (optional, but recommended for maintainability).

- **Integrate with AWS Services**

  - Ensure backend can:
    - Upload receipts to S3
    - Store/retrieve expenses in DynamoDB
    - Send notifications via SNS (if required for MVP)

- **Error Handling & Logging**

  - Replace all `print` statements with Django logging.
  - Return clear, consistent error messages to the frontend.

- **Testing**

  - Add at least one test for each endpoint (success and failure cases).
  - Use Django's test client for API tests.

- **Documentation**
  - Add endpoint documentation (in README or as docstrings).
  - Document environment variables and AWS setup requirements.

## 2. Frontend (Minimal)

- **Login UI**

  - Use existing login form; store JWT on success.

- **Expense Management UI**

  - Simple forms for:
    - Adding an expense
    - Uploading a receipt
    - Listing expenses
  - Use fetch/axios to call backend endpoints with JWT.

- **No Over-Engineering**
  - No advanced routing, state management, or styling unless required for workflow.

## 3. General

- **Security**

  - Never commit secrets or credentials.
  - Use `.env` files (add to `.gitignore`).

- **Update Documentation**
  - Keep README and this file up to date as features are added.

---

## How to Run the Backend Server Locally

1. **Install Python dependencies**

   ```bash
   cd ExpenseTrackerExtended/expense-tracker-backend
   pip install -r requirements.txt
   ```

2. **Set environment variables**

   - Create a `.env` file or set variables in your shell for:
     - `DJANGO_SECRET_KEY`
     - `COGNITO_CLIENT_ID`
     - `COGNITO_CLIENT_SECRET`
     - Any AWS credentials needed for boto3

3. **Run migrations**

   ```bash
   python manage.py migrate
   ```

4. **Start the server**

   ```bash
   python manage.py runserver
   ```

5. **Test existing functionality**
   - The login endpoint is available at: `POST /api/login/`
   - Use Postman or curl to test login with your Cognito credentials.

---

_Update this file as you complete each step or add new requirements._
