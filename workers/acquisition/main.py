from fastapi import FastAPI
from api.v1.endpoints import router as acquisition_router

app = FastAPI()

app.include_router(acquisition_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=51190)
