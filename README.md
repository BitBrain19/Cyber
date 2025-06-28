# SecurityAI - Enterprise IT Infrastructure Monitoring Platform

A comprehensive, production-ready IT infrastructure monitoring and threat detection platform with AI/ML capabilities, designed for enterprise security teams, CISOs, SOC analysts, and large organizations.

## 🚀 Overview

SecurityAI provides real-time monitoring, threat detection, and security analytics for IT infrastructure including networks, servers, endpoints, and user activity. The platform combines traditional security monitoring with advanced AI/ML capabilities to detect anomalies, classify threats, and provide actionable insights.

### Key Features

- **Real-time Monitoring**: WebSocket-based streaming for live dashboard updates
- **AI/ML Pipeline**: Anomaly detection, threat classification, NLP log parsing, graph analysis
- **Multi-database Architecture**: PostgreSQL, InfluxDB, Elasticsearch, Redis
- **Enterprise Security**: JWT authentication, RBAC, rate limiting, circuit breakers
- **Scalable Architecture**: Kubernetes deployment, auto-scaling, load balancing
- **Compliance Ready**: Audit logging, data encryption, secure APIs
- **Threat Intelligence**: Integration with MITRE ATT&CK, VirusTotal, AlienVault OTX

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/Vite)                   │
│  Dashboard │ Alerts │ Attack Paths │ Reports │ Settings        │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer (NGINX)                       │
│                    Rate Limiting & SSL                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Auth API  │ │ Monitor API │ │  Alerts API │ │ Visualize   │ │
│  │             │ │             │ │             │ │     API     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ Reports API │ │ Train API   │ │ Metrics API │ │ WebSocket   │ │
│  │             │ │             │ │             │ │   Stream    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │    InfluxDB     │ │  Elasticsearch  │
│ (Users/Assets/  │ │ (Time Series    │ │   (Log Search   │
│   Alerts)       │ │    Events)      │ │   & Analytics)  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                    │               │               │
                    ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│     Redis       │ │     Kafka       │ │   ML Pipeline   │
│   (Cache)       │ │   (Streaming)   │ │ (AI/ML Models)  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **React Router** for navigation

### Backend
- **FastAPI** (Python) for async APIs
- **PostgreSQL** for relational data
- **InfluxDB** for time-series data
- **Elasticsearch** for log search
- **Redis** for caching
- **Kafka** for streaming

### AI/ML
- **PyTorch** for deep learning
- **scikit-learn** for traditional ML
- **Transformers** for NLP
- **NetworkX** for graph analysis
- **MLflow** for model management
- **ONNX** for model optimization

### Infrastructure
- **Docker** for containerization
- **Kubernetes** for orchestration
- **Prometheus** for monitoring
- **Grafana** for visualization
- **AWS EKS** for cloud deployment

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- InfluxDB 2.0+
- Elasticsearch 8.0+
- Redis 7.0+
- Kafka 3.0+

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd securityai-platform
```

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 4. Database Setup

```bash
# PostgreSQL
docker exec -it securityai-postgres psql -U securityai -d securityai
# Tables will be created automatically on first run

# InfluxDB
# Buckets will be created automatically

# Elasticsearch
# Indexes will be created automatically
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user info

### Monitoring
- `GET /api/v1/monitor/status` - System status
- `GET /api/v1/monitor/metrics` - System metrics
- `GET /api/v1/monitor/events` - Get events
- `POST /api/v1/monitor/events` - Create event
- `WebSocket /api/v1/monitor/ws` - Real-time streaming

### Alerts
- `GET /api/v1/alerts` - Get alerts
- `POST /api/v1/alerts` - Create alert
- `GET /api/v1/alerts/{id}` - Get alert details
- `PUT /api/v1/alerts/{id}/status` - Update alert status
- `POST /api/v1/alerts/{id}/remediate` - Execute remediation

### Visualization
- `GET /api/v1/visualize/attack-paths` - Get attack paths
- `GET /api/v1/visualize/network-topology` - Get network topology
- `GET /api/v1/visualize/threat-map` - Get threat map
- `GET /api/v1/visualize/user-behavior` - Get user behavior

### Reports
- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports/{id}` - Download report
- `GET /api/v1/reports` - List reports

### ML Training
- `POST /api/v1/train` - Trigger model training (admin)
- `GET /api/v1/train/status/{id}` - Get training status
- `GET /api/v1/train/history` - Get training history

### Metrics
- `GET /api/v1/metrics` - Get all metrics
- `GET /api/v1/metrics/ml` - Get ML metrics
- `GET /api/v1/metrics/system` - Get system metrics
- `GET /api/v1/metrics/drift` - Get model drift metrics

## 🤖 ML Pipeline

### Models

1. **Anomaly Detection (Isolation Forest)**
   - Detects unusual patterns in security events
   - Features: bytes_transferred, login_attempts, duration, event_type
   - Output: anomaly_score (0-1)

2. **Threat Classification (Random Forest)**
   - Classifies events as benign/suspicious/malicious
   - Features: network metrics, user behavior, system activity
   - Output: classification with confidence score

3. **Log Parser (DistilBERT)**
   - Extracts structured data from log messages
   - Features: log message text
   - Output: entities (IP, user, action, etc.)

4. **Graph Analyzer (NetworkX)**
   - Detects lateral movement and attack paths
   - Features: network connections, asset relationships
   - Output: risk scores and attack paths

### Training

```bash
# Trigger model training
curl -X POST "http://localhost:8000/api/v1/train" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"models": ["anomaly_detector", "threat_classifier"]}'

# Check training status
curl "http://localhost:8000/api/v1/train/status/<training_id>" \
  -H "Authorization: Bearer <token>"
```

## 🔒 Security

### Authentication & Authorization

- **JWT Tokens**: Access tokens (30min) + refresh tokens (7 days)
- **Role-Based Access Control (RBAC)**:
  - `admin`: Full access, model training, user management
  - `analyst`: Alert management, report generation, data access
  - `viewer`: Read-only access to dashboards and reports

### Security Features

- **Rate Limiting**: 100 requests per minute per user
- **CORS**: Configurable allowed origins
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Input sanitization
- **TLS 1.3**: HTTPS enforcement in production

### Data Protection

- **Encryption**: AES-256 for sensitive data
- **Password Hashing**: bcrypt with salt
- **Audit Logging**: All actions logged with user context
- **Data Retention**: Configurable retention policies

## 🚀 Production Deployment

### Docker Compose (Development)

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Kubernetes (Production)

```bash
# Create namespace
kubectl create namespace securityai

# Apply secrets
kubectl apply -f backend/k8s/secrets.yaml

# Deploy application
kubectl apply -f backend/k8s/deployment.yaml

# Check status
kubectl get pods -n securityai
kubectl get services -n securityai
```

### AWS EKS Deployment

```bash
# Create EKS cluster
eksctl create cluster --name securityai-cluster --region us-east-1

# Deploy to EKS
kubectl apply -f backend/k8s/

# Set up ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/aws/deploy.yaml
```

## 📊 Monitoring & Observability

### Metrics

- **Application Metrics**: Request rate, response time, error rate
- **ML Metrics**: Model accuracy, inference latency, drift detection
- **System Metrics**: CPU, memory, disk usage
- **Business Metrics**: Alert volume, resolution time, threat trends

### Logging

- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Centralized Logging**: Elasticsearch for log aggregation
- **Log Retention**: Configurable retention policies

### Health Checks

```bash
# Health check endpoint
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

## 🧪 Testing

### Frontend Tests

```bash
# Run unit tests
npm run test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Run with test database
pytest --env=test
```

### Performance Tests

```bash
# Run load tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## 📈 Performance

### Benchmarks

- **API Response Time**: <100ms (95th percentile)
- **ML Inference**: <50ms per event
- **Throughput**: 10,000 events/second
- **Concurrent Users**: 1,000+ simultaneous connections
- **Data Processing**: 100,000+ events/day

### Optimization

- **Database Indexing**: Optimized indexes on frequently queried fields
- **Caching**: Redis for frequently accessed data
- **Connection Pooling**: Database connection pooling
- **Async Processing**: Non-blocking I/O operations
- **Model Optimization**: ONNX runtime for fast inference

## 🔧 Development

### Code Style

```bash
# Frontend
npm run lint
npm run format

# Backend
cd backend
black app/
isort app/
flake8 app/
mypy app/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement feature**
   - Add tests
   - Update documentation
   - Follow code style guidelines

3. **Create pull request**
   - Include description of changes
   - Link related issues
   - Request code review

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database status
   docker-compose ps
   
   # Check logs
   docker-compose logs postgres
   ```

2. **ML Model Loading Issues**
   ```bash
   # Check model files
   ls -la backend/models/
   
   # Retrain models
   curl -X POST "http://localhost:8000/api/v1/train"
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   ```

### Log Analysis

```bash
# View application logs
docker-compose logs -f backend

# Search for errors
grep "ERROR" logs/app.log

# Monitor real-time logs
tail -f logs/app.log | jq
```

## 📚 Documentation

- **API Documentation**: `http://localhost:8000/docs`
- **Backend Documentation**: [backend/README.md](backend/README.md)
- **Architecture Diagrams**: [docs/architecture.md](docs/architecture.md)
- **Deployment Guide**: [docs/deployment.md](docs/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.securityai.com](https://docs.securityai.com)
- **Issues**: [GitHub Issues](https://github.com/securityai/platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/securityai/platform/discussions)
- **Email**: support@securityai.com

## 🗺️ Roadmap

### Q1 2025
- [ ] Advanced threat hunting capabilities
- [ ] Integration with more threat intelligence feeds
- [ ] Enhanced ML model explainability

### Q2 2025
- [ ] Zero-trust architecture implementation
- [ ] Advanced compliance reporting
- [ ] Machine learning model marketplace

### Q3 2025
- [ ] Multi-tenant architecture
- [ ] Advanced automation and orchestration
- [ ] Integration with cloud-native security tools

### Q4 2025
- [ ] AI-powered threat prediction
- [ ] Advanced behavioral analytics
- [ ] Global threat intelligence sharing

## 🎯 Success Metrics

### Technical Metrics
- **Uptime**: 99.99% availability
- **Performance**: <100ms API response time
- **Scalability**: 100k+ events/day processing
- **Accuracy**: >90% threat detection accuracy

### Business Metrics
- **Time to Detection**: <5 minutes for critical threats
- **False Positive Rate**: <10%
- **Mean Time to Resolution**: <2 hours
- **User Adoption**: >80% of security team

### Compliance Metrics
- **Audit Coverage**: 100% of security events
- **Data Retention**: 90-day hot, 1-year cold storage
- **Encryption**: 100% of data at rest and in transit
- **Access Control**: Role-based access for all users 