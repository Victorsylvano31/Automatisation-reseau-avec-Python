from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    job_type = Column(String, index=True) # e.g. BACKUP, DEPLOY
    status = Column(String, default="PENDING")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class JobResult(Base):
    __tablename__ = "job_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, index=True)
    device_name = Column(String, index=True)
    status = Column(String)
    log_output = Column(Text, nullable=True)

class DeviceState(Base):
    __tablename__ = "device_states"
    hostname = Column(String, primary_key=True)
    is_online = Column(Boolean, default=False)
    last_backup_date = Column(DateTime, nullable=True)
    software_version = Column(String, nullable=True)

# Pour les besoins du projet, on utilise SQLite par défaut 
engine = create_engine("sqlite:///nre_platform.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
