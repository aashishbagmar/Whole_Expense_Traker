# Requirements Files Structure

## ✅ Current Structure (Production Ready)

```
backend/
  ├── requirements.txt              ✅ Backend dependencies ONLY
  └── requirements-backend-only.txt ℹ️  Backup copy (can be removed)

ml-service/
  └── requirements.txt              ✅ ML dependencies ONLY
```

---

## Backend Dependencies (`backend/requirements.txt`)

**Lightweight web service - NO ML libraries**

- Django, DRF, JWT authentication
- Celery, Redis (task queue)
- PostgreSQL driver
- HTTP client (requests) for calling ML service
- Analytics libraries (reportlab, matplotlib, xhtml2pdf)
- Payment integration (razorpay)

**Size:** ~150MB (vs original 800MB with ML)

---

## ML Service Dependencies (`ml-service/requirements.txt`)

**ML inference service - Heavy libraries**

- FastAPI, Uvicorn (web framework)
- scikit-learn, numpy (ML libraries)
- joblib (model serialization)
- Pydantic (validation)

**Size:** ~600MB

---

## Deployment Benefits

### ✅ Railway / Render / Fly.io
Each service has its own `requirements.txt` in its root directory, which these platforms expect.

### ✅ Docker
```dockerfile
# Backend Dockerfile
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# ML Service Dockerfile  
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
```

### ✅ GitHub Actions CI/CD
```yaml
# Backend workflow
- name: Install dependencies
  run: |
    cd backend
    pip install -r requirements.txt

# ML workflow
- name: Install dependencies
  run: |
    cd ml-service
    pip install -r requirements.txt
```

---

## Migration Notes

### Old Structure (Deprecated) ❌
```
backend/
  ├── requirements.txt           # Mixed ML + Backend
  ├── requirements-ml.txt        # ML only
  └── requirements-backend-only.txt  # Backend only
```

### Why Changed?
- **Confusing:** 3 files with unclear purposes
- **Deployment issues:** PaaS platforms expect single requirements.txt
- **Best practice:** Each service = one requirements.txt

---

## Cleanup (Optional)

You can safely remove the backup file:
```powershell
Remove-Item "backend\requirements-backend-only.txt"
```

The main `backend/requirements.txt` is now the authoritative source.
