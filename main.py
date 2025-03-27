from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from internal.application.routers import handlers
from internal.logger import logger



# OS signals handling
resource = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing resources...")
    resource["msg"] = "Initialized"
    yield
    print("Cleaning up resources...")
    resource.clear()


# entry point
app = FastAPI(lifespan=lifespan, docs_url='/docs')

handlers(app)

# root endpoint
@app.get("/")
async def root():
    logger.info('Root endpoint accessed', service="Spending Tracker")
    return {"message": resource.get("msg", "Resource not initialized")}

#logging requests
@app.middleware('http')
async def log_request_middleware(request: Request, call_next):
    response = await call_next(request)
    logger.info("Request completed",service="Spending Tracker")
    return response