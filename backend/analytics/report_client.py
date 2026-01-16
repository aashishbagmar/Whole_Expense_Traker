"""
HTTP Client for Report Service
Handles all communication with the Report Service microservice
"""
import logging
import base64
from typing import Optional, Dict, Any
import requests
from django.conf import settings
from io import BytesIO

logger = logging.getLogger(__name__)


class ReportServiceClient:
    """Client for interacting with the Report Service"""
    
    def __init__(self):
        """Initialize client with Report Service base URL"""
        self.base_url = getattr(
            settings,
            'REPORT_SERVICE_URL',
            'http://localhost:8001'
        )
        self.timeout = getattr(settings, 'REPORT_SERVICE_TIMEOUT', 30)
    
    def health_check(self) -> bool:
        """Check if Report Service is online"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Report Service health check failed: {e}")
            return False
    
    def generate_pie_chart(
        self,
        data: list,
        title: str = "Chart",
        colors: Optional[list] = None,
        dpi: int = 100,
        width: int = 8,
        height: int = 6
    ) -> Optional[str]:
        """
        Generate a pie chart
        
        Args:
            data: List of dicts with 'label', 'value', 'percentage'
            title: Chart title
            colors: Optional list of colors
            dpi: DPI for rendering
            width: Chart width
            height: Chart height
        
        Returns:
            Base64-encoded PNG image or None on error
        """
        try:
            payload = {
                "data": [
                    {
                        "label": item.get('label') or item.get('category', 'Unknown'),
                        "value": float(item.get('value') or item.get('amount', 0)),
                        "percentage": item.get('percentage')
                    }
                    for item in data
                ],
                "title": title,
                "colors": colors,
                "dpi": dpi,
                "width": width,
                "height": height
            }
            
            response = requests.post(
                f"{self.base_url}/generate-pie-chart",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('image_base64')
                else:
                    logger.error(f"Pie chart generation failed: {result.get('error')}")
            else:
                logger.error(f"Report Service error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error generating pie chart: {e}")
        
        return None
    
    def generate_bar_chart(
        self,
        categories: list,
        values: list,
        title: str = "Chart",
        x_label: str = "",
        y_label: str = "",
        colors: Optional[list] = None,
        dpi: int = 100,
        width: int = 10,
        height: int = 6
    ) -> Optional[str]:
        """
        Generate a bar chart
        
        Returns:
            Base64-encoded PNG image or None on error
        """
        try:
            payload = {
                "categories": categories,
                "values": [float(v) for v in values],
                "title": title,
                "x_label": x_label,
                "y_label": y_label,
                "colors": colors,
                "dpi": dpi,
                "width": width,
                "height": height
            }
            
            response = requests.post(
                f"{self.base_url}/generate-bar-chart",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('image_base64')
                else:
                    logger.error(f"Bar chart generation failed: {result.get('error')}")
            else:
                logger.error(f"Report Service error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error generating bar chart: {e}")
        
        return None
    
    def generate_line_chart(
        self,
        dates: list,
        values: list,
        title: str = "Trend",
        x_label: str = "Date",
        y_label: str = "Amount",
        color: str = "#3498db",
        dpi: int = 100,
        width: int = 12,
        height: int = 6
    ) -> Optional[str]:
        """
        Generate a line chart
        
        Returns:
            Base64-encoded PNG image or None on error
        """
        try:
            payload = {
                "dates": dates,
                "values": [float(v) for v in values],
                "title": title,
                "x_label": x_label,
                "y_label": y_label,
                "color": color,
                "dpi": dpi,
                "width": width,
                "height": height
            }
            
            response = requests.post(
                f"{self.base_url}/generate-line-chart",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('image_base64')
                else:
                    logger.error(f"Line chart generation failed: {result.get('error')}")
            else:
                logger.error(f"Report Service error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error generating line chart: {e}")
        
        return None
    
    def generate_pdf(
        self,
        report_data: Dict[str, Any],
        template_name: str = "report_template.html",
        include_charts: bool = True,
        include_transactions: bool = True,
        page_size: str = "A4"
    ) -> Optional[bytes]:
        """
        Generate a PDF report
        
        Args:
            report_data: Financial report data dictionary
            template_name: Name of template to use
            include_charts: Include charts in PDF
            include_transactions: Include transaction list
            page_size: A4 or letter
        
        Returns:
            PDF bytes or None on error
        """
        try:
            payload = {
                "report_data": report_data,
                "template_name": template_name,
                "include_charts": include_charts,
                "include_transactions": include_transactions,
                "page_size": page_size
            }
            
            response = requests.post(
                f"{self.base_url}/generate-pdf",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Decode base64 PDF
                    pdf_base64 = result.get('pdf_base64')
                    if pdf_base64:
                        pdf_bytes = base64.b64decode(pdf_base64)
                        return pdf_bytes
                    else:
                        logger.error("No PDF data in response")
                else:
                    logger.error(f"PDF generation failed: {result.get('error')}")
            else:
                logger.error(f"Report Service error: {response.status_code}")
                logger.error(f"Response: {response.text}")
        
        except Exception as e:
            logger.error(f"Error generating PDF: {e}", exc_info=True)
        
        return None


# Singleton instance
_client = None


def get_report_client() -> ReportServiceClient:
    """Get or create Report Service client"""
    global _client
    if _client is None:
        _client = ReportServiceClient()
    return _client
