from contextlib import asynccontextmanager

from fastapi import FastAPI

from internal.application.routers import handlers
from internal.logger.log_middleware import LogMiddleware


# OS signals handling
resource = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing resources...")
    resource["message"] = "Initialized"
    yield
    print("Cleaning up resources...")
    resource.clear()

# entry point
app = FastAPI(lifespan=lifespan, docs_url='/docs')
app.add_middleware(LogMiddleware)
handlers(app)

# root endpoint
@app.get("/")
async def root():
    return {"message": resource.get("message", "Resource not initialized")}