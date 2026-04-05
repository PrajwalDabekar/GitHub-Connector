# app/api/auth_routes.py
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from app.services.auth_service import GitHubAuthService
from app.config import settings
from app.services.github_service import GitHubService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Simple in-memory storage for tokens (for demo only!)
# In production, use a database with expiration!
token_store = {}

@router.get("/login")
async def oauth_login():
    """
    Step 1: Redirect user to GitHub for authentication.
    
    User clicks this link → Gets sent to GitHub login page
    """
    login_url = GitHubAuthService.get_login_url()
    
    # Return the URL - the frontend should redirect to this
    return {
        "login_url": login_url,
        "message": "Redirect user to this URL to authenticate with GitHub"
    }

@router.get("/login/redirect")
async def oauth_login_redirect():
    """
    Alternative: Automatically redirect the user.
    
    Visiting this endpoint automatically sends user to GitHub.
    """
    login_url = GitHubAuthService.get_login_url()
    return RedirectResponse(url=login_url)

@router.get("/oauth/callback")
async def oauth_callback(code: str = Query(...)):
    """
    Step 2: GitHub redirects here after user approves.
    
    GitHub sends a 'code' parameter. We exchange it for a token.
    
    Example URL after redirect:
    http://localhost:8000/api/v1/auth/oauth/callback?code=abc123
    """
    # Exchange the code for an access token
    token_data = await GitHubAuthService.exchange_code_for_token(code)
    
    access_token = token_data.get("access_token")
    token_type = token_data.get("token_type", "bearer")
    scope = token_data.get("scope", "")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")
    
    # Get user info using the token
    user_info = await GitHubAuthService.get_user_info(access_token)
    
    # Store token temporarily (in production, use session/DB)
    session_id = f"user_{user_info['id']}"
    token_store[session_id] = {
        "access_token": access_token,
        "user": user_info,
        "scopes": scope
    }
    
    return {
        "message": "Authentication successful!",
        "session_id": session_id,
        "user": {
            "login": user_info["login"],
            "name": user_info.get("name"),
            "avatar_url": user_info.get("avatar_url")
        },
        "token_preview": access_token[:20] + "...",
        "scopes": scope
    }

@router.get("/status")
async def auth_status(session_id: str = Query(...)):
    """Check if a session is still valid"""
    if session_id in token_store:
        session = token_store[session_id]
        return {
            "authenticated": True,
            "user": session["user"]["login"],
            "scopes": session["scopes"]
        }
    return {
        "authenticated": False,
        "message": "Session not found or expired"
    }

@router.post("/logout")
async def logout(session_id: str = Query(...)):
    """Logout - remove the session"""
    if session_id in token_store:
        del token_store[session_id]
        return {"message": "Logged out successfully"}
    return {"message": "Session not found"}

# Add to the existing auth_routes.py

@router.get("/me")
async def get_authenticated_user(session_id: str = Query(...)):
    """
    Get the authenticated user's info using their session.
    This demonstrates using the OAuth token to call GitHub.
    """
    # Get token from store
    if session_id not in token_store:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    session = token_store[session_id]
    #print(session)
    access_token = session["access_token"]
    #print(access_token)
    # Use GitHub service with OAuth token
    github_service = GitHubService(access_token)
    
    user_info = await github_service.get_user()
    repos = await github_service.get_repos(per_page=5)
    
    return {
        "user": user_info,
        "recent_repos": [{"name": repo["name"], "url": repo["html_url"]} for repo in repos[:5]]
    }