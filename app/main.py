from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.database.connection import engine, Base, sessionLocal
from app.utils.db_seed import seed_brokers
from app.routes import router

from middlewares import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)


async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sessionLocal() as session:
        await seed_brokers(session)

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

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


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
