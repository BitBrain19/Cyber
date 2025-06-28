#!/usr/bin/env python3
"""
Test script to verify the installation of Enterprise Monitoring Backend
"""

import sys
import importlib
from pathlib import Path

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: {e}")
        return False

def test_core_dependencies():
    """Test core dependencies"""
    print("\n🔍 Testing Core Dependencies:")
    print("=" * 40)
    
    core_modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("websockets", "WebSockets"),
        ("asyncpg", "AsyncPG"),
        ("psycopg2", "psycopg2"),
        ("redis", "Redis"),
        ("jose", "python-jose"),
        ("passlib", "passlib"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("sklearn", "scikit-learn"),
        ("pydantic", "Pydantic"),
        ("httpx", "HTTPX"),
        ("aiohttp", "aiohttp"),
        ("pytest", "pytest"),
        ("dotenv", "python-dotenv"),
        ("requests", "requests"),
    ]
    
    success_count = 0
    for module, name in core_modules:
        if test_import(module, name):
            success_count += 1
    
    return success_count, len(core_modules)

def test_optional_dependencies():
    """Test optional dependencies"""
    print("\n🔍 Testing Optional Dependencies:")
    print("=" * 40)
    
    optional_modules = [
        ("influxdb_client", "InfluxDB Client"),
        ("elasticsearch", "Elasticsearch"),
        ("kafka", "Kafka"),
        ("confluent_kafka", "Confluent Kafka"),
        ("pyspark", "PySpark"),
        ("prometheus_client", "Prometheus Client"),
        ("structlog", "Structlog"),
        ("sentry_sdk", "Sentry SDK"),
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("xgboost", "XGBoost"),
        ("mlflow", "MLflow"),
        ("onnxruntime", "ONNX Runtime"),
        ("shap", "SHAP"),
        ("pyod", "PyOD"),
        ("statsmodels", "Statsmodels"),
        ("prophet", "Prophet"),
        ("networkx", "NetworkX"),
        ("torch_geometric", "PyTorch Geometric"),
        ("dgl", "DGL"),
        ("kubernetes", "Kubernetes"),
        ("stix2", "STIX2"),
        ("taxii2client", "TAXII2 Client"),
        ("pybreaker", "PyBreaker"),
    ]
    
    success_count = 0
    for module, name in optional_modules:
        if test_import(module, name):
            success_count += 1
    
    return success_count, len(optional_modules)

def test_app_structure():
    """Test if the app structure is correct"""
    print("\n🔍 Testing Application Structure:")
    print("=" * 40)
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/api/v1/api.py",
        "app/api/v1/endpoints/auth.py",
        "app/api/v1/endpoints/monitor.py",
        "app/api/v1/endpoints/alerts.py",
        "app/services/ml_pipeline.py",
        "app/services/data_pipeline.py",
    ]
    
    success_count = 0
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
            success_count += 1
        else:
            print(f"❌ {file_path} (missing)")
    
    return success_count, len(required_files)

def test_configuration():
    """Test configuration loading"""
    print("\n🔍 Testing Configuration:")
    print("=" * 40)
    
    try:
        from app.core.config import settings
        print("✅ Configuration loaded successfully")
        print(f"   Project Name: {settings.PROJECT_NAME}")
        print(f"   API Version: {settings.API_V1_STR}")
        print(f"   Environment: {settings.ENVIRONMENT}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Enterprise Monitoring Backend - Installation Test")
    print("=" * 60)
    
    # Test Python version
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
    
    # Test core dependencies
    core_success, core_total = test_core_dependencies()
    
    # Test optional dependencies
    opt_success, opt_total = test_optional_dependencies()
    
    # Test app structure
    struct_success, struct_total = test_app_structure()
    
    # Test configuration
    config_success = test_configuration()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 40)
    print(f"Core Dependencies: {core_success}/{core_total}")
    print(f"Optional Dependencies: {opt_success}/{opt_total}")
    print(f"Application Structure: {struct_success}/{struct_total}")
    print(f"Configuration: {'✅' if config_success else '❌'}")
    
    total_tests = core_total + opt_total + struct_total + 1
    total_success = core_success + opt_success + struct_success + (1 if config_success else 0)
    
    print(f"\nOverall: {total_success}/{total_tests} tests passed")
    
    if core_success == core_total and struct_success == struct_total and config_success:
        print("\n🎉 Core installation is successful!")
        print("You can now run the application with:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        
        if opt_success < opt_total:
            print(f"\n⚠️  {opt_total - opt_success} optional dependencies are missing.")
            print("You can install them with:")
            print("   pip install -e .[ml]    # For ML/AI features")
            print("   pip install -e .[full]  # For all enterprise features")
        
        return True
    else:
        print("\n❌ Installation has issues. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 