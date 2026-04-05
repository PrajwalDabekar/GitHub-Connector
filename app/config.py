# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration settings for the application"""
    
    
    # GitHub OAuth (BONUS)
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_API_BASE: str = "https://api.github.com"
    
    # App Configuration
    APP_NAME: str = "GitHub Cloud Connector"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # OAuth URLs
    GITHUB_OAUTH_AUTHORIZE_URL: str = "https://github.com/login/oauth/authorize"
    GITHUB_OAUTH_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
    
    def validate(self):
        """Check if auth method is configured"""
        has_oauth = bool(self.GITHUB_CLIENT_ID and self.GITHUB_CLIENT_SECRET)
        
        
        if has_oauth:
            print(f"✅ OAuth configured with Client ID: {self.GITHUB_CLIENT_ID[:10]}...")
        

# Create instance
settings = Settings()
settings.validate()