from fastapi import FastAPI
import uvicorn
import logging

logger = logging.getLogger('uvicorn.access')

app = FastAPI()



if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=9000, log_config="internal/config/log_conf.yaml")