# 🚨 FEATURE FREEZE IN EFFECT
# Only stabilization & optimization allowed. Do NOT add new features until further notice.

# SETUP GUIDE - Using Virtual Environments

## ⚠️ Important: Use Separate Virtual Environments

To avoid dependency conflicts, each service should have its own virtual environment.

---

## Quick Setup

### Step 1: Create Virtual Environments (Already Done ✓)

```powershell
# Backend environment
cd "d:\AI Tracking Expenses\backend"
python -m venv venv-backend

# ML Service environment
cd "d:\AI Tracking Expenses\ml-service"
python -m venv venv-ml
```

### Step 2: Activate & Install Dependencies (all services)

#### Terminal 1: Report Service (NEW)
```powershell
cd "d:\AI Tracking Expenses\report-service"
.\venv-report\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 2: ML Service
```powershell
cd "d:\AI Tracking Expenses\ml-service"
.\venv-ml\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Terminal 3: Backend
```powershell
cd "d:\AI Tracking Expenses\backend"
.\venv-backend\Scripts\activate
pip install -r requirements.txt
$env:ML_SERVICE_URL="http://localhost:8000"
$env:REPORT_SERVICE_URL="http://localhost:8001"
python manage.py runserver 9000
```

#### Terminal 4: Frontend
```powershell
cd "d:\AI Tracking Expenses\frontend"
npm install
npm run dev
```

---

## Why Separate Virtual Environments?

**Problem:** Your global Python environment has conflicting packages:
- `dash-extensions`, `langchain`, `mcp` require newer pydantic
- `tensorflow-intel` requires older numpy
- `torchvision` requires specific torch version

**Solution:** Isolate each service's dependencies:
- Backend needs only Django + REST (no ML libraries)
- ML Service needs scikit-learn + FastAPI (no Django)
- No conflicts when isolated

---

## Current Status

✅ Virtual environments created  
⏳ Need to activate and install in clean environments  
⏳ Need to start services  

---

## Next Steps

Open 2 PowerShell terminals and run:

**Terminal 1 (ML Service):**
```powershell
cd "d:\AI Tracking Expenses\ml-service"
.\venv-ml\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 (Backend):**
```powershell
cd "d:\AI Tracking Expenses\backend"
.\venv-backend\Scripts\activate
pip install -r requirements-backend-only.txt
$env:ML_SERVICE_URL="http://localhost:8000"
python manage.py runserver 9000
```

This will give you clean, isolated environments with no conflicts!
