#!/usr/bin/env python3
"""
Installation script for Enterprise Monitoring Backend
This script helps install dependencies in the correct order to avoid conflicts.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )

def install_setuptools():
    """Install/upgrade setuptools"""
    return run_command(
        f"{sys.executable} -m pip install --upgrade setuptools wheel",
        "Installing/upgrading setuptools and wheel"
    )

def install_core_dependencies():
    """Install core dependencies"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements-minimal.txt",
        "Installing core dependencies"
    )

def install_optional_dependencies():
    """Install optional dependencies based on user choice"""
    print("\n📦 Optional Dependencies:")
    print("1. Development tools (black, isort, flake8, mypy)")
    print("2. ML/AI libraries (torch, transformers, xgboost, etc.)")
    print("3. Full enterprise features (all databases, monitoring, etc.)")
    print("4. Skip optional dependencies")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        return run_command(
            f"{sys.executable} -m pip install -e .[dev]",
            "Installing development dependencies"
        )
    elif choice == "2":
        return run_command(
            f"{sys.executable} -m pip install -e .[ml]",
            "Installing ML/AI dependencies"
        )
    elif choice == "3":
        return run_command(
            f"{sys.executable} -m pip install -e .[full]",
            "Installing full enterprise dependencies"
        )
    elif choice == "4":
        print("⏭️ Skipping optional dependencies")
        return True
    else:
        print("❌ Invalid choice, skipping optional dependencies")
        return True

def create_env_file():
    """Create a sample .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Creating sample .env file...")
        env_content = """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/monitoring_db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Enterprise Monitoring System
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Monitoring
PROMETHEUS_PORT=9090
SENTRY_DSN=your-sentry-dsn-here

# External Services
INFLUXDB_URL=http://localhost:8086
ELASTICSEARCH_URL=http://localhost:9200
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# ML/AI Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MODEL_REGISTRY_PATH=./models
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Sample .env file created")
        print("⚠️  Please update the .env file with your actual configuration values")
    else:
        print("✅ .env file already exists")

def main():
    """Main installation function"""
    print("🚀 Enterprise Monitoring Backend Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Upgrade pip
    if not upgrade_pip():
        print("❌ Failed to upgrade pip. Please try manually: python -m pip install --upgrade pip")
        sys.exit(1)
    
    # Install setuptools
    if not install_setuptools():
        print("❌ Failed to install setuptools. Please try manually: python -m pip install --upgrade setuptools wheel")
        sys.exit(1)
    
    # Install core dependencies
    if not install_core_dependencies():
        print("❌ Failed to install core dependencies")
        sys.exit(1)
    
    # Install optional dependencies
    if not install_optional_dependencies():
        print("❌ Failed to install optional dependencies")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update the .env file with your configuration")
    print("2. Set up your databases (PostgreSQL, Redis)")
    print("3. Run the application: python -m app.main")
    print("4. Access the API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 