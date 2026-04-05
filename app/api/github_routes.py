# app/api/github_routes.py
from fastapi import APIRouter, HTTPException, Query
from app.services.github_service import GitHubService
from app.api.auth_routes import token_store  # Import the session storage

router = APIRouter(prefix="/api/v1/github", tags=["GitHub Operations"])

# Helper function to get GitHub service from session
async def get_github_service(session_id: str) -> GitHubService:
    """Extract token from session and create GitHubService"""
    if session_id not in token_store:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    access_token = token_store[session_id]["access_token"]
    return GitHubService(access_token)


# ============================================
# REPOSITORY OPERATIONS
# ============================================

@router.get("/repos")
async def list_my_repos(
    session_id: str = Query(..., description="Your session ID from OAuth login"),
    per_page: int = Query(30, ge=1, le=100, description="Number of repos to return")
):
    """
    List all repositories for the authenticated user.
    
    Use Case: AI tool needs to scan all repos for code analysis
    """
    github = await get_github_service(session_id)
    repos = await github.get_repos(per_page=per_page)
    
    return {
        "count": len(repos),
        "repositories": [
            {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "private": repo["private"],
                "url": repo["html_url"],
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo["stargazers_count"]
            }
            for repo in repos
        ]
    }


@router.get("/repos/{owner}/{repo_name}")
async def get_repo_details(
    owner: str,
    repo_name: str,
    session_id: str = Query(..., description="Your session ID")
):
    """
    Get detailed information about a specific repository.
    
    Use Case: AI tool needs to understand repo structure before analyzing
    """
    github = await get_github_service(session_id)
    
    # We need to add this method to github_service.py
    # For now, let's make a direct call
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo_name}",
            headers=github.headers
        )
        response.raise_for_status()
        repo = response.json()
        
        return {
            "name": repo["name"],
            "full_name": repo["full_name"],
            "description": repo.get("description"),
            "language": repo.get("language"),
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "open_issues": repo["open_issues_count"],
            "default_branch": repo["default_branch"],
            "url": repo["html_url"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"]
        }


# ============================================
# ISSUE OPERATIONS
# ============================================

@router.post("/issues/create")
async def create_issue(
    session_id: str = Query(..., description="Your session ID"),
    owner: str = Query(..., description="Repository owner (username or org)"),
    repo: str = Query(..., description="Repository name"),
    title: str = Query(..., min_length=1, max_length=256, description="Issue title"),
    body: str = Query("", description="Issue description/body"),
    labels: str = Query("", description="Comma-separated labels, e.g., 'bug,urgent'")
):
    """
    Create a new issue in a repository.
    
    Use Case: AI tool finds a bug → automatically creates issue
    """
    github = await get_github_service(session_id)
    
    # Convert comma-separated labels to list
    labels_list = [label.strip() for label in labels.split(",") if label.strip()]
    
    issue = await github.create_issue(
        owner=owner,
        repo=repo,
        title=title,
        body=body,
        labels=labels_list
    )
    
    return {
        "success": True,
        "issue": {
            "number": issue["number"],
            "title": issue["title"],
            "url": issue["html_url"],
            "state": issue["state"],
            "created_at": issue["created_at"]
        },
        "message": f"Issue #{issue['number']} created successfully!"
    }


@router.get("/issues/list")
async def list_issues(
    session_id: str = Query(..., description="Your session ID"),
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    state: str = Query("open", regex="^(open|closed|all)$", description="Issue state"),
    per_page: int = Query(30, ge=1, le=100)
):
    """
    List issues from a repository.
    
    Use Case: AI tool checks existing issues before creating duplicates
    """
    github = await get_github_service(session_id)
    
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            headers=github.headers,
            params={"state": state, "per_page": per_page}
        )
        response.raise_for_status()
        issues = response.json()
        
        return {
            "count": len(issues),
            "issues": [
                {
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "url": issue["html_url"],
                    "created_at": issue["created_at"],
                    "user": issue["user"]["login"]
                }
                for issue in issues
            ]
        }




# ============================================
# COMMIT OPERATIONS
# ============================================

@router.get("/commits")
async def list_commits(
    session_id: str = Query(...),
    owner: str = Query(...),
    repo: str = Query(...),
    branch: str = Query("main", description="Branch name"),
    per_page: int = Query(30, ge=1, le=100)
):
    """
    List commits from a repository.
    
    Use Case: AI tool analyzes recent changes to understand codebase
    """
    github = await get_github_service(session_id)
    
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            headers=github.headers,
            params={"sha": branch, "per_page": per_page}
        )
        response.raise_for_status()
        commits = response.json()
        
        return {
            "count": len(commits),
            "commits": [
                {
                    "sha": commit["sha"][:7],
                    "message": commit["commit"]["message"].split("\n")[0],
                    "author": commit["commit"]["author"]["name"],
                    "date": commit["commit"]["author"]["date"],
                    "url": commit["html_url"]
                }
                for commit in commits
            ]
        }