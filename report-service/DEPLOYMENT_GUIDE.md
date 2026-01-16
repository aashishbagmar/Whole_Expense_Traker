# Report Service Deployment Guide

## Overview

The Report Service is deployed as a **separate Railway project**, independent from the main Django backend. This ensures:
- Light-weight main backend (faster builds and deployments)
- Reliable PDF/Chart generation
- Independent scaling
- Easy maintenance and updates

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- pip or pipenv
- Virtual environment tool (venv)

### Installation Steps

1. **Navigate to report-service directory:**
```bash
cd report-service
```

2. **Create and activate virtual environment:**
```bash
# Windows (PowerShell)
python -m venv venv-report
.\venv-report\Scripts\activate

# macOS/Linux
python3 -m venv venv-report
source venv-report/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
# Copy example config
cp .env.example .env

# Edit .env if needed
# DEBUG=False
# LOG_LEVEL=INFO
# PORT=8001
```

5. **Run development server:**
```bash
# Development (with auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Or production-like
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

6. **Verify it's running:**
```bash
# In another terminal
curl http://localhost:8001/health

# Expected output:
# {"status":"ok","service":"Report Service","version":"1.0.0",...}
```

---

## Docker Deployment

### Build Docker Image

```bash
# From report-service directory
docker build -t report-service:latest .

# Tag for registry
docker tag report-service:latest myregistry/report-service:latest
```

### Run Docker Container

```bash
# Development
docker run -p 8001:8001 \
  -e DEBUG=true \
  -e LOG_LEVEL=DEBUG \
  report-service:latest

# Production
docker run -p 8001:8001 \
  -e DEBUG=false \
  -e PORT=8001 \
  -e BACKEND_BASE_URL=https://backend-api.railway.app \
  report-service:latest
```

### Docker Compose (Local Development)

Create `docker-compose.yml` in workspace root:

```yaml
version: '3.8'

services:
  report-service:
    build:
      context: ./report-service
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - PORT=8001
      - BACKEND_BASE_URL=http://localhost:9000
    volumes:
      - ./report-service/templates:/app/templates
    networks:
      - expense-tracker

  backend:
    # ... existing backend configuration
    networks:
      - expense-tracker

networks:
  expense-tracker:
    driver: bridge
```

Start all services:
```bash
docker-compose up
```

---

## Railway Deployment

### Step 1: Prepare Your Repository

Ensure the report-service folder is committed to Git:
```bash
git add report-service/
git commit -m "Add Report Service microservice"
git push
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Click "Create New Project"
3. Connect your GitHub repository
4. Select "Deploy from GitHub"

### Step 3: Configure Project Settings

1. **Add Environment:**
   - Click "Variables"
   - Add the following environment variables:

```env
# Service Configuration
DEBUG=false
LOG_LEVEL=INFO
PORT=8001

# Backend Integration
BACKEND_BASE_URL=https://your-backend-api.railway.app

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend.vercel.app,https://your-backend-api.railway.app

# Chart Settings
CHART_DPI=100
```

2. **Configure Service Root:**
   - Go to "Settings" → "Deploy"
   - Set "Root Directory" to `report-service`
   - Set "Start Command" to empty (uses Dockerfile CMD)

### Step 4: Configure Dockerfile

The included Dockerfile handles both development and production:

```dockerfile
# Production deployment
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001"]

# Development deployment (if DEBUG=true)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Step 5: Deploy

1. **Trigger Deployment:**
   - Railway automatically deploys on Git push
   - Or manually trigger in Railway dashboard

2. **Monitor Deployment:**
   - Watch logs in Railway dashboard
   - Wait for "Successfully deployed" message

3. **Verify Deployment:**
   ```bash
   curl https://your-report-service.railway.app/health
   ```

### Step 6: Update Backend Configuration

In main backend's Django settings, update:

```python
REPORT_SERVICE_URL = os.environ.get(
    'REPORT_SERVICE_URL',
    'https://your-report-service.railway.app'
)
```

Or set environment variable in backend Railway project:
```env
REPORT_SERVICE_URL=https://your-report-service.railway.app
```

---

## Environment Variables Reference

### Service Configuration
```env
# Enable debug mode (development only)
DEBUG=false

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Service port (Railway will use 8001)
PORT=8001

# Service name and version (usually don't change)
SERVICE_NAME=Report Service
SERVICE_VERSION=1.0.0
```

### Backend Integration
```env
# Main backend API URL
BACKEND_BASE_URL=https://your-backend-api.railway.app

# Request timeout in seconds
# (Increase for slow connections or large reports)
# Not exposed as env var, but can be configured in config.py
```

### CORS Configuration
```env
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://example.com

# These are pre-configured defaults in config.py:
# - http://localhost:3000 (Next.js default)
# - http://localhost:5173 (Vite default)
# - https://expense-tracker-frontend.vercel.app (Production frontend)
# - https://expense-tracker-api.railway.app (Backend)
```

### Chart Configuration
```env
# DPI (dots per inch) for chart rendering
# Higher = better quality but slower
# Valid range: 50-300 (default: 100)
CHART_DPI=100
```

### Logging
```env
# Log level for the application
# DEBUG: Most verbose, includes all debug info
# INFO: General information messages
# WARNING: Warning and error messages
# ERROR: Error messages only
LOG_LEVEL=INFO
```

---

## Integration with Main Backend

### 1. Update Django Settings

In `backend/backend/settings.py`:
```python
REPORT_SERVICE_URL = os.environ.get('REPORT_SERVICE_URL', 'http://localhost:8001')
REPORT_SERVICE_TIMEOUT = int(os.environ.get('REPORT_SERVICE_TIMEOUT', 30))
REPORT_SERVICE_ENABLED = os.environ.get('REPORT_SERVICE_ENABLED', 'true').lower() == 'true'
```

### 2. Add to Django Requirements (if separate venv)
The backend requirements.txt no longer needs:
- ~~reportlab~~
- ~~xhtml2pdf~~
- ~~matplotlib~~
- ~~pillow~~

But DOES include:
- `requests` (for HTTP calls to Report Service)

### 3. Use Report Client in Views

```python
from analytics.report_client import get_report_client

# In your view/API endpoint
report_client = get_report_client()

# Check health
if not report_client.health_check():
    return Response({'error': 'Report service unavailable'}, status=503)

# Generate PDF
pdf_bytes = report_client.generate_pdf(report_data)
```

---

## Monitoring & Troubleshooting

### Check Service Status

```bash
# Health check
curl https://your-report-service.railway.app/health

# Service info
curl https://your-report-service.railway.app/info
```

### View Logs

**In Railway Dashboard:**
1. Select Report Service project
2. Click "Logs" tab
3. View real-time logs

**Command Line:**
```bash
# If using Railway CLI
railway logs
```

### Common Issues

#### 1. "Service Unavailable" Error

**Cause:** Report Service not running or unreachable

**Solution:**
- Check Railway deployment status
- Verify REPORT_SERVICE_URL environment variable
- Check network connectivity

```bash
# Test connectivity
curl https://your-report-service.railway.app/health
```

#### 2. Timeout Errors

**Cause:** Report Service takes too long to respond

**Solution:**
- Increase REPORT_SERVICE_TIMEOUT in Django settings
- Optimize chart generation (reduce DPI, image size)
- Check Report Service logs for performance issues

```python
# In Django settings
REPORT_SERVICE_TIMEOUT = 60  # Increase to 60 seconds
```

#### 3. Chart Generation Fails

**Cause:** Issues with matplotlib or pillow dependencies

**Solution:**
- Check Report Service logs for specific error
- Ensure all system dependencies are installed in Dockerfile
- Verify chart data format

#### 4. PDF Contains No Charts

**Cause:** Chart generation succeeded but PDF template issue

**Solution:**
- Verify template exists in report-service/templates
- Check chart base64 encoding
- Review PDF generation logs

### Debug Mode

Enable detailed logging:

1. Set environment variable:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

2. Redeploy to Railway

3. Check logs for detailed error information:
```bash
# In Railway dashboard, view verbose logs
```

### Performance Monitoring

Monitor key metrics:

```python
# In report_client.py, add timing logs
import time

start = time.time()
pdf_bytes = report_client.generate_pdf(data)
duration = time.time() - start
logger.info(f"PDF generation took {duration:.2f}s")
```

Expected performance:
- Charts: 500ms - 2.5s each
- PDF: 2s - 5s total

---

## Scaling Strategy

### Horizontal Scaling

**Option 1: Multiple Instances (Recommended)**
- Railway supports multiple instances
- Requests load-balanced automatically
- Each instance handles independent requests

**Option 2: Increase Instance Resources**
- Increase RAM/CPU allocation in Railway
- Better for CPU-intensive chart generation

### Configuration for High Load

```env
# In Railway dashboard, set:
# - Memory: 512MB - 1GB
# - CPU: 0.5 - 1.0 shared
# - Instances: 2-4 (with auto-scaling)

# In production settings:
DEBUG=false
LOG_LEVEL=WARNING
CHART_DPI=100
```

### Caching Strategy (Backend)

```python
# In backend analytics views
from django.core.cache import cache

cache_key = f"report_pdf_{user_id}_{month}_{year}"
pdf_bytes = cache.get(cache_key)

if not pdf_bytes:
    pdf_bytes = report_client.generate_pdf(data)
    cache.set(cache_key, pdf_bytes, timeout=86400)  # 24 hours
```

---

## Updates & Maintenance

### Updating Report Service

1. **Make changes locally:**
```bash
cd report-service
# Make your changes
# Test locally: uvicorn main:app --reload
```

2. **Commit and push:**
```bash
git add report-service/
git commit -m "Update report service: add new chart type"
git push
```

3. **Railway auto-deploys:**
- New deployment automatically triggered
- Old instance runs until new one is ready
- Seamless zero-downtime deployment

### Updating Dependencies

```bash
# Update requirements.txt
pip install --upgrade reportlab matplotlib pillow xhtml2pdf

# Export to requirements.txt
pip freeze > report-service/requirements.txt

# Commit
git add report-service/requirements.txt
git commit -m "Update dependencies"
git push
```

### Version Management

Current version: **1.0.0**

Update in `config.py`:
```python
SERVICE_VERSION = "1.0.1"  # Increment version
```

---

## Backup & Recovery

### No Database Needed

Report Service doesn't use a database, so no backup needed.

### Code Recovery

All code is version-controlled in Git:
```bash
# View deployment history
git log --oneline report-service/

# Rollback if needed
git revert <commit-hash>
git push
```

---

## Security Considerations

### 1. CORS Configuration

Update CORS_ORIGINS for production:
```env
# Secure CORS - only allow your frontend and backend
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-backend.railway.app

# Don't allow localhost in production
```

### 2. Network Security

- Report Service doesn't handle authentication (no user data)
- No sensitive information stored
- Calls back to backend for data validation if needed

### 3. Environment Variables

Never commit sensitive data:
```bash
# ✓ Good: Use Railway environment variables
REPORT_SERVICE_URL=https://your-service.railway.app

# ✗ Bad: Don't hardcode in code
REPORT_SERVICE_URL = "https://your-service.railway.app"
```

---

## Cost Optimization

### Railway Pricing

- Free tier: Limited resources, suitable for testing
- Pay-as-you-go: $0.10/GB/hour (reasonable for typical usage)

### Optimization Tips

1. **Resource Allocation:**
   - Start with 256MB RAM
   - Increase only if needed
   - Monitor actual usage in Railway dashboard

2. **Instance Count:**
   - Start with 1 instance
   - Scale to 2-3 during peak hours
   - Use Railway's auto-scaling if available

3. **Request Optimization:**
   - Reduce chart DPI if quality acceptable
   - Limit transaction list in reports
   - Cache frequently generated reports

### Estimated Monthly Cost

- 1 instance, 256MB RAM: ~$5-10/month
- 2 instances, 512MB RAM: ~$15-20/month
- 4 instances, 1GB RAM: ~$30-40/month

---

## Next Steps

1. **Test locally** with `uvicorn main:app --reload`
2. **Deploy to Railway** using this guide
3. **Update backend** REPORT_SERVICE_URL
4. **Monitor logs** for first week
5. **Optimize** based on actual performance

---

## Support

For issues or questions:
1. Check logs in Railway dashboard
2. Review API_CONTRACT.md for endpoint details
3. Check this deployment guide's troubleshooting section
4. Review main backend's analytics/report_client.py integration
