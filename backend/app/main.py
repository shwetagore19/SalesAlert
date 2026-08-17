import os
import sys

# Ensure project root directory is in sys.path for direct python backend/app/main.py execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    HAS_APSCHEDULER = True
except ImportError:
    HAS_APSCHEDULER = False

from backend.app.db.database import init_db, SessionLocal
from backend.app.routes import dashboard, sales, alerts, reports, intelligence
from backend.app.routes.reports import trigger_daily_update

app = FastAPI(
    title="AI Sales Intelligence & Daily Business Newspaper API",
    description="End-to-end business intelligence engine, verified KPI calculator, rule alert detector, and LLM daily report generator.",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(dashboard.router)
app.include_router(sales.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(intelligence.router)

@app.on_event("startup")
def on_startup():
    print("[Startup] Initializing Database & Seeding Data...")
    init_db()
    
    # Initialize background scheduler for daily update if configured
    if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
        scheduler = BackgroundScheduler()
        # Schedule every day at 19:00 (7:00 PM)
        scheduler.add_job(
            func=scheduled_daily_run,
            trigger="cron",
            hour=19,
            minute=0
        )
        scheduler.start()
        print("[Scheduler] APScheduler daily automated reporting job started.")

def scheduled_daily_run():
    print("[Scheduler] Running daily automated update...")
    db = SessionLocal()
    try:
        trigger_daily_update({}, db)
    finally:
        db.close()

# Serve compiled React Dashboard UI
dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
assets_dir = os.path.join(dist_dir, "assets")

if os.path.exists(assets_dir):
    from fastapi.staticfiles import StaticFiles
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/")
def serve_index():
    index_file = os.path.join(dist_dir, "index.html")
    if os.path.exists(index_file):
        from fastapi.responses import FileResponse
        return FileResponse(index_file)
    return {
        "status": "online",
        "system": "AI-Powered Daily Sales Intelligence & Business Reporting System",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
