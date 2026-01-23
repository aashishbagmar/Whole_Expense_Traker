
# AI-Powered Personal Finance Tracker

An AI-driven platform for modern personal finance management — combining voice input, receipt scanning, machine learning, and predictive analytics to help users take control of their financial future.

## Architecture Overview

This project uses a microservice architecture:

```
Frontend (Vite/React, deployed on Vercel)
	 ↓
Backend (Django REST API, deployed on Render)
	 ├──> ML Service (FastAPI, deployed on Render)
	 └──> Report Service (FastAPI, deployed on Render)
```

- **All API URLs are set via environment variables.**
- **Frontend uses `VITE_API_BASE_URL` for all API calls.**
- **Backend calls ML and Report services via HTTP using environment-configured URLs.**

---

## Deployment

- **Frontend:** Deployed on [Vercel](https://vercel.com/)
- **Backend, ML Service, Report Service:** Deployed on [Render](https://render.com/)

---

## Environment Variables

- **Frontend (Vercel):**
	- Set `VITE_API_BASE_URL` to your Render backend URL (e.g., `https://your-backend-service.onrender.com`).
	- Configure this in the Vercel dashboard under Project Settings → Environment Variables.

- **Backend (Render):**
	- Set environment variables for ML and Report service URLs (e.g., `ML_SERVICE_URL`, `REPORT_SERVICE_URL`) to the respective Render service URLs.
	- Configure these in the Render dashboard under Environment settings for each service.

---

## Example URLs

- **Frontend (Vercel):** `https://your-frontend-app.vercel.app`
- **Backend (Render):** `https://your-backend-service.onrender.com`
- **ML Service (Render):** `https://your-ml-service.onrender.com`
- **Report Service (Render):** `https://your-report-service.onrender.com`

---

## Quick Start

1. Deploy backend, ML, and report services to Render. Note the URLs Render provides for each service.
2. Set the ML and Report service URLs as environment variables in your backend Render service.
3. Deploy the frontend to Vercel. Set `VITE_API_BASE_URL` in Vercel to your backend Render URL.
4. Visit your Vercel frontend URL to use the app.

