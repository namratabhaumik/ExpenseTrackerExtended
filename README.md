# AWS Expense Tracker App with Kubernetes and EKS

This project is an extension of my previous AWS-based [expense tracker app](https://github.com/namratabhaumik/ExpenseTracker), where I integrated Docker, Kubernetes and AWS EKS (Elastic Kubernetes Service) for container orchestration and scalability. The goal of this project was to explore the power of AWS services, containerization with Docker, and orchestration with Kubernetes to build a scalable, cloud-native application.

## Features

- **Serverless Architecture**: Utilizes AWS Lambda for backend logic, DynamoDB for data storage, and AWS Cognito for authentication.
- **Containerization with Docker**: The frontend (React) and backend (Django) are containerized, ensuring a consistent environment across different stages of deployment.
- **Kubernetes and AWS EKS**: Kubernetes orchestrates the containers, with AWS EKS managing the Kubernetes clusters for scalability and reliability.
- **AWS Services Integration**: 
  - **IAM (Identity and Access Management)**: Secure service-to-service communication.
  - **S3**: For static asset storage (e.g., images, logs).
  - **DynamoDB**: A serverless NoSQL database for storing expense data.
  - **Cognito**: User authentication and authorization.
  - **EKS**: Manages the deployment and scaling of containerized applications.

## Architecture

This project follows a microservices architecture with separate frontend and backend components:

1. **Frontend**: A React application that communicates with the backend via APIs.
2. **Backend**: A Django-based API that handles the business logic for expense tracking and integrates with AWS services.
3. **Kubernetes**: Manages the containerized frontend and backend applications, ensuring scalability and high availability.
4. **AWS EKS**: Orchestrates the Kubernetes clusters, integrating with AWS services for seamless communication.

## Technologies Used

- **Frontend**: React.js
- **Backend**: Django (Python)
- **Containerization**: Docker
- **Orchestration**: Kubernetes (AWS EKS)
- **Cloud Services**: AWS (IAM, S3, DynamoDB, Cognito, Lambda, CloudWatch, SNS)

## Setup and Installation

To run this project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/aws-expense-tracker-k8s.git
   cd aws-expense-tracker-k8s
   ```

2. **Set up the backend (Django)**:
   - Navigate to the backend directory:
     ```bash
     cd expense-tracker-backend
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Set up the Django database and run migrations:
     ```bash
     python manage.py migrate
     ```

3. **Set up the frontend (React)**:
   - Navigate to the frontend directory:
     ```bash
     cd expense-tracker-frontend
     ```
   - Install dependencies:
     ```bash
     npm install
     ```

4. **Dockerize the Application**:
   - Build the Docker containers for the frontend and backend:
     ```bash
     docker build -t react-frontend ./expense-tracker-frontend
     docker build -t django-backend ./expense-tracker-backend
     ```

5. **Start the Docker Containers**:
   - Run the containers using Docker Compose (if you have a `docker-compose.yml` file configured):
     ```bash
     docker-compose up
     ```

6. **Access the Application**:
   - Navigate to `http://localhost:8000` to see the backend API.
   - The frontend will be accessible via `http://localhost:3000`.

## AWS Deployment

To deploy the project on AWS using Kubernetes and EKS, follow these steps:

1. **Set up AWS EKS**:
   - Configure your AWS CLI and ensure you have the necessary permissions.
   - Follow the steps in the [EKS documentation](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html) to create an EKS cluster.

2. **Deploy to Kubernetes**:
   - Use Kubernetes manifests to deploy the frontend and backend services on EKS.
   - Configure the LoadBalancer to expose services externally.

## Challenges Faced

Throughout the development of this project, I faced several challenges, such as:

- **IAM Permissions**: Getting the right permissions for Lambda, DynamoDB, and EKS to work together without over-permissioning services.
- **Kubernetes Networking**: Configuring Kubernetes services, Load Balancers, and security groups properly for external communication.
- **EKS Cluster Setup**: Learning how to create and manage EKS clusters and deploying containerized applications with Kubernetes.

These challenges provided valuable learning experiences and helped me improve my skills in cloud-native development.

## Future Enhancements

1. **Infrastructure as Code (IaC)**: Implement AWS CloudFormation to automate the provisioning and configuration of AWS resources.
2. **CloudFront CDN**: Improve the performance of the frontend by using CloudFront to deliver static assets faster and securely.
3. **Frontend and Backend Improvements**: Add new features such as interactive dashboards, advanced filtering, and better user management.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

For any queries or feedback, please open an issue or reach out!

