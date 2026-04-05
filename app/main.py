# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
import httpx
from app.config import settings
from app.api.auth_routes import router as auth_router  # Import OAuth routes
from app.api.github_routes import router as github_router
from app.utils.errors import (
    github_api_error_handler,
    validation_error_handler,
    generic_error_handler
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## GitHub Cloud Connector
    
    ### Authentication
    - `GET /api/v1/auth/login` - Get GitHub login URL
    - `GET /api/v1/auth/oauth/callback` - OAuth callback endpoint
    - `GET /api/v1/auth/status` - Check session status
    
    ### GitHub Operations (use after authentication)
    - `GET /api/v1/github/repos` - List your repositories
    - `POST /api/v1/github/issues/create` - Create an issue
    - `GET /api/v1/github/issues/list` - List issues
    - `POST /api/v1/github/pulls/create` - Create pull request (BONUS)
    - `GET /api/v1/github/commits` - List commits
    """
)

# Register error handlers
app.add_exception_handler(httpx.HTTPStatusError, github_api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Register OAuth routes
app.include_router(auth_router)
app.include_router(github_router)
# Existing routes...
@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}",
        "authentication_methods": {
            "pat": bool(settings.GITHUB_PAT),
            "oauth": bool(settings.GITHUB_CLIENT_ID)
        },
        "docs": "/docs",
        "oauth_login": "/api/v1/auth/login"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}