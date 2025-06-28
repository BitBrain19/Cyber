@echo off
echo 🚀 Enterprise Monitoring Backend Installation
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Upgrade pip
echo.
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Failed to upgrade pip
    pause
    exit /b 1
)

REM Install setuptools
echo.
echo 🔄 Installing setuptools...
python -m pip install --upgrade setuptools wheel
if errorlevel 1 (
    echo ❌ Failed to install setuptools
    pause
    exit /b 1
)

REM Install core dependencies
echo.
echo 🔄 Installing core dependencies...
python -m pip install -r requirements-minimal.txt
if errorlevel 1 (
    echo ❌ Failed to install core dependencies
    pause
    exit /b 1
)

echo.
echo 📦 Optional Dependencies:
echo 1. Development tools (black, isort, flake8, mypy)
echo 2. ML/AI libraries (torch, transformers, xgboost, etc.)
echo 3. Full enterprise features (all databases, monitoring, etc.)
echo 4. Skip optional dependencies

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo 🔄 Installing development dependencies...
    python -m pip install -e .[dev]
) else if "%choice%"=="2" (
    echo 🔄 Installing ML/AI dependencies...
    python -m pip install -e .[ml]
) else if "%choice%"=="3" (
    echo 🔄 Installing full enterprise dependencies...
    python -m pip install -e .[full]
) else (
    echo ⏭️ Skipping optional dependencies
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo.
    echo 📝 Creating sample .env file...
    (
        echo # Database Configuration
        echo DATABASE_URL=postgresql://user:password@localhost:5432/monitoring_db
        echo REDIS_URL=redis://localhost:6379/0
        echo.
        echo # Security
        echo SECRET_KEY=your-secret-key-here-change-in-production
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo.
        echo # API Configuration
        echo API_V1_STR=/api/v1
        echo PROJECT_NAME=Enterprise Monitoring System
        echo BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
        echo.
        echo # Monitoring
        echo PROMETHEUS_PORT=9090
        echo SENTRY_DSN=your-sentry-dsn-here
        echo.
        echo # External Services
        echo INFLUXDB_URL=http://localhost:8086
        echo ELASTICSEARCH_URL=http://localhost:9200
        echo KAFKA_BOOTSTRAP_SERVERS=localhost:9092
        echo.
        echo # ML/AI Configuration
        echo MLFLOW_TRACKING_URI=http://localhost:5000
        echo MODEL_REGISTRY_PATH=./models
    ) > .env
    echo ✅ Sample .env file created
    echo ⚠️  Please update the .env file with your actual configuration values
) else (
    echo ✅ .env file already exists
)

echo.
echo 🎉 Installation completed successfully!
echo.
echo 📋 Next steps:
echo 1. Update the .env file with your configuration
echo 2. Set up your databases (PostgreSQL, Redis)
echo 3. Run the application: python -m app.main
echo 4. Access the API documentation at: http://localhost:8000/docs

pause 