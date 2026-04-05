# app/services/github_service.py
import httpx
from typing import Dict, Any, Optional

class GitHubService:
    """Service to interact with GitHub API using either PAT or OAuth token"""
    
    def __init__(self, token: str):
        """
        Initialize with a token (either PAT or OAuth access_token)
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def get_user(self) -> Dict:
        """Get authenticated user info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_repos(self, per_page: int = 30) -> list:
        """Get user's repositories"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                params={"per_page": per_page, "sort": "updated"}
            )
            response.raise_for_status()
            return response.json()
    
    async def create_issue(
        self, 
        owner: str, 
        repo: str, 
        title: str, 
        body: str = "",
        labels: list = None
    ) -> Dict:
        """Create an issue in a repository"""
        async with httpx.AsyncClient() as client:
            data = {
                "title": title,
                "body": body,
                "labels": labels or []
            }
            response = await client.post(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()