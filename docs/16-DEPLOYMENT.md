# Deployment & Operations Guide
## Autonomous AI Agent for Enterprise Task Automation

**Document Version:** 1.0.0  
**Status:** Approved  
**Targets:** Docker / Linux Server / Streamlit Community Cloud  

---

## 1. Deployment Topologies

The application supports three production deployment topologies:

```mermaid
graph TD
    subgraph Topology 1: Local / On-Premise
        LocalHost[Local Desktop Python Run]
    end

    subgraph Topology 2: Containerized (Docker)
        DockerHost[Docker Engine / Compose]
        ContainerApp[Streamlit Agent Container]
        VolumeMount[(SQLite & Logs Volume)]
        DockerHost --> ContainerApp
        ContainerApp --> VolumeMount
    end

    subgraph Topology 3: Cloud Hosted
        CloudRunner[Cloud VM / Render / AWS EC2]
        ReverseProxy[Nginx / SSL Termination]
        CloudApp[Agent App Instance]
        CloudRunner --> ReverseProxy
        ReverseProxy --> CloudApp
    end
```

---

## 2. Docker Containerization Specification

### 2.1 `Dockerfile` Specification

```dockerfile
# Multi-stage lightweight Python runtime
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8501

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests
COPY requirements.txt .

# Install Python packages
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application source code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose Streamlit default port
EXPOSE 8501

# Healthcheck configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch command
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2.2 `docker-compose.yml` Specification

```yaml
version: '3.8'

services:
  autonomous-agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: enterprise_ai_agent
    restart: unless-stopped
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./token.json:/app/token.json
    environment:
      - DATABASE_URL=sqlite:////app/data/tasks.db
      - LOG_LEVEL=INFO
```

---

## 3. Production Hardening & Operations Checklist

1. **OAuth Redirect Port Management:** For headless cloud containers, configure Google OAuth with explicit Web Application Redirect URIs (e.g., `https://your-domain.com/oauth2callback`).
2. **Persistent Storage Mounts:** Ensure `/data` (for SQLite database) and `/logs` are mounted to persistent host volumes or managed block storage.
3. **Database Backup Strategy:** Schedule daily automated SQLite backups using SQLite's online backup API:
   ```bash
   sqlite3 /app/data/tasks.db ".backup '/app/data/backups/tasks_$(date +%Y%m%d).db'"
   ```
4. **Log Rotation:** Keep maximum log file retention at 14 days with 50MB per chunk via Loguru rotation policies.
5. **Resource Limits:**
   - **Minimum CPU:** 1 vCPU
   - **Minimum Memory:** 1.5 GB RAM
   - **Network:** Outbound HTTPS (Port 443) access to `*.googleapis.com`.
