import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="debug")
