#!/usr/bin/env python3
"""
Full Stack SecurityAI Startup Script
This script starts all backend services and the frontend
"""
import subprocess
import sys
import os
import time
import requests
import threading
from pathlib import Path

def run_command(command, description, cwd=None, shell=False):
    """Run a command and return the result"""
    print(f"🚀 {description}...")
    try:
        if shell:
            result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        else:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_service(url, service_name, timeout=30):
    """Check if a service is responding"""
    print(f"🔍 Checking {service_name} at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 401, 403]:
                print(f"✅ {service_name} is responding")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
    
    print(f"❌ {service_name} is not responding")
    return False

def start_backend_services():
    """Start backend services using Docker Compose"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Start Docker services
    if not run_command(["docker-compose", "up", "-d"], "Starting Docker services", cwd=backend_dir):
        print("⚠️  Docker services failed to start, continuing...")
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(15)
    
    # Check service health
    services = [
        ("http://localhost:5432", "PostgreSQL"),
        ("http://localhost:6379", "Redis"),
        ("http://localhost:8086/health", "InfluxDB"),
        ("http://localhost:9200/_cluster/health", "Elasticsearch"),
    ]
    
    healthy_services = 0
    for url, service_name in services:
        if check_service(url, service_name):
            healthy_services += 1
    
    print(f"📊 {healthy_services}/{len(services)} services are healthy")
    return healthy_services > 0

def start_backend():
    """Start the FastAPI backend"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    env_example = backend_dir / "env.example"
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, "r") as src, open(env_file, "w") as dst:
            dst.write(src.read())
    
    # Install backend dependencies
    if not run_command(["python", "-m", "pip", "install", "-r", "requirements.txt"], 
                      "Installing backend dependencies", cwd=backend_dir):
        print("⚠️  Some dependencies may not be installed")
    
    # Start the backend
    print("🎯 Starting SecurityAI Backend...")
    backend_process = subprocess.Popen(
        ["python", "run_full.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for backend to start
    time.sleep(10)
    
    # Check if backend is responding
    if check_service("http://localhost:8000/health", "Backend API", timeout=30):
        print("✅ Backend is running at http://localhost:8000")
        return backend_process
    else:
        print("❌ Backend failed to start")
        backend_process.terminate()
        return None

def start_frontend():
    """Start the React frontend"""
    # Check if package.json exists
    if not Path("package.json").exists():
        print("❌ Frontend package.json not found")
        return None
    
    # Install frontend dependencies
    if not run_command(["npm", "install"], "Installing frontend dependencies"):
        print("⚠️  Frontend dependencies may not be installed")
    
    # Start the frontend
    print("🎨 Starting SecurityAI Frontend...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for frontend to start
    time.sleep(10)
    
    # Check if frontend is responding
    if check_service("http://localhost:5173", "Frontend", timeout=30):
        print("✅ Frontend is running at http://localhost:5173")
        return frontend_process
    else:
        print("❌ Frontend failed to start")
        frontend_process.terminate()
        return None

def main():
    """Main function to start the full stack"""
    print("🚀 SecurityAI Full Stack Startup")
    print("=" * 50)
    
    # Start backend services
    print("\n🐳 Starting Backend Services...")
    start_backend_services()
    
    # Start backend
    print("\n🔧 Starting Backend...")
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        return
    
    # Start frontend
    print("\n🎨 Starting Frontend...")
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        return
    
    print("\n🎉 Full Stack is Running!")
    print("=" * 50)
    print("📖 Backend API Docs: http://localhost:8000/docs")
    print("🔍 Backend Health: http://localhost:8000/health")
    print("🎨 Frontend: http://localhost:5173")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("=" * 50)
    print("Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        # Stop Docker services
        backend_dir = Path("backend")
        if backend_dir.exists():
            run_command(["docker-compose", "down"], "Stopping Docker services", cwd=backend_dir)
        
        print("👋 All services stopped")

if __name__ == "__main__":
    main() 