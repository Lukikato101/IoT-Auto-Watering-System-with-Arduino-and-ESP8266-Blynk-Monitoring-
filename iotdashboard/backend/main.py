import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, Field

from database import engine, SessionLocal, get_db
from models import Base, SensorData

# === CONFIGURATION ===
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CREATE DATABASE TABLES ===
Base.metadata.create_all(bind=engine)
logger.info("Database tables initialized")

# === FASTAPI APP INITIALIZATION ===
app = FastAPI(
    title="IoT Watering System API",
    description="REST API for soil moisture monitoring and irrigation control",
    version="1.0.0"
)

# === CORS MIDDLEWARE ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

logger.info(f"CORS enabled for origins: {ALLOWED_ORIGINS}")


# === PYDANTIC MODELS ===
class SensorInput(BaseModel):
    """Incoming sensor data validation model."""
    moisture: int = Field(
        ...,
        ge=0,
        le=1023,
        description="Soil moisture reading (0-1023 from analog sensor)"
    )

    class Config:
        json_schema_extra = {
            "example": {"moisture": 650}
        }


class SensorOutput(BaseModel):
    """Sensor data response model."""
    id: int
    moisture: int
    timestamp: datetime

    class Config:
        from_attributes = True


class SensorHistoryItem(BaseModel):
    """Historical sensor data model."""
    id: int
    value: int
    time: str  # ISO format timestamp

    class Config:
        from_attributes = True


# === ENDPOINTS ===

@app.get(
    "/",
    tags=["Health"],
    summary="Health check endpoint"
)
def health_check():
    """Verify API and database connectivity."""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": ENVIRONMENT
    }


@app.post(
    "/sensor",
    response_model=SensorOutput,
    status_code=status.HTTP_201_CREATED,
    tags=["Sensor Data"],
    summary="Record new sensor reading"
)
def record_sensor_data(
    data: SensorInput,
    db: Session = Depends(get_db)
):
    """Record a new soil moisture sensor reading.
    
    Args:
        data: SensorInput containing moisture value (0-1023)
        db: Database session (injected)
    
    Returns:
        SensorOutput: Saved sensor record with ID and timestamp
    
    Raises:
        HTTPException: If database operation fails
    """
    try:
        new_record = SensorData(moisture=data.moisture)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        logger.info(f"Sensor data recorded: ID={new_record.id}, Moisture={data.moisture}")
        return new_record
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error recording sensor data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save sensor data"
        )



@app.get(
    "/sensor/latest",
    response_model=Optional[SensorOutput],
    tags=["Sensor Data"],
    summary="Get latest sensor reading"
)
def get_latest_sensor_data(db: Session = Depends(get_db)):
    """Retrieve the most recent soil moisture reading.
    
    Returns:
        SensorOutput: Latest sensor record, or None if no data exists
    """
    try:
        latest = db.query(SensorData).order_by(desc(SensorData.timestamp)).first()
        
        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sensor data available"
            )
        
        logger.info(f"Latest sensor data retrieved: ID={latest.id}")
        return latest
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest sensor data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sensor data"
        )


@app.get(
    "/sensor/history",
    response_model=List[SensorHistoryItem],
    tags=["Sensor Data"],
    summary="Get historical sensor data"
)
def get_sensor_history(
    limit: int = Query(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of records to return"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip (pagination)"
    ),
    hours: Optional[int] = Query(
        default=None,
        ge=1,
        le=730,
        description="Limit results to last N hours (optional)"
    ),
    db: Session = Depends(get_db)
) -> List[SensorHistoryItem]:
    """Retrieve historical soil moisture data with pagination.
    
    Args:
        limit: Max records to return (1-10000, default 100)
        offset: Pagination offset (default 0)
        hours: Filter to last N hours (optional)
        db: Database session (injected)
    
    Returns:
        List[SensorHistoryItem]: Historical sensor records
    """
    try:
        query = db.query(SensorData).order_by(desc(SensorData.timestamp))
        
        # Optional time filter
        if hours:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(SensorData.timestamp >= time_threshold)
        
        # Apply pagination
        total_count = query.count()
        data = query.offset(offset).limit(limit).all()
        
        logger.info(f"History retrieved: {len(data)} records from {total_count} total")
        
        return [
            SensorHistoryItem(
                id=item.id,
                value=item.moisture,
                time=item.timestamp.isoformat() if item.timestamp else None
            )
            for item in data
        ]
    
    except Exception as e:
        logger.error(f"Error retrieving sensor history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sensor history"
        )


@app.get(
    "/sensor/stats",
    tags=["Sensor Data"],
    summary="Get sensor statistics"
)
def get_sensor_statistics(
    hours: int = Query(
        default=24,
        ge=1,
        le=730,
        description="Time window in hours for statistics"
    ),
    db: Session = Depends(get_db)
):
    """Calculate sensor statistics (min, max, average) over time period.
    
    Args:
        hours: Time window in hours (default 24)
        db: Database session (injected)
    
    Returns:
        Dictionary with min, max, avg, and count statistics
    """
    try:
        from sqlalchemy import func
        
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        stats = db.query(
            func.min(SensorData.moisture).label("min_moisture"),
            func.max(SensorData.moisture).label("max_moisture"),
            func.avg(SensorData.moisture).label("avg_moisture"),
            func.count(SensorData.id).label("sample_count")
        ).filter(SensorData.timestamp >= time_threshold).first()
        
        return {
            "period_hours": hours,
            "min_moisture": stats.min_moisture or 0,
            "max_moisture": stats.max_moisture or 0,
            "avg_moisture": round(float(stats.avg_moisture) if stats.avg_moisture else 0, 2),
            "sample_count": stats.sample_count or 0
        }
    
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate statistics"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)