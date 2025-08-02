# Production-Ready Roadmap

This document outlines the plan to elevate the Expense Tracker application from a personal project to a secure, scalable, and maintainable commercial product.

## Phase 1: Secure the Foundation (Must-Haves)

This phase focuses on immediate security and cleanup tasks that are critical for a production environment.

### 1. Codebase Cleanup

- [x] Delete the `k8s` directory.
- [x] Delete the `cloudformation` directory.
- [x] Update the `README.md` to remove references to Kubernetes and CloudFormation.

### 2. Secure Database and Caching

- [x] Migrate from SQLite to Supabase (PostgreSQL) for production database
- [x] Configure Django to use database-backed cache in production
- [x] Set up environment variables for database connection
- [x] Update deployment pipeline to handle database migrations

### 3. Control Deployments

- [x] Trigger production deployments only from the `main` branch.

### 4. Strengthen Security

- [x] Implement rate limiting on authentication endpoints.
- [x] Migrate to secure database connection with Supabase (SSL required)
- [x] Store database credentials in Cloud Run environment variables
- [x] Ensure all sensitive data is properly encrypted in transit and at rest

### 5. Frontend Security

- **Task:** Improve frontend token storage security.
- **Why:** Storing the `accessToken` in `localStorage` can make it vulnerable to XSS attacks.
- **Action Items:**
  - [x] Refactor the frontend to store the `accessToken` in an HttpOnly cookie.
  - [x] Update backend to set secure, HttpOnly cookies for authentication.
  - [x] **Verified:** `accessToken` is no longer stored in `localStorage` and is now handled by a secure, HttpOnly cookie set by the backend with the correct `path` attribute, resolving cross-domain authentication issues.

## Phase 2: Improve and Harden (Should-Haves)

This phase focuses on improving the codebase's maintainability, testability, and feature set.

### 1. Refactor for Maintainability

- **Task:** Break down the `Expenses.js` component into smaller, more focused components.
- **Why:** The `Expenses.js` component is too large and complex, making it difficult to maintain and test.
- **Action Items:**

  - [x] Create separate components for the "Add Expense" form, the "Upload Receipt" form, and the expenses table. (2025-07-27)

- **Task:** Use a library like `axios` for API calls.
- **Why:** `axios` provides a more consistent and powerful way to handle API requests and responses.
- **Action Items:**

  - [x] Add `axios` to the frontend dependencies. (2025-07-27)
  - [x] Refactor all `fetch` calls to use `axios`. (2025-07-27)

- **Task:** Refactor the backend authentication views to reduce code duplication.
- **Why:** To improve code reuse and maintainability.
- **Action Items:**

  - [x] Create a utility function to calculate the Cognito secret hash. (2025-07-27)
  - [x] Refactor the authentication views to use the utility function. (2025-07-27)

- **Task:** Move the DynamoDB logic from the `models.py` file to a separate service or repository layer.
- **Why:** To separate the data access logic from the model definition.
- **Action Items:**
  - [x] Create a new `services` or `repositories` directory in the `auth_app`. (2025-07-27)
  - [x] Move the `DynamoDBExpense` class to a new file in the new directory. (2025-07-27)
  - [x] Update all backend usages to use the new service layer. (2025-07-27)
  - [x] Verified: Backend expense logic refactor is complete and tested as of 2025-07-27.

### 2. Improve Testing

- **Task:** Increase test coverage to at least 80%.
- **Why:** To ensure that the application is well-tested and to catch bugs early.
- **Action Items:**
  - [x] Write more tests for the backend and frontend. (2025-07-27)
  - [x] Add a test coverage check to the frontend tests in the `github-ci.yml` file. (2025-07-27)
  - [x] All backend and frontend component tests now pass with 80%+ coverage. Frontend test suite was stabilized by mocking axios and updating test selectors to handle duplicate elements. (2025-07-27)

### 3. Implement Missing Features

- **Task:** Implement the ability to edit and delete expenses.
- **Why:** To make the application more useful.
- **Action Items:**
  - [x] Add new API endpoints to the backend for editing and deleting expenses.
  - [x] Add UI elements to the frontend for editing and deleting expenses.

### 4. Improve Observability

- **Task:** Set up structured logging and monitoring in Google Cloud.
- **Why:** To make it easier to debug and monitor the application in production.
- **Action Items:**
  - [x] Configure the Django application to output logs in a structured JSON format.
  - [x] Use Google Cloud's Operations Suite (formerly Stackdriver) to view and search logs.
  - [x] Create dashboards and alerts to monitor key metrics like error rates, latency, and resource utilization.
  - [x] **Completed:** Implemented comprehensive monitoring with structured JSON logging, request/response tracking, error monitoring, performance monitoring, dashboard configuration, and alerting policies. Added middleware for automatic logging and created setup scripts for easy deployment. (2025-01-27)

## Phase 3: Polish (Nice-to-Haves)

This phase focuses on polishing the application and adding advanced features.

### 1. Enhanced Developer Experience

- **Task:** Use a tool like Swagger/OpenAPI to generate interactive API documentation.
- **Why:** To make it easier for developers to understand and use the API.
- **Action Items:**
  - [ ] Add a library like `drf-spectacular` to the backend to generate an OpenAPI schema.
  - [ ] Add a UI like Swagger UI or ReDoc to the backend to display the interactive API documentation.

### 3. Performance Optimization

- **Task:** Optimize DynamoDB queries and data models for performance.
- **Why:** To ensure that the application is fast and responsive, even with a large amount of data.
- **Action Items:**
  - [ ] Analyze the DynamoDB queries and data models to identify any potential performance bottlenecks.
  - [ ] Use techniques like indexing and query optimization to improve performance.

## Phase 4: AI-Powered Enhancements

This phase introduces an LLM-powered feature to provide users with intelligent, actionable insights into their spending habits, significantly increasing the app's value and showcasing modern AI integration skills.

### 1. The Feature: "Smart Summary"

- **Task:** Implement an "AI Financial Summary" on the main dashboard.
- **Why:** To provide users with a quick, digestible overview of their financial activity and trends without manual analysis. This serves as a strong portfolio piece demonstrating practical AI application.
- **Action Items:**
  - [ ] **Tech Stack Definition:**
    - **LLM Provider:** Google AI for Developers (Gemini Pro API).
  - [ ] **Backend Implementation:**
    - [ ] Add `google-generativeai` and `python-dotenv` to `requirements.txt`.
    - [ ] Securely store the Google AI API key using a `.env` file and ensure `.env` is in `.gitignore`.
    - [ ] Create a new service in the backend to handle communication with the Gemini API.
    - [ ] Develop a robust prompt that sends expense data and asks for a structured JSON output of 3-5 financial insights.
    - [ ] Create a new API endpoint (e.g., `/api/financial-summary/`) to expose this functionality.
  - [ ] **Frontend Implementation:**
    - [ ] Create a new React component (`FinancialSummary.js`) to display the insights.
    - [ ] Fetch the summary from the backend API when the dashboard loads.
    - [ ] Render the insights in a clean, readable format (e.g., a bulleted list) on the dashboard.
