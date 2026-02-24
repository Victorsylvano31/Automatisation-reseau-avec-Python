from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import jobs, devices

app = FastAPI(
    title="NRE Platform V2 API",
    description="API for Modern Network Automation Platform",
    version="1.0.0"
)

# CORS — Allow the Vite dev server (port 5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
