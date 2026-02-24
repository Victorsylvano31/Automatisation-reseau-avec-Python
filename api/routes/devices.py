from fastapi import APIRouter
from db.models import SessionLocal, DeviceState

router = APIRouter()

@router.get("/")
def get_all_devices():
    """Get status of all devices from the cached DB state."""
    db = SessionLocal()
    devices = db.query(DeviceState).all()
    db.close()
    return devices
