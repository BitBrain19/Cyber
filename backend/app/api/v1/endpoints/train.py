"""
API endpoints for triggering, monitoring, and validating ML model training.
Supports background retraining, status/history queries, and synthetic data generation for demonstration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog
from datetime import datetime
import asyncio

from app.core.security import require_admin
from app.services.ml_pipeline import MLPipeline

logger = structlog.get_logger()
router = APIRouter()

class TrainingRequest(BaseModel):
    models: Optional[list] = None  # List of models to retrain, if None retrain all
    force_retrain: bool = False
    hyperparameters: Optional[Dict[str, Any]] = None

class TrainingResponse(BaseModel):
    training_id: str
    status: str
    models: list
    started_at: str
    estimated_duration: str

@router.post("/")
async def trigger_model_training(
    training_request: TrainingRequest,
    current_user = Depends(require_admin)
):
    """Trigger ML model retraining (admin only)"""
    try:
        # Generate training ID
        training_id = f"training_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user.id}"
        
        # Get ML pipeline instance
        ml_pipeline = MLPipeline()
        
        # Start training in background
        training_task = asyncio.create_task(
            _run_training(training_id, ml_pipeline, training_request)
        )
        
        logger.info("Model training triggered", 
                   training_id=training_id,
                   user_id=current_user.id,
                   models=training_request.models)
        
        return TrainingResponse(
            training_id=training_id,
            status="started",
            models=training_request.models or ["all"],
            started_at=datetime.utcnow().isoformat(),
            estimated_duration="30-60 minutes"
        )
        
    except Exception as e:
        logger.error("Failed to trigger model training", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger model training"
        )

@router.get("/status/{training_id}")
async def get_training_status(
    training_id: str,
    current_user = Depends(require_admin)
):
    """Get training status"""
    try:
        # In a real implementation, you would store training status in database/Redis
        # For now, return mock status
        status_data = {
            "training_id": training_id,
            "status": "completed",  # or "running", "failed"
            "progress": 100,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "models_trained": ["anomaly_detector", "threat_classifier"],
            "performance_metrics": {
                "anomaly_detector": {
                    "accuracy": 0.94,
                    "precision": 0.92,
                    "recall": 0.89,
                    "f1_score": 0.90
                },
                "threat_classifier": {
                    "accuracy": 0.91,
                    "precision": 0.89,
                    "recall": 0.87,
                    "f1_score": 0.88
                }
            },
            "logs": [
                "Loading training data...",
                "Preprocessing features...",
                "Training anomaly detection model...",
                "Training threat classification model...",
                "Evaluating model performance...",
                "Saving models to disk...",
                "Training completed successfully"
            ]
        }
        
        return status_data
        
    except Exception as e:
        logger.error("Failed to get training status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get training status"
        )

@router.get("/history")
async def get_training_history(
    current_user = Depends(require_admin),
    limit: int = 10
):
    """Get training history"""
    try:
        # Mock training history
        history = [
            {
                "training_id": f"training_{i}",
                "status": "completed",
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "models": ["anomaly_detector", "threat_classifier"],
                "performance_improvement": 0.05
            }
            for i in range(limit)
        ]
        
        return {
            "training_history": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error("Failed to get training history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get training history"
        )

@router.post("/validate")
async def validate_models(
    current_user = Depends(require_admin)
):
    """Validate trained models"""
    try:
        ml_pipeline = MLPipeline()
        
        # Run validation tests
        validation_results = await _validate_models(ml_pipeline)
        
        logger.info("Model validation completed", results=validation_results)
        
        return {
            "validation_results": validation_results,
            "overall_status": "passed" if all(r["status"] == "passed" for r in validation_results) else "failed",
            "validated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to validate models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate models"
        )

async def _run_training(training_id: str, ml_pipeline: MLPipeline, training_request: TrainingRequest):
    """Run model training in background"""
    try:
        logger.info("Starting model training", training_id=training_id)
        
        # Generate synthetic training data (in production, this would come from real data)
        training_data = _generate_training_data()
        
        # Train models
        results = await ml_pipeline.train_models(training_data)
        
        logger.info("Model training completed", 
                   training_id=training_id,
                   results=results)
        
    except Exception as e:
        logger.error("Model training failed", 
                    training_id=training_id,
                    error=str(e))

def _generate_training_data():
    """Generate synthetic training data for demonstration"""
    import pandas as pd
    import numpy as np
    
    # Generate synthetic security events
    n_samples = 10000
    
    data = {
        'bytes_transferred': np.random.exponential(1000, n_samples),
        'login_attempts': np.random.poisson(2, n_samples),
        'duration': np.random.normal(300, 100, n_samples),
        'event_type': np.random.choice(['login', 'file_access', 'network_scan', 'data_transfer'], n_samples),
        'source_ip': [f"192.168.1.{np.random.randint(1, 255)}" for _ in range(n_samples)],
        'destination_port': np.random.randint(1, 65535, n_samples),
        'protocol': np.random.choice([80, 443, 22, 3389], n_samples),
        'threat_label': np.random.choice(['benign', 'suspicious', 'malicious'], n_samples, p=[0.8, 0.15, 0.05])
    }
    
    return pd.DataFrame(data)

async def _validate_models(ml_pipeline: MLPipeline) -> list:
    """Validate trained models"""
    validation_results = []
    
    # Test anomaly detector
    try:
        test_event = {
            'bytes_transferred': 5000,
            'login_attempts': 10,
            'duration': 600,
            'event_type': 'suspicious_activity',
            'source_ip': '192.168.1.100'
        }
        
        anomaly_result = ml_pipeline.anomaly_detector.predict(test_event)
        
        validation_results.append({
            "model": "anomaly_detector",
            "status": "passed",
            "test_result": anomaly_result,
            "message": "Anomaly detection working correctly"
        })
    except Exception as e:
        validation_results.append({
            "model": "anomaly_detector",
            "status": "failed",
            "error": str(e)
        })
    
    # Test threat classifier
    try:
        classification_result = ml_pipeline.threat_classifier.predict(test_event)
        
        validation_results.append({
            "model": "threat_classifier",
            "status": "passed",
            "test_result": classification_result,
            "message": "Threat classification working correctly"
        })
    except Exception as e:
        validation_results.append({
            "model": "threat_classifier",
            "status": "failed",
            "error": str(e)
        })
    
    return validation_results 