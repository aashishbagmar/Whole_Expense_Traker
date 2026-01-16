from django.urls import path
from .views import user_statistics, revenue_statistics, activity_logs, export_financial_report_pdf, get_financial_report_data, get_analytics_summary, get_analytics_insights

urlpatterns = [
    path('user-stats/', user_statistics, name='user_statistics'),
    path('revenue-stats/', revenue_statistics, name='revenue_statistics'),
    path('activity-logs/', activity_logs, name='activity_logs'),
    path('summary/', get_analytics_summary, name='analytics_summary'),
    path('insights/', get_analytics_insights, name='analytics_insights'),
    path('financial-report/', get_financial_report_data, name='financial_report_data'),
    path('export-pdf/', export_financial_report_pdf, name='export_financial_report_pdf'),
]
