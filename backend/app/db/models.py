from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TrafficFlow(Base):
    __tablename__ = "traffic_flow"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    road_name = Column(String(128), nullable=False, index=True)
    speed = Column(Float, nullable=False)
    congestion_level = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    geometry = Column(JSON, nullable=True)  # Store as list of [lon, lat] pairs or GeoJSON

class TrafficIncident(Base):
    __tablename__ = "traffic_incident"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    type = Column(String(64), nullable=False, index=True)
    description = Column(String(256))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    road_name = Column(String(128), nullable=False, index=True)  # NEW FIELD
