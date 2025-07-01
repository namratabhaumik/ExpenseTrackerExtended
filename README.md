# Expense Tracker

## Project Overview

A cloud-native, serverless expense tracker with:

- Django backend (deployed on GCP Cloud Run)
- React frontend (to be deployed on AWS S3 + CloudFront)
- AWS Cognito for authentication
- AWS DynamoDB for expense storage
- AWS S3 for receipt uploads

## Deployment Architecture

- **Backend:** GCP Cloud Run (Dockerized Django)
- **Frontend:** AWS S3 + CloudFront (static React build)
- **AWS Services:** Cognito, DynamoDB, S3
- **Infrastructure as Code:** CloudFormation and Kubernetes manifests are present for reference, but not used in the current deployment.

## How to Test (API)

Replace `YOUR_ACCESS_TOKEN_HERE` with the token from the login response.

### 1. Login

```bash
curl -X POST "https://expense-tracker-backend-876160330159.us-central1.run.app/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "password": "your-password"}'
```

### 2. Add Expense

```bash
curl -X POST "https://expense-tracker-backend-876160330159.us-central1.run.app/api/expenses/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{"amount": 25.50, "category": "Food", "description": "Lunch"}'
```

### 3. Get Expenses

```bash
curl -X GET "https://expense-tracker-backend-876160330159.us-central1.run.app/api/expenses/list/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 4. Upload Receipt

```bash
curl -X POST "https://expense-tracker-backend-876160330159.us-central1.run.app/api/receipts/upload/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{"file": "VGhpcyBpcyBhIHRlc3QgcmVjZWlwdCBmaWxlLg==", "filename": "test_receipt.txt"}'
```

## Current Status

- [x] Backend deployed to GCP Cloud Run
- [x] API tested and working (login, add expense, get expenses, upload receipt)
- [x] AWS Cognito, DynamoDB, S3 integration
- [x] CI/CD with GitHub Actions and Workload Identity Federation
- [ ] Frontend integration (next step)
- [ ] Frontend deployment to S3/CloudFront (next step)

## Note

CloudFormation and Kubernetes manifests are included to demonstrate infrastructure-as-code and k8s (previously implemented in the project), but are not used in the current deployment. The chosen architecture is optimized for serverless, cost-effective, and quick deployments.
