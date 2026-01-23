# AI-Powered Personal Finance Tracker

An AI-driven platform for modern personal finance management — combining voice input, receipt scanning, machine learning, and predictive analytics to help users take control of their financial future.

## Architecture Overview

This project uses a microservice architecture:

```
Frontend (Vite/React)
	↓
Backend (Django REST API)
	├──> ML Service (FastAPI, HTTP, env-configured URL)
	└──> Report Service (FastAPI, HTTP, env-configured URL)
```

- **All API URLs are set via environment variables.**
- **Frontend uses `VITE_API_BASE_URL` for all API calls.**
- **Backend calls ML and Report services via HTTP using environment-configured URLs.**

## Environment Variables

- **Frontend:** Set `VITE_API_BASE_URL` to your backend URL (e.g., `https://expense-tracker-backend-production.up.railway.app`).
- **Backend:** Set ML and Report service URLs in environment or settings.

