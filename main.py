from internal.logger import logger
from internal.config.config import config
from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager


# OS signals handling
resource = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing resources...")
    resource["msg"] = "Initialized"
    yield
    print("Cleaning up resources...")
    resource.clear()



app = FastAPI(lifespan=lifespan)

#logging requests
@app.middleware('http')
async def log_request_middleware(request: Request, call_next):
    response = await call_next(request)
    logger.info("Request completed",service="Spending Tracker")
    return response


#main
@app.get("/")
async def root():
    logger.info('Root endpoint accessed', service="Spending Tracker")
    return {"message": resource.get("msg", "Resource not initialized")}