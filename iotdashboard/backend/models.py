from sqlalchemy import Column, Integer, DateTime, Index
from sqlalchemy.sql import func
from datetime import datetime
from database import Base


class SensorData(Base):
    """Soil moisture sensor data model.
    
    Fields:
        id: Unique record identifier
        moisture: Moisture reading (0-1023 from analog sensor)
        timestamp: Record creation timestamp (UTC)
    """

    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    moisture = Column(
        Integer,
        nullable=False,
        index=True,  # Index for faster queries
        comment="Moisture reading from analog sensor (0-1023)"
    )
    timestamp = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        index=True,  # Index for time-based queries
        comment="UTC timestamp of data collection"
    )

    # Create composite index for efficient time-range queries
    __table_args__ = (
        Index('idx_timestamp_desc', 'timestamp'),
    )

    def __repr__(self):
        return f"<SensorData(id={self.id}, moisture={self.moisture}, timestamp={self.timestamp})>"