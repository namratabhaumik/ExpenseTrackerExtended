# Expense Tracker Frontend

## Features

- User login (Cognito)
- View and add expenses (DynamoDB backend)

## Environment Variables

Create a `.env` file in the root of `expense-tracker-frontend` with:

```
REACT_APP_BACKEND_URL=http://localhost:8000  # Or your backend URL
REACT_APP_AWS_REGION=your-region
REACT_APP_AWS_USER_POOL_ID=your-user-pool-id
REACT_APP_AWS_CLIENT_ID=your-client-id
```

## Expenses Endpoints

- **GET /api/expenses/list/**: Fetch all expenses for the logged-in user.
- **POST /api/expenses/**: Add a new expense. Required fields: `amount`, `category`. Optional: `description`.

## Usage

1. Login with your credentials.
2. After login, you can:
   - View your expenses in a table.
   - Add a new expense using the form.

## Development

- Start the backend server first.
- Then run:
  ```
  npm install
  npm start
  ```
- The app will use the backend URL from your `.env` file.
