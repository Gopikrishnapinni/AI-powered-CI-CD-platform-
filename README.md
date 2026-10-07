# AI-Powered CI/CD Security & Deployment Platform

Reference implementation for building, scanning, deploying, and observing Spring Boot services on AWS EKS.

## Architecture

```text
GitHub push
    |
    v
GitHub Actions --> Maven tests --> SonarQube --> Trivy --> ECR --> Helm/EKS
       |                                             |
       +--> AI failure analyzer <--------------------+

Spring Boot API --> /actuator/prometheus --> Prometheus --> Grafana
       |
       +--> /actuator/health (Kubernetes readiness/liveness)
```

## Repository layout

- `backend/` - Java 17 Spring Boot REST API with Actuator and Prometheus metrics.
- `ai-service/` - Python FastAPI service that analyzes CI/CD logs and returns likely root causes.
- `helm/ci-platform/` - Helm chart with probes, rolling updates, and rollback-friendly configuration.
- `terraform/` - AWS VPC, EKS, ECR, and IAM infrastructure.
- `.github/workflows/ci-cd.yml` - build, test, scan, publish, deploy, and failure-analysis workflow.
- `monitoring/` - Prometheus scrape configuration and Grafana dashboard provisioning.
- `docker-compose.yml` - local backend, AI service, Prometheus, and Grafana stack.

## Run locally

Requirements: Java 17, Maven 3.9+, Python 3.11+, Docker Desktop.

```powershell
docker compose up --build
```

Endpoints:

- Backend API: http://localhost:8080/api/v1/greetings
- Backend health: http://localhost:8080/actuator/health
- AI analyzer: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (`admin` / `admin`)

Run the backend without Docker:

```powershell
cd backend
mvn spring-boot:run
```

Run the AI service without Docker:

```powershell
cd ai-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Deploy to AWS

1. Configure AWS credentials and create an S3/DynamoDB Terraform backend if desired.
2. Set `TF_VAR_region`, `TF_VAR_cluster_name`, and `TF_VAR_environment`.
3. Apply infrastructure:

```powershell
cd terraform
terraform init
terraform plan
terraform apply
```

4. Connect kubectl to the cluster using the output command from Terraform.
5. Build and push the image, then deploy:

```powershell
helm upgrade --install ci-platform .\helm\ci-platform `
  --namespace ci-platform --create-namespace `
  --set image.repository=<account>.dkr.ecr.<region>.amazonaws.com/ci-platform `
  --set image.tag=<git-sha>
```

## CI/CD secrets

Configure these GitHub repository secrets:

- `AWS_ROLE_TO_ASSUME` - GitHub OIDC role ARN with ECR/EKS permissions.
- `EKS_CLUSTER_NAME` - Terraform-created cluster name.
- `SONAR_TOKEN` and `SONAR_HOST_URL` - SonarQube credentials.
- `AI_ANALYZER_URL` - deployed AI service URL, optional.

The workflow intentionally fails on high/critical Trivy findings. The failure-analysis job is allowed to report recommendations without masking the original failure.

## API examples

```powershell
curl http://localhost:8080/api/v1/greetings
curl -X POST http://localhost:8000/analyze `
  -H "Content-Type: application/json" `
  -d '{"workflow":"build","logs":"mvn test failed: Connection refused to postgres"}'
```

## Security notes

The Terraform setup uses private worker subnets, IRSA-ready EKS settings, encrypted ECR images, and GitHub OIDC instead of long-lived AWS keys. Replace all local development credentials before using this in a shared environment.
