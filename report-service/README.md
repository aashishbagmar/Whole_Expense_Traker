# Report Service 📊

A **dedicated microservice** for PDF and Chart Generation in the Expense Tracker system.

## Overview

The Report Service is a **stateless, lightweight FastAPI application** that handles:
- **Chart Generation** (Pie, Bar, Line charts)
- **PDF Report Generation** (Professional financial reports)
- **Image Embedding** (Charts as base64-encoded images)

This service is **completely independent** from the main Django backend, ensuring:
- ✅ Lightweight backend deployment
- ✅ Reliable PDF/Chart generation
- ✅ Independent scaling
- ✅ Easy maintenance and updates
- ✅ Production-ready reliability

---

## Key Features

### 🎨 Chart Generation
- **Pie Charts**: Expense distribution by category
- **Bar Charts**: Category/time-based comparisons
- **Line Charts**: Trend visualization over time
- **Customizable**: Colors, sizes, DPI, labels

### 📄 PDF Reports
- **Professional Layout**: Clean, readable financial reports
- **Embedded Charts**: Generated charts embedded directly in PDF
- **Rich Data**: Full transaction history with summaries
- **AI Insights**: Intelligent spending observations

### ⚡ Performance
- **Fast Generation**: Charts in 500ms-2.5s, PDFs in 2-5s
- **Stateless**: No session management or database
- **Scalable**: Easy to add instances for load handling
- **Efficient**: Uses base64 encoding for easy transport

---

## Architecture

```
Frontend (React/Vite)
       ↓ (HTTP)
Main Backend (Django)
       ↓ (HTTP)
Report Service (FastAPI)
       ↓
Charts + PDFs (Base64)
```

### Service Responsibilities

| Layer | Responsibility | Does NOT Do |
|-------|---|---|
| **Report Service** | Chart generation, PDF creation | Database access, authentication |
| **Django Backend** | Data collection, business logic | PDF/Chart generation |
| **Frontend** | Display data, download reports | Generate PDFs or charts |

---

## Technology Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| **Web Framework** | FastAPI | High-performance async HTTP API |
| **ASGI Server** | Uvicorn | Lightweight async server |
| **Production Server** | Gunicorn + Uvicorn | Scalable production deployment |
| **Charts** | Matplotlib | High-quality chart generation |
| **Images** | Pillow | Image processing and handling |
| **PDF Creation** | ReportLab + xhtml2pdf | PDF generation and HTML conversion |
| **Templating** | Jinja2 | HTML template rendering |
| **Validation** | Pydantic | Request/response validation |

---

## Quick Start

### Local Development

```bash
# 1. Create virtual environment
python -m venv venv-report
source venv-report/bin/activate  # Windows: .\venv-report\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run development server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# 4. Check it's running
curl http://localhost:8001/health
```

### Docker

```bash
# Build image
docker build -t report-service:latest .

# Run container
docker run -p 8001:8001 report-service:latest
```

### Railway Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed Railway setup.

---

## API Endpoints

### Health & Info
- `GET /` - Service status
- `GET /health` - Health check
- `GET /info` - Service information and endpoints

### Chart Generation
- `POST /generate-pie-chart` - Generate pie chart
- `POST /generate-bar-chart` - Generate bar chart
- `POST /generate-line-chart` - Generate line chart

### PDF Generation
- `POST /generate-pdf` - Generate financial report PDF

See [API_CONTRACT.md](API_CONTRACT.md) for detailed endpoint documentation.

---

## Usage Examples

### Generate Pie Chart

```python
import requests

response = requests.post(
    'http://localhost:8001/generate-pie-chart',
    json={
        "data": [
            {"label": "Food", "value": 5000, "percentage": 25},
            {"label": "Transport", "value": 3000, "percentage": 15},
            {"label": "Utilities", "value": 2000, "percentage": 10}
        ],
        "title": "Expense Distribution"
    }
)

result = response.json()
image_base64 = result['image_base64']  # Embed in HTML or PDF
```

### Generate PDF Report

```python
report_data = {
    "month": 1,
    "year": 2024,
    "user_name": "John Doe",
    "summary": {
        "income": 50000,
        "expense": 35000,
        "net_savings": 15000,
        "savings_rate": 30.0,
        "transaction_count": 45,
        "income_count": 5,
        "expense_count": 40
    },
    "category_breakdown": [
        {"category": "Food", "amount": 8000, "count": 12, "percentage": 22.9}
    ],
    "transactions": [
        {
            "id": 1,
            "date": "2024-01-15",
            "description": "Grocery shopping",
            "category": "Food",
            "type": "expense",
            "amount": 2500
        }
    ]
}

response = requests.post(
    'http://localhost:8001/generate-pdf',
    json={"report_data": report_data}
)

result = response.json()
pdf_base64 = result['pdf_base64']

# Decode and save
import base64
pdf_bytes = base64.b64decode(pdf_base64)
with open('report.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Using from Django Backend

```python
from analytics.report_client import get_report_client

report_client = get_report_client()

# Check health
if not report_client.health_check():
    return Response({'error': 'Report service unavailable'}, status=503)

# Generate PDF
pdf_bytes = report_client.generate_pdf(report_data)

# Return to user
from django.http import FileResponse
return FileResponse(
    BytesIO(pdf_bytes),
    as_attachment=True,
    filename='Financial_Report.pdf',
    content_type='application/pdf'
)
```

---

## Configuration

### Environment Variables

```env
# Service
DEBUG=false
LOG_LEVEL=INFO
SERVICE_NAME=Report Service
SERVICE_VERSION=1.0.0

# Server
HOST=0.0.0.0
PORT=8001

# Backend Integration
BACKEND_BASE_URL=http://localhost:9000

# Charts
CHART_DPI=100

# PDF
PDF_PAGE_SIZE=A4

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://example.com
```

### Configuration File

Edit `config.py` for advanced settings:
- Chart colors and dimensions
- PDF margins and fonts
- Jinja2 template settings
- CORS origins

---

## Project Structure

```
report-service/
├── main.py                 # FastAPI app with all endpoints
├── config.py               # Configuration and settings
├── schemas.py              # Pydantic request/response models
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── API_CONTRACT.md         # API documentation
├── DEPLOYMENT_GUIDE.md     # Railway deployment guide
├── README.md               # This file
├── templates/              # HTML templates
│   └── report_template.html # Financial report template
└── charts/                 # Temporary chart files
```

---

## Development

### Running Tests

```bash
# Run integration tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Code Style

```bash
# Format code
black main.py config.py schemas.py

# Lint
pylint main.py config.py schemas.py

# Type checking
mypy main.py config.py schemas.py
```

### Adding New Chart Types

1. Add schema in `schemas.py`:
```python
class CustomChartRequest(BaseModel):
    data: List[dict]
    title: str
    # ... more fields
```

2. Add generation function in `main.py`:
```python
def generate_custom_chart(request: CustomChartRequest) -> str:
    # Implementation
    return chart_base64
```

3. Add FastAPI endpoint:
```python
@app.post("/generate-custom-chart")
async def endpoint_generate_custom_chart(request: CustomChartRequest):
    # Use function above
    return ChartResponse(...)
```

---

## Performance

### Typical Response Times
| Operation | Time |
|-----------|------|
| Pie Chart | 500ms - 1.5s |
| Bar Chart | 600ms - 2s |
| Line Chart | 700ms - 2.5s |
| PDF (with charts) | 2s - 5s |

### Optimization Tips
1. Use DPI=100 for charts (lower quality, faster)
2. Limit transaction list to recent transactions
3. Consider pagination for very large reports
4. Cache frequently generated reports

---

## Troubleshooting

### Service Won't Start
```bash
# Check dependencies
pip install -r requirements.txt

# Check port is available
netstat -an | grep 8001

# Run with verbose logging
DEBUG=true LOG_LEVEL=DEBUG uvicorn main:app
```

### Slow Chart Generation
```bash
# Reduce DPI
CHART_DPI=75  # Default is 100

# Reduce chart dimensions
# Edit config.py CHART_WIDTH, CHART_HEIGHT
```

### PDF Contains No Charts
```bash
# Check template exists
ls templates/report_template.html

# Check chart generation succeeded
# Review logs for chart generation errors
```

### Connection Issues
```bash
# Check service is running
curl http://localhost:8001/health

# Check backend can reach it
curl http://<report-service-url>/health
```

---

## Monitoring

### Health Checks

```bash
# Manual health check
curl http://localhost:8001/health

# In application
if report_client.health_check():
    # Service is available
    pdf_bytes = report_client.generate_pdf(data)
```

### Logging

Set log level via environment variable:
```bash
LOG_LEVEL=DEBUG    # Most verbose
LOG_LEVEL=INFO     # Normal
LOG_LEVEL=WARNING  # Less verbose
LOG_LEVEL=ERROR    # Errors only
```

### Metrics

Monitor from Railway dashboard:
- Response times
- Error rate
- Request count
- CPU/Memory usage

---

## Integration with Main Backend

The Report Service integrates seamlessly with Django:

```python
# In Django views
from analytics.report_client import get_report_client

report_client = get_report_client()
pdf_bytes = report_client.generate_pdf(report_data)
```

See `backend/analytics/report_client.py` for full client implementation.

---

## Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test locally: `uvicorn main:app --reload`
- [ ] Build Docker image: `docker build -t report-service:latest .`
- [ ] Test Docker: `docker run -p 8001:8001 report-service:latest`
- [ ] Deploy to Railway (see DEPLOYMENT_GUIDE.md)
- [ ] Update REPORT_SERVICE_URL in Django settings
- [ ] Test from backend: `curl http://backend/analytics/export-pdf/`
- [ ] Monitor logs for 24 hours
- [ ] Set up auto-scaling if needed

---

## Next Steps

1. **Local Setup**: Follow Quick Start above
2. **Test Endpoints**: Review API_CONTRACT.md
3. **Deploy**: Follow DEPLOYMENT_GUIDE.md
4. **Monitor**: Check logs and performance metrics
5. **Optimize**: Adjust settings based on usage patterns

---

## Support

- 📖 **API Documentation**: See API_CONTRACT.md
- 🚀 **Deployment Guide**: See DEPLOYMENT_GUIDE.md
- 🔧 **Configuration**: See config.py comments
- 📊 **Architecture**: See main project README.md

---

## Version

**Current Version**: 1.0.0

---

## License

Part of the Expense Tracker project.

---

## Key Benefits

✅ **Production-Ready**: Optimized for Railway deployment  
✅ **Scalable**: Easy horizontal scaling with multiple instances  
✅ **Maintainable**: Clean, documented, well-structured code  
✅ **Reliable**: Error isolation prevents backend outages  
✅ **Fast**: Optimized for quick response times  
✅ **Flexible**: Easy to add new chart/report types  

---

**Status**: Active & Maintained ✨
