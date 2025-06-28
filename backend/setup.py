from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements-minimal.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="enterprise-monitoring-backend",
    version="1.0.0",
    author="Enterprise Monitoring Team",
    author_email="team@enterprise-monitoring.com",
    description="Enterprise IT Infrastructure Monitoring System Backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/enterprise-monitoring/backend",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "pytest-cov>=4.1.0",
        ],
        "ml": [
            "xgboost>=2.0.0",
            "torch>=2.1.0",
            "transformers>=4.35.0",
            "mlflow>=2.8.0",
            "onnxruntime>=1.16.0",
            "shap>=0.44.0",
            "pyod>=1.1.0",
            "statsmodels>=0.14.0",
            "prophet>=1.1.0",
            "networkx>=3.2.0",
            "torch-geometric>=2.4.0",
            "dgl>=1.1.0",
        ],
        "full": [
            "influxdb-client>=1.38.0",
            "elasticsearch[async]>=8.11.0",
            "kafka-python>=2.0.0",
            "confluent-kafka>=2.3.0",
            "pyspark>=3.5.0",
            "prometheus-client>=0.19.0",
            "structlog>=23.2.0",
            "sentry-sdk[fastapi]>=1.38.0",
            "python-docx>=1.1.0",
            "reportlab>=4.0.0",
            "openpyxl>=3.1.0",
            "kubernetes>=28.1.0",
            "stix2>=3.0.0",
            "taxii2-client>=2.3.0",
            "pybreaker>=1.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "monitoring-backend=app.main:main",
        ],
    },
) 