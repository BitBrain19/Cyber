#!/usr/bin/env python3
"""
Full SecurityAI Backend Runner
This script starts the complete backend with all services
"""
import uvicorn
import sys
import os
import time
import subprocess
import requests
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_service_health(url, service_name, timeout=30):
    """Check if a service is healthy"""
    print(f"🔍 Checking {service_name} at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 401, 403]:  # Accept various success codes
                print(f"✅ {service_name} is healthy")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for {service_name}...")
        time.sleep(2)
    
    print(f"❌ {service_name} is not responding after {timeout} seconds")
    return False

def check_docker_services():
    """Check if Docker services are running"""
    services = [
        ("http://localhost:5432", "PostgreSQL"),
        ("http://localhost:6379", "Redis"),
        ("http://localhost:8086/health", "InfluxDB"),
        ("http://localhost:9200/_cluster/health", "Elasticsearch"),
        ("http://localhost:9092", "Kafka")
    ]
    
    all_healthy = True
    for url, service_name in services:
        if not check_service_health(url, service_name):
            all_healthy = False
    
    return all_healthy

def start_docker_services():
    """Start Docker services using docker-compose"""
    print("🐳 Starting Docker services...")
    try:
        # Check if docker-compose.yml exists
        if not Path("docker-compose.yml").exists():
            print("❌ docker-compose.yml not found")
            return False
        
        # Start services
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ Docker services started successfully")
            return True
        else:
            print(f"❌ Failed to start Docker services: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Docker or docker-compose not found. Please install Docker Desktop.")
        return False
    except Exception as e:
        print(f"❌ Error starting Docker services: {e}")
        return False

def main():
    """Main function to start the full backend"""
    print("🚀 SecurityAI Full Backend Startup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        try:
            with open("env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ .env file created")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return
    
    # Start Docker services
    if not start_docker_services():
        print("⚠️  Continuing without Docker services (some features may not work)")
    else:
        # Wait for services to be healthy
        print("⏳ Waiting for services to be ready...")
        time.sleep(10)
        
        if not check_docker_services():
            print("⚠️  Some services are not healthy, but continuing...")
    
    print("\n🎯 Starting SecurityAI Backend...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("=" * 50)
    
    # Start the backend
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 