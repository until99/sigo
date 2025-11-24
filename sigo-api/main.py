from fastapi import FastAPI
from views.auth_view import router_auth

app = FastAPI()

app.router.include_router(router_auth, prefix="/v1", tags=["auth"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
