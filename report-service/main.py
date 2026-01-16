"""
Report Service - FastAPI Application
Dedicated Microservice for PDF and Chart Generation
No database, no authentication, stateless service
"""
import logging
import base64
import io
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
import matplotlib
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from xhtml2pdf import pisa
import pytz

from config import settings
from schemas import (
    PieChartRequest, BarChartRequest, LineChartRequest, ChartResponse,
    FinancialReportData, PDFGenerationRequest, PDFResponse,
    HealthCheck, ErrorResponse
)

# Use non-interactive backend for matplotlib in production
matplotlib.use('Agg')

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Report Service",
    description="PDF and Chart Generation Microservice",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://expense-tracker-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZIP middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Initialize Jinja2 environment for templates
jinja_env = Environment(
    loader=FileSystemLoader(str(settings.TEMPLATES_DIR)),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True
)


# ============================================
# Health Check & Meta Endpoints
# ============================================

@app.get("/", tags=["health"])
@app.get("/health", tags=["health"])
async def health_check():
    """Service health check endpoint"""
    return HealthCheck(
        status="ok",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        timestamp=datetime.now(pytz.UTC).isoformat()
    )


@app.get("/info", tags=["health"])
async def service_info():
    """Get service information"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
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


# ============================================
# Chart Generation Endpoints
# ============================================

def generate_pie_chart(request: PieChartRequest) -> str:
    """Generate a pie chart, save as PNG, and return base64-encoded PNG"""
    try:
        logger.info(f"Generating pie chart (file-based): {request.title}")
        output_dir = settings.CHARTS_TEMP_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        # Use a unique filename based on title and timestamp
        import time
        safe_title = ''.join(c if c.isalnum() else '_' for c in request.title)
        filename = f"pie_{safe_title}_{int(time.time())}.png"
        file_path = output_dir / filename

        labels = [item.label for item in request.data]
        sizes = [item.value for item in request.data]
        colors_to_use = request.colors or settings.CHART_COLORS

        fig, ax = plt.subplots(figsize=(request.width, request.height), dpi=request.dpi)
        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_to_use[:len(sizes)]
        )
        ax.set_title(request.title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(file_path, format="png")
        plt.close(fig)

        # Read file and encode as base64
        with open(file_path, "rb") as f:
            chart_base64 = base64.b64encode(f.read()).decode('utf-8')

        logger.info(f"Pie chart saved and encoded from: {file_path}")
        return chart_base64
    except Exception as e:
        logger.error(f"Pie chart file generation failed: {e}", exc_info=True)
        raise


def generate_bar_chart(request: BarChartRequest) -> str:
    """Generate a bar chart and return base64-encoded PNG"""
    try:
        logger.info(f"Generating bar chart: {request.title}")
        
        colors_to_use = request.colors or [settings.CHART_COLORS[0]] * len(request.categories)
        
        # Create figure
        fig, ax = plt.subplots(
            figsize=(request.width, request.height),
            dpi=request.dpi
        )
        
        # Generate bar chart
        ax.bar(request.categories, request.values, color=colors_to_use)
        ax.set_title(request.title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(request.x_label, fontsize=11)
        ax.set_ylabel(request.y_label, fontsize=11)
        
        # Rotate x-axis labels if many categories
        if len(request.categories) > 5:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=request.dpi, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        # Convert to base64
        chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
        logger.info(f"Bar chart generated successfully: {request.title}")
        
        return chart_base64
    except Exception as e:
        logger.error(f"Error generating bar chart: {e}", exc_info=True)
        raise


def generate_line_chart(request: LineChartRequest) -> str:
    """Generate a line chart and return base64-encoded PNG"""
    try:
        logger.info(f"Generating line chart: {request.title}")
        
        # Create figure
        fig, ax = plt.subplots(
            figsize=(request.width, request.height),
            dpi=request.dpi
        )
        
        # Generate line chart
        ax.plot(request.dates, request.values, marker='o', color=request.color, linewidth=2)
        ax.set_title(request.title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(request.x_label, fontsize=11)
        ax.set_ylabel(request.y_label, fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=request.dpi, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        # Convert to base64
        chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
        logger.info(f"Line chart generated successfully: {request.title}")
        
        return chart_base64
    except Exception as e:
        logger.error(f"Error generating line chart: {e}", exc_info=True)
        raise


@app.post("/generate-pie-chart", response_model=ChartResponse, tags=["charts"])
async def endpoint_generate_pie_chart(request: PieChartRequest) -> ChartResponse:
    """
    Generate a pie chart from expense data
    
    Returns base64-encoded PNG image embedded in response
    """
    try:
        image_base64 = generate_pie_chart(request)
        return ChartResponse(
            success=True,
            image_base64=image_base64,
            chart_type="pie"
        )
    except Exception as e:
        logger.error(f"Pie chart endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-bar-chart", response_model=ChartResponse, tags=["charts"])
async def endpoint_generate_bar_chart(request: BarChartRequest) -> ChartResponse:
    """
    Generate a bar chart from categorical data
    
    Returns base64-encoded PNG image embedded in response
    """
    try:
        image_base64 = generate_bar_chart(request)
        return ChartResponse(
            success=True,
            image_base64=image_base64,
            chart_type="bar"
        )
    except Exception as e:
        logger.error(f"Bar chart endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-line-chart", response_model=ChartResponse, tags=["charts"])
async def endpoint_generate_line_chart(request: LineChartRequest) -> ChartResponse:
    """
    Generate a line chart for trend visualization
    
    Returns base64-encoded PNG image embedded in response
    """
    try:
        image_base64 = generate_line_chart(request)
        return ChartResponse(
            success=True,
            image_base64=image_base64,
            chart_type="line"
        )
    except Exception as e:
        logger.error(f"Line chart endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PDF Generation Endpoints
# ============================================

def generate_pdf_from_html(html_string: str, filename: str) -> bytes:
    """Convert HTML to PDF using xhtml2pdf"""
    try:
        logger.info(f"Converting HTML to PDF: {filename}")
        
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html_string, pdf_buffer)
        
        if pisa_status.err:
            raise Exception(f"PDF generation failed: {pisa_status.err}")
        
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.getvalue()
        
        logger.info(f"PDF generated successfully: {filename} ({len(pdf_bytes)} bytes)")
        return pdf_bytes
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        raise

@app.get("/api/analytics/financial-report/")
def render_financial_report_html(report_data: FinancialReportData) -> str:
    """Render financial report HTML from template with data"""
    try:
        logger.info(f"Rendering financial report HTML for {report_data.user_name}")
        
        # Generate pie chart from expense data (file-based logic)
        pie_chart_base64 = None
        pie_chart_path = None
        logger.info(f"Pie chart debug: category_breakdown = {report_data.category_breakdown}")
        if report_data.category_breakdown:
            try:
                chart_request = PieChartRequest(
                    data=[
                        {'label': item.category, 'value': item.amount}
                        for item in report_data.category_breakdown
                    ],
                    title="Expense Distribution by Category"
                )
                safe_user_name = report_data.user_name.replace(' ', '_')
                filename = f"pie_chart_{safe_user_name}_{report_data.month}_{report_data.year}.png"
                pie_chart_path = Path(
                    generate_pie_chart_file(
                        chart_request,
                        filename
                    )
                ).resolve()
                # Read file and encode as base64
                with open(pie_chart_path, "rb") as f:
                    pie_chart_base64 = base64.b64encode(f.read()).decode('utf-8')
                logger.info(f"Pie chart file generated and encoded: {pie_chart_path}")
            except Exception as chart_error:
                logger.warning(f"Failed to generate pie chart: {chart_error}")
                logger.warning(f"Pie chart error details:", exc_info=True)
        
        # Format numbers with Rs. prefix
        def format_currency(amount: float) -> str:
            return f"Rs. {amount:,.2f}"
        
        # Calculate report period
        from calendar import month_name
        report_period = f"{month_name[report_data.month]} {report_data.year}"
        
        # Get current datetime in IST
        ist = pytz.timezone('Asia/Kolkata')
        generated_date = datetime.now(ist).strftime('%d %B %Y at %H:%M:%S')
        
        # Compute relative path from working directory for xhtml2pdf compatibility
        pie_chart_rel_path = pie_chart_path.relative_to(Path.cwd()).as_posix()
        
        # Prepare context for template
        context = {
            'user_name': report_data.user_name,
            'report_period': report_period,
            'generated_date': generated_date,
            'pie_chart_path': pie_chart_rel_path,
            'total_income': format_currency(report_data.summary.income),
            'total_expense': format_currency(report_data.summary.expense),
            'net_savings': format_currency(report_data.summary.net_savings),
            'savings_rate': f"{report_data.summary.savings_rate:.1f}%",
            'expense_breakdown': report_data.category_breakdown,
            'transactions': report_data.transactions,
            'pie_chart_base64': pie_chart_base64,
            'ai_insights': generate_ai_insights(report_data)
        }
        
        # Render template
        template = jinja_env.get_template('report_template.html')
        html_string = template.render(context)
        
        logger.info(f"Financial report HTML rendered successfully")
        return html_string
    except Exception as e:
        logger.error(f"Error rendering financial report HTML: {e}", exc_info=True)
        raise


def generate_ai_insights(report_data: FinancialReportData) -> str:
    """Generate AI insights based on financial data"""
    insights = []
    
    # Top spending category
    if report_data.category_breakdown:
        top_item = report_data.category_breakdown[0]
        insights.append(
            f"<p><strong>Top Spending Category:</strong> {top_item.category} accounts for "
            f"{top_item.percentage:.1f}% of your total expenses.</p>"
        )
    
    # Savings rate analysis
    income = report_data.summary.income
    if income > 0:
        savings_rate = report_data.summary.savings_rate
        if savings_rate >= 50:
            insights.append(
                "<p>Excellent savings rate! You are saving more than half of your income. "
                "Keep up this financial discipline!</p>"
            )
        elif savings_rate >= 30:
            insights.append(
                "<p>Good savings rate. You are maintaining a healthy financial discipline.</p>"
            )
        elif savings_rate >= 10:
            insights.append(
                "<p>You are saving a portion of your income. Consider analyzing your expenses "
                "to increase your savings rate.</p>"
            )
        else:
            insights.append(
                "<p>Your current savings rate is low. Review your expenses to improve your "
                "financial health.</p>"
            )
    else:
        insights.append("<p>No income recorded for this period.</p>")
    
    # Transaction count
    if report_data.summary.transaction_count > 0:
        insights.append(
            f"<p><strong>Transaction Summary:</strong> You recorded {report_data.summary.transaction_count} "
            f"transactions ({report_data.summary.income_count} income, "
            f"{report_data.summary.expense_count} expenses).</p>"
        )
    
    return "\n".join(insights)


@app.post("/generate-pdf", response_model=PDFResponse, tags=["pdf"])
async def endpoint_generate_pdf(request: PDFGenerationRequest) -> PDFResponse:
    """
    Generate a PDF financial report from structured data
    
    Accepts:
    - report_data: Financial data (income, expenses, breakdown, transactions)
    - template_name: HTML template to use (default: report_template.html)
    - include_charts: Whether to embed charts (default: True)
    - include_transactions: Whether to include transaction list (default: True)
    
    Returns:
    - PDF content as base64-encoded string
    """
    try:
        logger.info(f"Generating PDF report for {request.report_data.user_name}")
        
        # Render HTML template with data
        html_string = render_financial_report_html(request.report_data)
        
        # Generate PDF from HTML
        pdf_bytes = generate_pdf_from_html(
            html_string,
            f"Financial_Report_{request.report_data.month}_{request.report_data.year}.pdf"
        )
        
        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return PDFResponse(
            success=True,
            pdf_base64=pdf_base64,
            file_name=f"Financial_Report_{request.report_data.month}_{request.report_data.year}.pdf",
            generated_at=datetime.now(pytz.UTC).isoformat()
        )
    except Exception as e:
        logger.error(f"PDF generation endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================
# Startup & Shutdown Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info(f"Templates directory: {settings.TEMPLATES_DIR}")
    logger.info(f"Charts directory: {settings.CHARTS_TEMP_DIR}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


def generate_pie_chart_file(request: PieChartRequest, filename: str) -> str:
    """
    Generate a pie chart and save it as PNG file
    Returns absolute file path
    """
    try:
        output_dir = settings.CHARTS_TEMP_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / filename

        labels = [item.label for item in request.data]
        sizes = [item.value for item in request.data]
        colors_to_use = request.colors or settings.CHART_COLORS

        fig, ax = plt.subplots(figsize=(6, 6), dpi=150)

        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_to_use[:len(sizes)]
        )

        ax.set_title(request.title, fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(file_path, format="png")
        plt.close(fig)

        logger.info(f"Pie chart saved at: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"Pie chart file generation failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
