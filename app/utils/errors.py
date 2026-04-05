# app/utils/errors.py
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Union
import httpx
import logging

logger = logging.getLogger(__name__)

async def github_api_error_handler(request: Request, exc: httpx.HTTPStatusError):
    """Handle GitHub API specific errors"""
    status_code = exc.response.status_code
    error_data = exc.response.json() if exc.response.text else {}
    
    # Map GitHub error codes to user-friendly messages
    error_messages = {
        401: "Invalid or expired GitHub token. Please re-authenticate.",
        403: "You don't have permission to perform this action.",
        404: "The requested resource was not found. Check owner/repo names.",
        422: "Validation failed. Check your input data.",
        429: "GitHub API rate limit exceeded. Please try again later."
    }
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_messages.get(status_code, "GitHub API error"),
            "status_code": status_code,
            "details": error_data.get("message", str(exc)),
            "documentation": "https://docs.github.com/en/rest"
        }
    )


async def validation_error_handler(request: Request, exc: Exception):
    """Handle validation errors (invalid input)"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Invalid request",
            "message": str(exc),
            "status_code": 400
        }
    )


async def generic_error_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
    )