from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from database.connection import engine, Base
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Pytrade API",
    description="API for investment platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router, prefix="/api")


# Health Check
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Pytrade API Operational"}


@app.get("/healthcheck", tags=["system"])
async def healthcheck():
    """Endpoint to test API status"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
