# app/services/auth_service.py
import httpx
from fastapi import HTTPException, status
from app.config import settings

class GitHubAuthService:
    """Handles GitHub OAuth 2.0 flow"""
    
    @staticmethod
    def get_login_url() -> str:
        """
        Generate the URL where users should be sent to login with GitHub.
        
        Returns a URL like:
        https://github.com/login/oauth/authorize?client_id=xxx&scope=repo,user
        """
        # The scopes (permissions) we're requesting
        scopes = ["repo", "user"]
        
        # Build the authorization URL
        auth_url = (
            f"{settings.GITHUB_OAUTH_AUTHORIZE_URL}"
            f"?client_id={settings.GITHUB_CLIENT_ID}"
            f"&scope={','.join(scopes)}"
            f"&redirect_uri=http://localhost:8000/api/v1/auth/oauth/callback"
        )
        
        return auth_url
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> dict:
        """
        Exchange the temporary 'code' for a permanent access token.
        
        GitHub gives us a code (temporary, single-use)
        We exchange it for an access_token (long-lasting)
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.GITHUB_OAUTH_TOKEN_URL,
                headers={
                    "Accept": "application/json"  # Tell GitHub to return JSON
                },
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": "http://localhost:8000/api/v1/auth/oauth/callback"
                }
            )
            
            # Check if request failed
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange code: {response.text}"
                )
            
            # Parse the response
            token_data = response.json()
            
            # Check for errors
            if "error" in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"OAuth error: {token_data['error']} - {token_data.get('error_description', '')}"
                )
            
            return token_data
    
    @staticmethod
    async def get_user_info(access_token: str) -> dict:
        """Get the authenticated user's information using the token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch user info"
                )
            
            return response.json()