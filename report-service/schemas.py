"""
Pydantic schemas for Report Service
Defines request/response models for all endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================
# Chart Generation Schemas
# ============================================

class ChartDataPoint(BaseModel):
    """Single data point for a chart"""
    label: str
    value: float
    percentage: Optional[float] = None


class PieChartRequest(BaseModel):
    """Request to generate a pie chart"""
    data: List[ChartDataPoint]
    title: str = "Chart"
    colors: Optional[List[str]] = None
    dpi: int = Field(default=100, ge=50, le=300)
    width: int = Field(default=8, ge=4, le=20)
    height: int = Field(default=6, ge=4, le=20)


class BarChartRequest(BaseModel):
    """Request to generate a bar chart"""
    categories: List[str]
    values: List[float]
    title: str = "Chart"
    x_label: str = ""
    y_label: str = ""
    colors: Optional[List[str]] = None
    dpi: int = Field(default=100, ge=50, le=300)
    width: int = Field(default=10, ge=4, le=20)
    height: int = Field(default=6, ge=4, le=20)


class LineChartRequest(BaseModel):
    """Request to generate a line chart"""
    dates: List[str]  # YYYY-MM-DD format
    values: List[float]
    title: str = "Trend"
    x_label: str = "Date"
    y_label: str = "Amount"
    color: str = "#3498db"
    dpi: int = Field(default=100, ge=50, le=300)
    width: int = Field(default=12, ge=4, le=20)
    height: int = Field(default=6, ge=4, le=20)


class ChartResponse(BaseModel):
    """Response from chart generation"""
    success: bool
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    chart_type: str
    error: Optional[str] = None


# ============================================
# Financial Report Data Schemas
# ============================================

class CategoryBreakdown(BaseModel):
    """Category-wise expense breakdown"""
    category: str
    amount: float
    count: int
    percentage: float


class TransactionData(BaseModel):
    """Individual transaction in report"""
    id: int
    date: str  # YYYY-MM-DD
    description: str
    category: str
    type: str  # 'income' or 'expense'
    amount: float


class FinancialSummary(BaseModel):
    """Summary statistics for financial report"""
    income: float
    expense: float
    net_savings: float
    savings_rate: float
    transaction_count: int
    income_count: int
    expense_count: int


class FinancialReportData(BaseModel):
    """Complete data for financial report PDF generation"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2099)
    user_name: str
    user_email: Optional[str] = None
    summary: FinancialSummary
    category_breakdown: List[CategoryBreakdown]
    transactions: List[TransactionData]
    generated_at: Optional[str] = None  # ISO format datetime


class PDFGenerationRequest(BaseModel):
    """Request to generate a PDF report"""
    report_data: FinancialReportData
    template_name: str = "report_template.html"
    include_charts: bool = True
    include_transactions: bool = True
    page_size: str = "A4"  # A4 or letter


class PDFResponse(BaseModel):
    """Response from PDF generation"""
    success: bool
    pdf_base64: Optional[str] = None
    pdf_url: Optional[str] = None
    file_name: str
    error: Optional[str] = None
    generated_at: Optional[str] = None


# ============================================
# Health Check & Meta Schemas
# ============================================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


# ============================================
# Chart Request for Multiple Charts
# ============================================

class MultiChartRequest(BaseModel):
    """Request to generate multiple charts at once"""
    charts: List[Dict[str, Any]]  # flexible structure for different chart types
    include_base64: bool = True
    include_files: bool = False


class MultiChartResponse(BaseModel):
    """Response containing multiple generated charts"""
    success: bool
    charts: List[ChartResponse]
    error: Optional[str] = None
