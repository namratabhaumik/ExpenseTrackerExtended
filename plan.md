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
  - [x] Verify: accessToken is not present in localStorage/sessionStorage and is only sent via HttpOnly cookie.

## Phase 2: Improve and Harden (Should-Haves)

This phase focuses on improving the codebase's maintainability, testability, and feature set.

### 1. Refactor for Maintainability

- **Task:** Break down the `Expenses.js` component into smaller, more focused components.
- **Why:** The `Expenses.js` component is too large and complex, making it difficult to maintain and test.
- **Action Items:**

  - [ ] Create separate components for the "Add Expense" form, the "Upload Receipt" form, and the expenses table.

- **Task:** Use a library like `axios` for API calls.
- **Why:** `axios` provides a more consistent and powerful way to handle API requests and responses.
- **Action Items:**

  - [ ] Add `axios` to the frontend dependencies.
  - [ ] Refactor all `fetch` calls to use `axios`.

- **Task:** Refactor the backend authentication views to reduce code duplication.
- **Why:** To improve code reuse and maintainability.
- **Action Items:**

  - [ ] Create a utility function to calculate the Cognito secret hash.
  - [ ] Refactor the authentication views to use the utility function.

- **Task:** Move the DynamoDB logic from the `models.py` file to a separate service or repository layer.
- **Why:** To separate the data access logic from the model definition.
- **Action Items:**
  - [ ] Create a new `services` or `repositories` directory in the `auth_app`.
  - [ ] Move the `DynamoDBExpense` class to a new file in the new directory.

### 2. Improve Testing

- **Task:** Increase test coverage to at least 80%.
- **Why:** To ensure that the application is well-tested and to catch bugs early.
- **Action Items:**
  - [ ] Write more tests for the backend and frontend.
  - [ ] Add a test coverage check to the frontend tests in the `github-ci.yml` file.

### 3. Implement Missing Features

- **Task:** Implement the ability to edit and delete expenses.
- **Why:** To make the application more useful.
- **Action Items:**
  - [ ] Add new API endpoints to the backend for editing and deleting expenses.
  - [ ] Add UI elements to the frontend for editing and deleting expenses.

### 4. Improve Observability

- **Task:** Set up structured logging and monitoring in Google Cloud.
- **Why:** To make it easier to debug and monitor the application in production.
- **Action Items:**
  - [ ] Configure the Django application to output logs in a structured JSON format.
  - [ ] Use Google Cloud's Operations Suite (formerly Stackdriver) to view and search logs.
  - [ ] Create dashboards and alerts to monitor key metrics like error rates, latency, and resource utilization.

## Phase 3: Polish (Nice-to-Haves)

This phase focuses on polishing the application and adding advanced features.

### 1. Advanced Observability

- **Task:** Implement distributed tracing.
- **Why:** To get a better understanding of how requests flow through the system.
- **Action Items:**
  - [ ] Use a library like OpenTelemetry to add distributed tracing to the backend and frontend.

### 2. Enhanced Developer Experience

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
