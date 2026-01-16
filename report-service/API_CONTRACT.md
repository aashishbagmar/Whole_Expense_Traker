# Report Service API Contract

## Overview

The Report Service is a dedicated microservice responsible for:
- **Chart Generation**: Pie, bar, line charts from financial data
- **PDF Report Generation**: Professional financial reports with charts
- **Image Embedding**: Charts as base64-encoded images for easy transport

### Key Principles

- **Stateless**: No database, no session management
- **Fast**: Lightweight, quick response times
- **Independent**: Can be scaled separately from main backend
- **Reliable**: Isolated failures don't affect main system
- **Flexible**: Easy to add new chart types or report formats

---

## Health Check Endpoints

### GET /

### GET /health

Check if the Report Service is online and healthy.

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "Report Service",
  "version": "1.0.0",
  "timestamp": "2024-01-06T10:30:45.123456+00:00"
}
```

**Usage:**
```bash
curl http://localhost:8001/health
```

---

### GET /info

Get service information and available endpoints.

**Response (200 OK):**
```json
{
  "service": "Report Service",
  "version": "1.0.0",
  "features": ["pie-charts", "bar-charts", "line-charts", "pdf-reports"],
  "endpoints": {
    "charts": {
      "pie": "/generate-pie-chart",
      "bar": "/generate-bar-chart",
      "line": "/generate-line-chart"
    },
    "pdf": "/generate-pdf"
  }
}
```

---

## Chart Generation Endpoints

### POST /generate-pie-chart

Generate a pie chart showing expense distribution.

**Request Body:**
```json
{
  "data": [
    {
      "label": "Food & Dining",
      "value": 5000,
      "percentage": 25.5
    },
    {
      "label": "Transportation",
      "value": 3000,
      "percentage": 15.3
    },
    {
      "label": "Utilities",
      "value": 2000,
      "percentage": 10.2
    }
  ],
  "title": "Expense Distribution by Category",
  "colors": ["#e74c3c", "#e67e22", "#f39c12"],
  "dpi": 100,
  "width": 8,
  "height": 6
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "chart_type": "pie",
  "error": null
}
```

**Error Response (500):**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Usage:**
```bash
curl -X POST http://localhost:8001/generate-pie-chart \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "title": "My Pie Chart"
  }'
```

---

### POST /generate-bar-chart

Generate a bar chart for categorical data comparison.

**Request Body:**
```json
{
  "categories": ["January", "February", "March", "April"],
  "values": [5000, 6200, 4800, 7100],
  "title": "Monthly Expenses",
  "x_label": "Month",
  "y_label": "Amount (Rs.)",
  "colors": ["#3498db", "#3498db", "#3498db", "#3498db"],
  "dpi": 100,
  "width": 10,
  "height": 6
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "chart_type": "bar",
  "error": null
}
```

**Parameters:**
- `categories` (required): List of category labels
- `values` (required): List of numerical values
- `title` (optional): Chart title
- `x_label` (optional): X-axis label
- `y_label` (optional): Y-axis label
- `colors` (optional): List of colors, one per category
- `dpi` (optional, default: 100): Dots per inch (50-300)
- `width` (optional, default: 10): Chart width in inches
- `height` (optional, default: 6): Chart height in inches

---

### POST /generate-line-chart

Generate a line chart for trend visualization.

**Request Body:**
```json
{
  "dates": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
  "values": [3500, 4200, 3800, 4500],
  "title": "Daily Spending Trend",
  "x_label": "Date",
  "y_label": "Amount (Rs.)",
  "color": "#3498db",
  "dpi": 100,
  "width": 12,
  "height": 6
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "chart_type": "line",
  "error": null
}
```

**Parameters:**
- `dates` (required): List of date strings (YYYY-MM-DD format)
- `values` (required): List of numerical values
- `title` (optional): Chart title
- `x_label` (optional, default: "Date"): X-axis label
- `y_label` (optional, default: "Amount"): Y-axis label
- `color` (optional, default: "#3498db"): Single color for line
- `dpi` (optional, default: 100): Dots per inch (50-300)
- `width` (optional, default: 12): Chart width in inches
- `height` (optional, default: 6): Chart height in inches

---

## PDF Generation Endpoints

### POST /generate-pdf

Generate a complete financial report PDF with charts.

**Request Body:**
```json
{
  "report_data": {
    "month": 1,
    "year": 2024,
    "user_name": "John Doe",
    "user_email": "john@example.com",
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
      {
        "category": "Food & Dining",
        "amount": 8000,
        "count": 12,
        "percentage": 22.9
      },
      {
        "category": "Transportation",
        "amount": 6000,
        "count": 8,
        "percentage": 17.1
      }
    ],
    "transactions": [
      {
        "id": 1,
        "date": "2024-01-15",
        "description": "Grocery shopping at Supermarket",
        "category": "Food & Dining",
        "type": "expense",
        "amount": 2500
      }
    ]
  },
  "template_name": "report_template.html",
  "include_charts": true,
  "include_transactions": true,
  "page_size": "A4"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQKJeLjz9MNCjEgMCBvYmo...",
  "file_name": "Financial_Report_January_2024.pdf",
  "generated_at": "2024-01-06T10:30:45.123456+00:00",
  "error": null
}
```

**Error Response (500):**
```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "timestamp": "2024-01-06T10:30:45.123456+00:00"
}
```

**Request Parameters:**

**report_data (required):**
- `month` (int, 1-12): Report month
- `year` (int): Report year
- `user_name` (string): Full name of user
- `user_email` (string, optional): User email
- `summary` (object): Financial summary with income, expense, savings
- `category_breakdown` (array): Category-wise expense breakdown
- `transactions` (array): List of transactions to include

**summary object:**
```json
{
  "income": 50000,           // Total income
  "expense": 35000,          // Total expenses
  "net_savings": 15000,      // Income - Expense
  "savings_rate": 30.0,      // (Savings / Income) * 100
  "transaction_count": 45,   // Total transactions
  "income_count": 5,         // Income transactions
  "expense_count": 40        // Expense transactions
}
```

**category_breakdown array:**
```json
[
  {
    "category": "Food & Dining",
    "amount": 8000,
    "count": 12,
    "percentage": 22.9
  }
]
```

**transactions array:**
```json
[
  {
    "id": 1,
    "date": "2024-01-15",
    "description": "Grocery shopping",
    "category": "Food & Dining",
    "type": "expense",
    "amount": 2500
  }
]
```

**Options:**
- `template_name` (optional, default: "report_template.html"): HTML template to use
- `include_charts` (optional, default: true): Generate and embed charts
- `include_transactions` (optional, default: true): Include transaction list
- `page_size` (optional, default: "A4"): A4 or letter

**Usage from Backend:**
```python
from analytics.report_client import get_report_client

# Get client
report_client = get_report_client()

# Check health
if not report_client.health_check():
    raise Exception("Report Service unavailable")

# Generate PDF
pdf_bytes = report_client.generate_pdf(report_data)

# Return to user
from django.http import FileResponse
from io import BytesIO
return FileResponse(
    BytesIO(pdf_bytes),
    as_attachment=True,
    filename='report.pdf',
    content_type='application/pdf'
)
```

---

## Data Structures

### Category Breakdown Format
```json
{
  "category": "Food & Dining",
  "amount": 8000.50,
  "count": 12,
  "percentage": 22.9
}
```

### Transaction Format
```json
{
  "id": 123,
  "date": "2024-01-15",
  "description": "Grocery shopping at XYZ",
  "category": "Food & Dining",
  "type": "expense",
  "amount": 2500.50
}
```

### Chart Data Point Format
```json
{
  "label": "Food & Dining",
  "value": 8000,
  "percentage": 22.9
}
```

---

## Error Handling

### Service Unavailable (503)
```json
{
  "detail": "Service temporarily unavailable"
}
```

### Invalid Request (400)
```json
{
  "detail": "Invalid request parameters"
}
```

### Server Error (500)
```json
{
  "detail": "Internal server error"
}
```

---

## Best Practices

### 1. Health Checks
Always check Report Service health before making requests:
```python
if not report_client.health_check():
    # Handle gracefully, show error to user
    return error_response("Report service unavailable")
```

### 2. Timeouts
Set appropriate timeouts for long-running PDF generation:
```python
# Adjust in Django settings
REPORT_SERVICE_TIMEOUT = 30  # seconds
```

### 3. Error Handling
Implement proper error handling and user-friendly messages:
```python
try:
    pdf_bytes = report_client.generate_pdf(data)
except Exception as e:
    logger.error(f"PDF generation failed: {e}")
    return Response(
        {"error": "Failed to generate report. Please try again later."},
        status=503
    )
```

### 4. Caching
Cache generated reports if frequently requested:
```python
# Consider caching PDFs for the same report parameters
cache_key = f"pdf_{user_id}_{month}_{year}"
pdf_bytes = cache.get(cache_key)
if not pdf_bytes:
    pdf_bytes = report_client.generate_pdf(data)
    cache.set(cache_key, pdf_bytes, timeout=3600)
```

### 5. Background Processing
For very large reports, consider async processing:
```python
# Use Celery task for report generation
@shared_task
def generate_report_async(user_id, month, year):
    # Gather data
    # Call Report Service
    # Store result
    pass
```

---

## Configuration

### Environment Variables

```bash
# Report Service location
REPORT_SERVICE_URL=http://localhost:8001

# Connection timeout (seconds)
REPORT_SERVICE_TIMEOUT=30

# Enable/disable Report Service
REPORT_SERVICE_ENABLED=true
```

### Django Settings

```python
REPORT_SERVICE_URL = os.environ.get('REPORT_SERVICE_URL', 'http://localhost:8001')
REPORT_SERVICE_TIMEOUT = int(os.environ.get('REPORT_SERVICE_TIMEOUT', 30))
REPORT_SERVICE_ENABLED = os.environ.get('REPORT_SERVICE_ENABLED', 'true').lower() == 'true'
```

---

## Deployment

### Local Development
```bash
cd report-service
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Docker
```bash
docker build -t report-service:latest .
docker run -p 8001:8001 report-service:latest
```

### Railway
See `DEPLOYMENT_GUIDE_REPORT_SERVICE.md` for detailed Railway deployment instructions.

---

## Performance

### Typical Response Times
- Pie Chart: 500ms - 1.5s
- Bar Chart: 600ms - 2s
- Line Chart: 700ms - 2.5s
- PDF with Charts: 2s - 5s

### Optimization Tips
- Use appropriate DPI for charts (100 is usually sufficient)
- Limit transaction list to last 100 transactions for large reports
- Consider pagination for very large transaction lists

---

## Support & Debugging

### Enable Debug Logging
```bash
DEBUG=true LOG_LEVEL=DEBUG python -m uvicorn main:app
```

### Check Logs
```bash
# View service logs
tail -f service.log
```

### Test Endpoint
```bash
# Test health
curl http://localhost:8001/health

# Test chart generation
curl -X POST http://localhost:8001/generate-pie-chart \
  -H "Content-Type: application/json" \
  -d '{"data": [{"label": "Test", "value": 100}], "title": "Test"}'
```

---

## Version History

### v1.0.0 (2024-01-06)
- Initial release
- Pie, bar, line chart support
- PDF report generation
- Jinja2 templating
- Full API documentation
