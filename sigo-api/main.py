from fastapi import FastAPI
from dotenv import load_dotenv
import os

from views.auth_view import router_auth
from views.user_view import router_user
from database import engine, Base


load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SIGO API",
    description="API for SIGO application",
    version="1.0.0",
)

app.include_router(router_auth, prefix="/v1", tags=["Authentication"])
app.include_router(router_user, prefix="/v1", tags=["Users"])


@app.get("/", tags=["Health Check"])
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "message": "SIGO API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("SERVER_PORT", 8000)),
        reload=True,
    )
