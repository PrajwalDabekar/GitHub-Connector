# A production-ready REST API connector for GitHub that provides secure authentication and seamless integration with GitHub's API. Built with FastAPI and Python.

## 🌟 Features

- **🔐 OAuth 2.0 Authentication** - Secure GitHub login flow
- **📁 Repository Management** - List and inspect repositories
- **🐛 Issue Operations** - Create and list issues programmatically
- **📝 Commit History** - Fetch commit logs from any branch
- **📚 Auto-generated Docs** - Interactive Swagger UI at `/docs`

  ## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- GitHub account
- (For OAuth) GitHub OAuth App registered

### Installation

#### 1. Clone the Repository

```
git clone https://github.com/yourusername/github-connector.git
cd github-connector
```

#### 2. Create Virtual Environment

#### Windows
```
python -m venv venv
venv\Scripts\activate
```

#### Mac/Linux
```
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```
pip install -r requirements.txt
```

#### 4. Configure Environment
```
cp .env.example .env
```
Edit .env with your credentials (see Configuration section).

#### 5. Run the Server
```
uvicorn app.main:app --reload --port 8000
```
Visit http://localhost:8000 to verify it's running.

#### ⚙️ Configuration
Environment Variables
Create a .env file with these variables:


#### GitHub OAuth (Recommended for production)
GITHUB_CLIENT_ID=your_oauth_client_id
GITHUB_CLIENT_SECRET=your_oauth_client_secret


#### Application Settings
DEBUG=true
SECRET_KEY=your-secret-key-change-this-in-production
Getting Credentials
OAuth Go to GitHub Settings → Developer settings → OAuth Apps

Click "New OAuth App"

Fill in:

Application name: ```GitHub Connector```

Homepage URL: ```http://localhost:8000```

Authorization callback URL: ```http://localhost:8000/api/v1/auth/oauth/callback```

Copy Client ID and Client Secret to .env


#### 📡 API Endpoints
Base URL
```
http://localhost:8000/api/v1
```

login:
```
http://localhost:8000/api/v1/auth/login
```
Open URL in browser and authorize the application


OR
```
http://localhost:8000/api/v1/auth/login/redirect -> ( It will redirect you to GitHub Auth page)
```
Copy session_id from the callback response

Use session_id in all API calls

Status:
```
http://localhost:8000/api/v1/auth/status?session_id=YOUR_SESSION_ID
```

list Repos:
```
http://localhost:8000/api/v1/github/repos?session_id=YOUR_SESSION_ID
```
Create Issue:
```
http://localhost:8000/api/v1/github/issues/create?session_id=YOUR_SESSION_ID&owner=YOUR_OWNER_NAME&repo=YOUR_REPO_NAME&title=Test%20Issue%20from%20API-3&body=This%20is%20a%20demo&labels=bug,test
```

List Issues:
```
http://localhost:8000/api/v1/github/issues/list?session_id=YOUR_SESSION_ID&owner=YOUR_OWNER_NAME&repo=YOUR_REPO_NAME
```
List Commits:
```
http://localhost:8000/api/v1/github/commits?session_id=YOUR_SESSION_ID&owner=YOUR_OWNER_NAME&repo=YOUR_REPO_NAME
```
Logout:
```
http://localhost:8000/api/v1/auth/logout?session_id=YOUR_SESSION_ID
```

#### 📞 Support

Check the documentation 
```
http://localhost:8000/docs
```
