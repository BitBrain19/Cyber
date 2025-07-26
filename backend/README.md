# SecurityAI Backend

Enterprise-grade IT infrastructure monitoring and threat detection backend system with AI/ML capabilities.

## 🚀 Features

- **Real-time Monitoring**: WebSocket-based streaming for live dashboard updates
- **AI/ML Pipeline**: Anomaly detection, threat classification, NLP log parsing, and graph analysis
- **Multi-database Architecture**: PostgreSQL, InfluxDB, Elasticsearch, Redis
- **Enterprise Security**: JWT authentication, RBAC, rate limiting, circuit breakers
- **Scalable Architecture**: Kubernetes deployment, auto-scaling, load balancing
- **Compliance Ready**: Audit logging, data encryption, secure APIs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   FastAPI       │
│   (React/Vite)  │◄──►│   (NGINX)       │◄──►│   Backend       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────────────────────────────┐
                       │                                         │
              ┌────────▼────────┐    ┌─────────────┐    ┌────────▼────────┐
              │   PostgreSQL    │    │   InfluxDB  │    │   Elasticsearch │
              │   (Users/Assets)│    │ (Time Series)│    │   (Log Search)  │
              └─────────────────┘    └─────────────┘    └─────────────────┘
                       │                                         │
              ┌────────▼────────┐    ┌─────────────┐    ┌────────▼────────┐
              │     Redis       │    │    Kafka    │    │   ML Pipeline   │
              │   (Cache)       │    │ (Streaming) │    │ (AI/ML Models)  │
              └─────────────────┘    └─────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Kubernetes cluster (for production)
- PostgreSQL 15+
- InfluxDB 2.0+
- Elasticsearch 8.0+
- Redis 7.0+
- Kafka 3.0+

## ��️ Installation

### Quick Start (Recommended)

#### Windows

```bash
# Run the Windows installation script
install.bat
```

#### Linux/macOS

```bash
# Run the Python installation script
python install.py
```

### Manual Installation

#### 1. **Clone the repository**

```bash
git clone <repository-url>
cd backend
```

#### 2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. **Upgrade pip and setuptools**

```bash
python -m pip install --upgrade pip setuptools wheel
```

#### 4. **Install dependencies**

**Option A: Minimal setup (recommended for testing)**

```bash
pip install -r requirements-minimal.txt
```

**Option B: Full setup with all features**

```bash
pip install -r requirements.txt
```

**Option C: Install with extras**

```bash
# Core + Development tools
pip install -e .[dev]

# Core + ML/AI libraries
pip install -e .[ml]

# Core + Full enterprise features
pip install -e .[full]
```

#### 5. **Set up environment variables**

```bash
# The installation script will create a sample .env file
# Edit .env with your configuration
```

#### 6. **Start development services**

```bash
# Use the main docker-compose.yml for development
# (docker-compose.dev.yml does not exist)
docker-compose up -d
```

#### 7. **Run the application**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Troubleshooting

#### Common Issues

1. **setuptools import error**

   ```bash
   python -m pip install --upgrade setuptools wheel
   ```

2. **Python version compatibility**

   - Ensure you're using Python 3.11 or higher
   - Check with: `python --version`

3. **Dependency conflicts**

   - Use the minimal requirements first: `pip install -r requirements-minimal.txt`
   - Then add optional dependencies as needed

4. **Windows-specific issues**

   - Use the `install.bat` script
   - Ensure Visual C++ build tools are installed for some packages

5. **Memory issues with ML packages**
   - Install core dependencies first
   - Install ML packages separately: `pip install -e .[ml]`

### Production Deployment

1. **Build Docker image**

   ```bash
   docker build -t securityai/backend:latest .
   ```

2. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/
   ```

## 🔧 Configuration

### Environment Variables

| Variable                  | Description                          | Default                                |
| ------------------------- | ------------------------------------ | -------------------------------------- |
| `ENVIRONMENT`             | Environment (development/production) | `development`                          |
| `SECRET_KEY`              | JWT secret key                       | `your-secret-key-change-in-production` |
| `POSTGRES_URL`            | PostgreSQL connection string         | `postgresql://user:pass@localhost/db`  |
| `INFLUXDB_TOKEN`          | InfluxDB API token                   | `your-influxdb-token`                  |
| `ELASTICSEARCH_URL`       | Elasticsearch URL                    | `http://localhost:9200`                |
| `REDIS_URL`               | Redis connection string              | `redis://localhost:6379`               |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka servers                        | `localhost:9092`                       |

### Database Setup

1. **PostgreSQL**

   ```sql
   CREATE DATABASE securityai;
   CREATE USER securityai WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE securityai TO securityai;
   ```

2. **InfluxDB**

   ```bash
   # Create organization and bucket
   influx org create -n securityai
   influx bucket create -n security_events -o securityai -r 90d
   ```

3. **Elasticsearch**
   ```bash
   # Create index
   curl -X PUT "localhost:9200/security_logs" -H 'Content-Type: application/json' -d'
   {
     "mappings": {
       "properties": {
         "timestamp": {"type": "date"},
         "source": {"type": "keyword"},
         "message": {"type": "text"}
       }
     }
   }'
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

## 🚀 Deployment

### Docker Compose (Development)

```yaml
# docker-compose.dev.yml
version: "3.8"
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
    depends_on:
      - postgres
      - redis
      - influxdb
      - elasticsearch
      - kafka

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: securityai
      POSTGRES_USER: securityai
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=password
      - DOCKER_INFLUXDB_INIT_ORG=securityai
      - DOCKER_INFLUXDB_INIT_BUCKET=security_events

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

volumes:
  postgres_data:
```

### Kubernetes (Production)

```bash
# Create namespace
kubectl create namespace securityai

# Apply secrets
kubectl apply -f k8s/secrets.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -n securityai
kubectl get services -n securityai
```

## 🧪 Testing

### Unit Tests

```bash
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
# Format code
black app/
isort app/

# Lint code
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
   ls -la models/

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

## 📚 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

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
- **Issues**: [GitHub Issues](https://github.com/securityai/backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/securityai/backend/discussions)
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
