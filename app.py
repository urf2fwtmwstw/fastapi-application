from contextlib import asynccontextmanager
from datetime import UTC

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from dependencies import get_dependency, initialize_dependencies
from scheduled_jobs import create_scheduled_jobs

resources = {}


# OS signals handling
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing resources...")
    await initialize_dependencies(resources)
    jobstores = {"default": MemoryJobStore()}
    scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=UTC)
    await create_scheduled_jobs(scheduler, await get_dependency("report_service", resources["services"]))
    resources["message"] = "Initialized"
    scheduler.start()
    yield
    print("Cleaning up resources...")
    resources.clear()
    scheduler.shutdown()


# entry point
app = FastAPI(lifespan=lifespan, docs_url="/docs")


# root endpoint
@app.get("/")
async def root():
    return {"message": resources.get("message", "Resource not initialized")}
