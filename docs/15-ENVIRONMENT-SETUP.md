# Developer & Environment Setup Guide
## Autonomous AI Agent for Enterprise Task Automation

**Document Version:** 1.0.0  
**Status:** Approved  
**Target Environment:** Linux / macOS / Windows  

---

## 1. System Prerequisites

Before configuring the project, verify that the following dependencies are installed:
- **Python 3.11+** (`python3 --version` or `python --version`)
- **Git** (`git --version`)
- **Google Cloud Console Account** (for Gmail API & OAuth 2.0 Credentials)
- **Google AI Studio Account** (for Gemini API Key)

---

## 2. Google Cloud Platform (GCP) & Gmail API Setup

To enable programmatic email dispatch via Gmail API:

### Step 1: Create a GCP Project
1. Navigate to [Google Cloud Console](https://console.cloud.google.com/).
2. Click **Select a project** $\rightarrow$ **New Project**.
3. Name your project (e.g. `autonomous-ai-agent-mvp`) and click **Create**.

### Step 2: Enable the Gmail API
1. In the GCP Console search bar, search for **Gmail API**.
2. Click **Enable**.

### Step 3: Configure the OAuth Consent Screen
1. Go to **APIs & Services** $\rightarrow$ **OAuth consent screen**.
2. Select User Type: **External** $\rightarrow$ Click **Create**.
3. Fill in required fields:
   - **App name:** `Autonomous AI Agent`
   - **User support email:** `<your_email@gmail.com>`
   - **Developer contact information:** `<your_email@gmail.com>`
4. Click **Save and Continue**.
5. Under **Scopes**, click **Add or Remove Scopes** and add:
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.compose`
   - `https://www.googleapis.com/auth/userinfo.email`
6. Under **Test Users**, add your personal Gmail address for testing.
7. Click **Save and Continue**.

### Step 4: Create OAuth 2.0 Client Credentials
1. Go to **APIs & Services** $\rightarrow$ **Credentials**.
2. Click **Create Credentials** $\rightarrow$ **OAuth client ID**.
3. Select **Application type:** `Desktop app` (or `Web application` with redirect URI `http://localhost:8501`).
4. Set Name: `AI Agent Desktop Client` $\rightarrow$ Click **Create**.
5. Click **Download JSON** $\rightarrow$ Rename the downloaded file to `credentials.json`.
6. Place `credentials.json` in the project root directory.

---

## 3. Local Development Setup

### Step 1: Clone the Repository & Create Virtual Environment

```bash
# Clone the repository
git clone <repo-url>
cd "automomous ai for task aotomation"

# Create virtual environment with Python 3.11
python3 -m venv venv

# Activate virtual environment
# On Linux / macOS:
source venv/bin/activate

# On Windows (Command Prompt):
# venv\Scripts\activate.bat
# On Windows (PowerShell):
# venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```ini
# --- LLM API Credentials ---
GEMINI_API_KEY=your_google_gemini_api_key_here
LLM_MODEL_NAME=gemini-1.5-flash
LLM_TEMPERATURE=0.2

# --- Google OAuth 2.0 Config ---
GOOGLE_CLIENT_SECRETS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json

# --- Application & Storage Config ---
DATABASE_URL=sqlite:///./tasks.db
LOG_LEVEL=INFO
APP_ENV=development
```

---

## 4. Running the Application

### 4.1 Launch Streamlit Web Application

```bash
streamlit run app.py
```
The interface will automatically open at `http://localhost:8501`.

### 4.2 Run Test Suites & Quality Checks

```bash
# Run unit and integration tests
pytest

# Run code linter
ruff check .

# Run type checker
mypy .
```

---

## 5. Troubleshooting Common Setup Issues

| Issue | Root Cause | Solution |
|---|---|---|
| `AttributeError: module 'google.auth' has no attribute...` | Conflicting Google auth packages | Run `pip install --upgrade google-api-python-client google-auth-oauthlib` |
| `Access Blocked: App has not completed verification` | OAuth Consent Screen is in "Testing" mode | Ensure your Gmail address is added under **Test Users** in GCP OAuth consent screen. |
| `FileNotFoundError: credentials.json` | Missing OAuth client file | Ensure `credentials.json` downloaded from GCP is located in the project root. |
| `Port 8501 already in use` | Another Streamlit instance is running | Run on alternate port: `streamlit run app.py --server.port 8502` |
