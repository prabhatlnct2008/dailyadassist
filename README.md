# Daily Ad Agent

An AI-powered Facebook Ads management tool that acts as your personal media buyer. It provides intelligent campaign analysis, creative generation, and automated optimization through a conversational interface.

## Features

- **AI-Powered Chat Interface** - Converse with an intelligent agent that understands Facebook Ads
- **Performance Analysis** - Real-time insights into campaign metrics and trends
- **Creative Generation** - AI-generated ad copy and creative recommendations
- **Campaign Management** - Create, edit, and publish campaigns through chat
- **Safety Guardrails** - Budget limits and policy compliance checks
- **Live Ad Preview** - See Facebook ad mockups before publishing

## Tech Stack

### Backend
- **Framework**: Flask (Python 3.9+)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-JWT-Extended + Google/Facebook OAuth
- **AI/Agents**: LangChain with multi-agent architecture
- **API**: RESTful with Server-Sent Events (SSE) for streaming

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context + React Query
- **Routing**: React Router v6

## Project Structure

```
dailyadassist/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py            # Configuration classes
│   │   ├── models/              # SQLAlchemy models
│   │   ├── api/                 # API blueprints
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Business logic services
│   │   ├── agents/              # LangChain agents
│   │   │   ├── orchestrator.py  # Main agent (routes to sub-agents)
│   │   │   ├── performance_analyst.py
│   │   │   ├── creative_strategist.py
│   │   │   ├── copywriter.py
│   │   │   ├── execution_agent.py
│   │   │   ├── qa_safety_agent.py
│   │   │   └── tools/           # Agent tools
│   │   └── utils/               # Utilities (encryption, helpers)
│   ├── migrations/              # Database migrations
│   ├── requirements.txt
│   └── run.py                   # Entry point
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client modules
│   │   ├── components/          # Shared UI components
│   │   ├── context/             # React context providers
│   │   ├── features/            # Feature modules
│   │   │   ├── auth/            # Login, OAuth callback
│   │   │   ├── onboarding/      # Setup wizard
│   │   │   ├── warroom/         # Main chat + preview interface
│   │   │   └── settings/        # User settings
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── plan.md                      # Architecture specification
├── phases.md                    # Implementation phases
└── README.md
```

---

## Local Development Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   cp .env.example .env  # if exists, or create manually
   ```

   Create `.env` file with:
   ```env
   # Flask
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here-generate-a-random-one

   # Database
   DATABASE_URL=sqlite:///app.db

   # JWT
   JWT_SECRET_KEY=your-jwt-secret-key-here

   # Google OAuth
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret

   # Facebook OAuth
   FACEBOOK_APP_ID=your-facebook-app-id
   FACEBOOK_APP_SECRET=your-facebook-app-secret

   # LLM (OpenAI or Anthropic)
   OPENAI_API_KEY=your-openai-api-key
   # or
   ANTHROPIC_API_KEY=your-anthropic-api-key

   # Frontend URL (for CORS)
   FRONTEND_URL=http://localhost:5173

   # Encryption key for tokens (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
   ENCRYPTION_KEY=your-fernet-encryption-key
   ```

5. **Initialize database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the backend**
   ```bash
   python run.py
   ```

   Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create environment file**

   Create `.env` file:
   ```env
   VITE_API_URL=http://localhost:5000/api
   VITE_GOOGLE_CLIENT_ID=your-google-client-id
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

### Running Both Together

Open two terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
python run.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

---

## Production Deployment

### Backend Deployment (PythonAnywhere)

PythonAnywhere offers free Python hosting perfect for Flask applications.

#### Step 1: Create PythonAnywhere Account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account (or paid for custom domains)

#### Step 2: Upload Code

**Option A: Git Clone (Recommended)**
1. Open a Bash console in PythonAnywhere
2. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/dailyadassist.git
   cd dailyadassist/backend
   ```

**Option B: Manual Upload**
1. Go to Files tab
2. Upload your backend folder as a zip
3. Extract in the console

#### Step 3: Create Virtual Environment

In PythonAnywhere Bash console:
```bash
cd ~/dailyadassist/backend
mkvirtualenv --python=/usr/bin/python3.10 dailyadassist-env
pip install -r requirements.txt
```

#### Step 4: Configure Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Select **Manual configuration** (not Flask)
4. Choose **Python 3.10**

#### Step 5: Configure WSGI

Edit the WSGI configuration file (linked in Web tab):

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/dailyadassist/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-production-secret-key'
os.environ['JWT_SECRET_KEY'] = 'your-jwt-secret'
os.environ['DATABASE_URL'] = 'sqlite:////home/yourusername/dailyadassist/backend/app.db'
os.environ['GOOGLE_CLIENT_ID'] = 'your-google-client-id'
os.environ['GOOGLE_CLIENT_SECRET'] = 'your-google-client-secret'
os.environ['FACEBOOK_APP_ID'] = 'your-facebook-app-id'
os.environ['FACEBOOK_APP_SECRET'] = 'your-facebook-app-secret'
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'
os.environ['FRONTEND_URL'] = 'https://your-frontend-domain.vercel.app'
os.environ['ENCRYPTION_KEY'] = 'your-fernet-encryption-key'

# Import Flask app
from app import create_app
application = create_app('production')
```

#### Step 6: Set Virtual Environment Path

In Web tab, set **Virtualenv** path:
```
/home/yourusername/.virtualenvs/dailyadassist-env
```

#### Step 7: Configure Static Files (Optional)

If serving static files:
- URL: `/static/`
- Directory: `/home/yourusername/dailyadassist/backend/app/static`

#### Step 8: Initialize Database

In Bash console:
```bash
cd ~/dailyadassist/backend
workon dailyadassist-env
flask db upgrade
```

#### Step 9: Reload Web App

Click **Reload** button in Web tab.

Your backend will be available at: `https://yourusername.pythonanywhere.com`

#### PythonAnywhere Tips

- **Free tier limitations**:
  - CPU seconds quota (resets daily)
  - No custom domains
  - Outbound internet restricted to allowlisted sites

- **For Facebook API access** on free tier:
  - Add `graph.facebook.com` to allowlist (Paid accounts only, or use mock data)

- **Scheduled tasks**: Use Tasks tab for background jobs

- **Logs**: Check Error log and Server log in Web tab for debugging

---

### Frontend Deployment (Vercel)

Vercel offers excellent free hosting for React applications.

#### Step 1: Prepare for Production

1. Update `frontend/.env.production`:
   ```env
   VITE_API_URL=https://yourusername.pythonanywhere.com/api
   VITE_GOOGLE_CLIENT_ID=your-google-client-id
   ```

2. Ensure `vite.config.js` is production-ready (already configured)

#### Step 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from frontend directory**
   ```bash
   cd frontend
   vercel
   ```

4. **Follow prompts**:
   - Set up and deploy? `Y`
   - Which scope? Select your account
   - Link to existing project? `N`
   - Project name: `dailyadassist`
   - Directory: `./` (current)
   - Override settings? `N`

5. **Set environment variables**
   ```bash
   vercel env add VITE_API_URL
   # Enter: https://yourusername.pythonanywhere.com/api

   vercel env add VITE_GOOGLE_CLIENT_ID
   # Enter: your-google-client-id
   ```

6. **Deploy to production**
   ```bash
   vercel --prod
   ```

#### Step 3: Deploy via Vercel Dashboard (Alternative)

1. Go to [vercel.com](https://vercel.com)
2. Sign up/Login with GitHub
3. Click **Import Project**
4. Select your repository
5. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. Add environment variables in Settings
7. Click **Deploy**

#### Step 4: Configure Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS as instructed

Your frontend will be available at: `https://dailyadassist.vercel.app` (or custom domain)

---

### Post-Deployment Configuration

#### Update OAuth Redirect URIs

**Google Cloud Console:**
1. Go to APIs & Services → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add authorized redirect URIs:
   - `https://yourusername.pythonanywhere.com/api/auth/google/callback`
   - `https://dailyadassist.vercel.app/auth/callback`

**Facebook Developer Console:**
1. Go to your app settings
2. Add OAuth redirect URIs:
   - `https://yourusername.pythonanywhere.com/api/auth/facebook/callback`
3. Add your domains to "Valid OAuth Redirect URIs"

#### Update CORS Settings

In PythonAnywhere WSGI file, ensure `FRONTEND_URL` matches your Vercel domain:
```python
os.environ['FRONTEND_URL'] = 'https://dailyadassist.vercel.app'
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `FLASK_ENV` | Environment (development/production) | Yes |
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `DATABASE_URL` | SQLite or PostgreSQL URL | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | Yes |
| `FACEBOOK_APP_ID` | Facebook App ID | Yes |
| `FACEBOOK_APP_SECRET` | Facebook App secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key | No* |
| `ANTHROPIC_API_KEY` | Anthropic API key | No* |
| `FRONTEND_URL` | Frontend URL for CORS | Yes |
| `ENCRYPTION_KEY` | Fernet key for token encryption | Yes |

*At least one LLM API key required for AI features

### Frontend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL | Yes |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |

---

## API Endpoints

### Authentication
- `POST /api/auth/google` - Initiate Google OAuth
- `GET /api/auth/google/callback` - Google OAuth callback
- `POST /api/auth/facebook` - Initiate Facebook OAuth
- `GET /api/auth/facebook/callback` - Facebook OAuth callback
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - Logout user

### Users
- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update user profile
- `GET /api/users/me/preferences` - Get preferences
- `PUT /api/users/me/preferences` - Update preferences

### Conversations
- `GET /api/conversations` - List conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations/:id` - Get conversation
- `GET /api/conversations/:id/messages` - Get messages

### Agent
- `POST /api/agent/chat` - Send message (SSE streaming)

### Drafts
- `GET /api/drafts` - List drafts
- `POST /api/drafts` - Create draft
- `PUT /api/drafts/:id` - Update draft
- `POST /api/drafts/:id/publish` - Publish draft

### Performance
- `GET /api/performance/overview` - Account overview
- `GET /api/performance/campaigns` - Campaign metrics
- `GET /api/performance/top-performers` - Top performing ads

---

## Agent Architecture

The application uses a multi-agent system built with LangChain:

```
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator                          │
│              (Senior Media Buyer Persona)                │
│                                                          │
│  Routes requests to specialized sub-agents based on      │
│  user intent and conversation context                    │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Performance  │   │   Creative    │   │   Copywriter  │
│   Analyst     │   │  Strategist   │   │               │
│               │   │               │   │               │
│ Analyzes KPIs │   │ Generates     │   │ Writes ad     │
│ and trends    │   │ creative      │   │ copy with     │
│               │   │ briefs        │   │ char limits   │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   Execution   │   │   QA/Safety   │
│    Agent      │   │    Agent      │
│               │   │               │
│ Creates and   │   │ Validates     │
│ manages       │   │ policy &      │
│ campaigns     │   │ budget limits │
└───────────────┘   └───────────────┘
```

---

## Troubleshooting

### Common Issues

**Backend won't start**
- Check Python version: `python --version` (need 3.9+)
- Verify virtual environment is activated
- Check all dependencies installed: `pip install -r requirements.txt`
- Verify `.env` file exists with all required variables

**Database errors**
- Run migrations: `flask db upgrade`
- If corrupted, delete `app.db` and re-run migrations

**CORS errors in browser**
- Verify `FRONTEND_URL` in backend `.env` matches actual frontend URL
- Check no trailing slash in URLs

**OAuth not working**
- Verify redirect URIs match exactly in Google/Facebook console
- Check client ID and secret are correct
- Ensure HTTPS in production

**Agent not responding**
- Check LLM API key is set (OpenAI or Anthropic)
- Verify API key has credits/quota
- Check server logs for errors

### PythonAnywhere Specific

**"Error loading WSGI application"**
- Check WSGI file syntax
- Verify virtualenv path is correct
- Check error log in Web tab

**"Module not found"**
- Ensure you're in the correct virtualenv
- Re-install requirements: `pip install -r requirements.txt`

**Outbound requests failing (free tier)**
- Facebook API requires paid account or allowlist
- Use mock data for development

### Vercel Specific

**Build failures**
- Check Node version (need 18+)
- Verify `package.json` has correct build script
- Check for TypeScript/ESLint errors

**Environment variables not working**
- Prefix with `VITE_` for client-side access
- Redeploy after adding new variables

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

MIT License - see LICENSE file for details.
