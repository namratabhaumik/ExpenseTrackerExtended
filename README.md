# AWS Expense Tracker App - Cloud-Native Backend with DynamoDB

This project is an extension of my previous AWS-based [expense tracker app](https://github.com/namratabhaumik/ExpenseTracker) with a focus on cloud-native architecture. Here I've integrated Django with AWS services, containerization with Docker, and orchestration with Kubernetes using AWS EKS for microservices-based scalability.

## Medium Links

- [Mastering Containerization and Orchestration: Lessons from My First AWS EKS Project](https://namrata-bhaumik.medium.com/mastering-containerization-and-orchestration-lessons-from-my-first-aws-eks-project-0e9918f43b12?source=friends_link&sk=08cef3208d13c6e2dc68b067e3576285)
- [Overcoming Cloud Challenges: Lessons Learned from Building a Serverless AWS App](https://namrata-bhaumik.medium.com/overcoming-cloud-challenges-lessons-learned-from-building-a-serverless-aws-app-5d3c59efc9eb?source=friends_link&sk=437b217db913371db42d0e9ec5831cc4)

## Features

- **Cloud-Native Backend**: Django API with AWS DynamoDB for serverless, scalable data storage
- **Serverless Authentication**: AWS Cognito for secure user authentication and JWT token management
- **Containerization with Docker**: Frontend (React) and backend (Django) containerized for consistent deployment
- **Kubernetes and AWS EKS**: Container orchestration for scalability and high availability
- **AWS Services Integration**:
  - **DynamoDB**: Serverless NoSQL database for expense data (free tier friendly)
  - **Cognito**: User authentication and authorization
  - **S3**: For receipt file storage (planned)
  - **SNS**: For notifications (planned)
  - **IAM**: Secure service-to-service communication
  - **EKS**: Kubernetes cluster management

## Architecture

This project follows a cloud-native microservices architecture:

1. **Frontend**: React application communicating with Django APIs
2. **Backend**: Django API with DynamoDB integration for expense management
3. **Database**: AWS DynamoDB (serverless, auto-scaling)
4. **Authentication**: AWS Cognito (JWT tokens)
5. **Containerization**: Docker for consistent environments
6. **Orchestration**: Kubernetes (AWS EKS) for deployment and scaling

## Technologies Used

- **Frontend**: React.js
- **Backend**: Django (Python) with boto3 for AWS integration
- **Database**: AWS DynamoDB (serverless NoSQL)
- **Authentication**: AWS Cognito
- **Containerization**: Docker
- **Orchestration**: Kubernetes (AWS EKS)
- **Cloud Services**: AWS (DynamoDB, Cognito, S3, SNS, IAM, EKS)

## API Endpoints

### Authentication

- **POST** `/api/login/` - User login with Cognito

### Expense Management

- **POST** `/api/expenses/` - Add a new expense
- **GET** `/api/expenses/list/?user_id=<user_id>` - Get expenses for a user
- **POST** `/api/receipts/upload/` - Upload receipt (placeholder for S3 integration)

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- AWS Account with appropriate permissions
- AWS CLI configured

### 1. Clone and Setup Backend

```bash
git clone https://github.com/your-username/aws-expense-tracker-k8s.git
cd aws-expense-tracker-k8s/expense-tracker-backend
```

### 2. Environment Configuration

Create a `.env` file in `expense-tracker-backend/`:

```env
DJANGO_SECRET_KEY=your-django-secret-key
COGNITO_REGION=us-east-1
COGNITO_CLIENT_ID=your-cognito-client-id
COGNITO_CLIENT_SECRET=your-cognito-client-secret
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=expense-tracker-table
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup AWS Resources

```bash
# Run the master setup script to create DynamoDB table
python scripts/setup_all.py

# Or run individual scripts:
python scripts/setup_dynamodb.py  # Create DynamoDB table
python scripts/check_s3.py        # Check S3 bucket (using existing bucket)
python scripts/test_s3_upload.py  # Test S3 upload functionality
```

**Note:** This project uses your existing S3 bucket `my-finance-tracker-receipts`. If you want to use a different bucket, update the `S3_BUCKET_NAME` in your `.env` file.

### 5. Run Django Server

```bash
cd expense_tracker
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

### 6. Setup Frontend (Optional)

```bash
cd ../expense-tracker-frontend
npm install
npm start
```

## API Testing with curl

### 1. User Login

```bash
curl -X POST "http://127.0.0.1:8000/api/login/" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"your-email@example.com\", \"password\": \"your-password\"}"
```

**Response:**

```json
{
  "message": "Login successful",
  "access_token": "eyJraWQiOiJ...",
  "id_token": "eyJraWQiOiJ...",
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ..."
}
```

### 2. Add Expense

```bash
curl -X POST "http://127.0.0.1:8000/api/expenses/" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"test_user\", \"amount\": 25.50, \"category\": \"Food\", \"description\": \"Lunch\"}"
```

**Response:**

```json
{
  "message": "Expense added successfully",
  "expense_id": "550e8400-e29b-41d4-a716-446655440000",
  "expense": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "test_user",
    "amount": "25.50",
    "category": "Food",
    "description": "Lunch",
    "timestamp": "2025-06-29T22:30:00.123456"
  }
}
```

### 3. Get User Expenses

```bash
curl -X GET "http://127.0.0.1:8000/api/expenses/list/?user_id=test_user"
```

**Response:**

```json
{
  "message": "Expenses retrieved successfully",
  "expenses": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "test_user",
      "amount": "25.50",
      "category": "Food",
      "description": "Lunch",
      "timestamp": "2025-06-29T22:30:00.123456",
      "receipt_url": null
    }
  ],
  "count": 1
}
```

### 4. Upload Receipt

```bash
curl -X POST "http://127.0.0.1:8000/api/receipts/upload/" \
  -H "Content-Type: application/json" \
  -d "{\"file\": \"base64-encoded-file-content\", \"filename\": \"receipt.jpg\", \"user_id\": \"test_user\", \"expense_id\": \"optional-expense-id\"}"
```

**Response:**

```json
{
  "message": "Receipt uploaded successfully",
  "file_url": "https://my-finance-tracker-receipts.s3.us-east-1.amazonaws.com/user_id/filename.jpg",
  "file_key": "user_id/filename.jpg",
  "file_name": "receipt.jpg",
  "expense_id": "optional-expense-id",
  "status": "success"
}
```

**Note:**

- `file`: Base64 encoded file content (max 10MB)
- `filename`: Name of the file
- `user_id`: Required user identifier
- `expense_id`: Optional - if provided, links receipt to existing expense

## AWS Deployment

### Infrastructure as Code (CloudFormation)

Deploy the CloudFormation stack:

```bash
aws cloudformation create-stack \
  --stack-name ExpenseTrackerStack \
  --template-body file://cloudformation/expense-tracker-stack.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

### Kubernetes Deployment

1. **Build and push Docker images:**

   ```bash
   docker build -t expense-tracker-backend ./expense-tracker-backend
   docker build -t expense-tracker-frontend ./expense-tracker-frontend
   ```

2. **Deploy to EKS:**
   ```bash
   kubectl apply -f k8s/
   ```

## Current Status

### ✅ Completed

- Cloud-native Django backend with DynamoDB integration
- AWS Cognito authentication
- Core expense management APIs (add, list)
- Environment variable configuration
- Docker containerization
- Kubernetes deployment manifests

### 🔄 In Progress

- S3 integration for receipt uploads
- SNS notifications
- Frontend React integration
- Comprehensive testing

### 📋 Planned

- Advanced expense analytics
- Receipt OCR processing
- Multi-user support with proper authorization
- Performance monitoring and logging

## Free Tier Considerations

This project is designed to work within AWS Free Tier limits:

- **DynamoDB**: 25GB storage + 25 WCU/RCU per month
- **Cognito**: 50,000 MAUs
- **S3**: 5GB storage
- **EKS**: Not included in free tier (consider Lambda for serverless)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

For any queries or feedback, please open an issue or reach out!

#Test commit
