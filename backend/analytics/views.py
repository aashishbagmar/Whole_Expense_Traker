from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.utils.timezone import now
from django.db.models import Sum, Count, Q
from datetime import timedelta, datetime
from transactions.models import Transaction
from django.contrib.auth import get_user_model
from .serializers import UserCountSerializer, RevenueSerializer
# from payments.models import Subscription  # Payments app removed
from django.http import FileResponse
from io import BytesIO
import logging

from .report_client import get_report_client

logger = logging.getLogger(__name__)



User = get_user_model()

@api_view(['GET'])
def user_statistics(request):
    total_users = User.objects.count()
    premium_users = User.objects.filter(is_premium=True).count()

    data = {
        "total_users": total_users,
        "premium_users": premium_users,
    }
    serializer = UserCountSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
def revenue_statistics(request):
    total_revenue = Transaction.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    current_month = now().month
    monthly_revenue = Transaction.objects.filter(
        created_at__month=current_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    data = {
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
    }
    serializer = RevenueSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
def activity_logs(request):
    # TODO: Implement activity logs if needed
    return Response({'message': 'Activity logs not yet implemented'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_summary(request):
    """
    Get quick analytics summary for dashboard
    Returns: income, expenses, balance, transaction count
    """
    try:
        user = request.user
        all_transactions = Transaction.objects.filter(user=user)
        
        income_total = all_transactions.filter(category_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = all_transactions.filter(category_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'success': True,
            'income': float(income_total),
            'expense': float(expense_total),
            'balance': float(income_total) - float(expense_total),
            'transaction_count': all_transactions.count()
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_insights(request):
    """
    Get analytics insights and trends
    Returns: top categories, trends, insights
    """
    try:
        user = request.user
        all_transactions = Transaction.objects.filter(user=user)
        
        # Get top expense categories
        top_categories = all_transactions.filter(
            category_type='expense'
        ).values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')[:5]
        
        top_categories_data = []
        for item in top_categories:
            top_categories_data.append({
                'category': item['category__name'] or 'Uncategorized',
                'amount': float(item['total']),
                'count': item['count']
            })
        
        return Response({
            'success': True,
            'top_categories': top_categories_data,
            'insights': 'Your expense patterns are being analyzed'
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_financial_report_data(request):
    """
    Get aggregated financial report data with flexible filtering.
    Filters: month, year, category, transaction_type (income/expense/all)
    Returns: income, expense, net savings, category breakdown, all transactions
    """
    try:
        # Get filter parameters
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        category_filter = request.query_params.get('category')  # Category name or 'all'
        transaction_type = request.query_params.get('transaction_type', 'all')  # 'income', 'expense', 'all'
        
        # Set defaults
        if month and year:
            month = int(month)
            year = int(year)
        else:
            current_date = now()
            month = current_date.month
            year = current_date.year
        
        user = request.user
        
        # Base query: all transactions for the user, filtered by month/year
        base_query = Transaction.objects.filter(
            user=user,
            date__month=month,
            date__year=year
        )
        
        print(f"\n=== FINANCIAL REPORT DATA ===")
        print(f"Filters: Month={month}, Year={year}, Category={category_filter}, Type={transaction_type}")
        print(f"Total transactions in period: {base_query.count()}")
        
        # Apply category filter if specified
        if category_filter and category_filter.lower() != 'all':
            base_query = base_query.filter(category__name__iexact=category_filter)
            print(f"After category filter: {base_query.count()}")
        
        # Apply transaction type filter
        if transaction_type.lower() != 'all':
            base_query = base_query.filter(category_type=transaction_type.lower())
            print(f"After type filter: {base_query.count()}")
        
        # Calculate totals
        income_total = base_query.filter(category_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = base_query.filter(category_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        net_savings = float(income_total) - float(expense_total)
        savings_rate = (net_savings / float(income_total) * 100) if float(income_total) > 0 else 0
        
        print(f"Income: {income_total}, Expense: {expense_total}, Net: {net_savings}")
        
        # Get expense breakdown by category
        expense_breakdown = base_query.filter(
            category_type='expense'
        ).values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Format breakdown for response
        breakdown_data = []
        for item in expense_breakdown:
            category_name = item['category__name'] or 'Uncategorized'
            amount = float(item['total'])
            count = item['count']
            percentage = (amount / float(expense_total) * 100) if float(expense_total) > 0 else 0
            breakdown_data.append({
                'category': category_name,
                'amount': amount,
                'count': count,
                'percentage': round(percentage, 1)
            })
        
        # Get all transactions for the report
        transactions = base_query.select_related('category').order_by('-date')
        transactions_data = []
        for trans in transactions:
            transactions_data.append({
                'id': trans.id,
                'date': trans.date.strftime('%Y-%m-%d'),
                'description': trans.description or '',
                'category': trans.category.name if trans.category else 'Uncategorized',
                'type': trans.category_type,
                'amount': float(trans.amount)
            })
        
        print(f"=== END REPORT ===\n")
        
        return Response({
            'success': True,
            'month': month,
            'year': year,
            'filters': {
                'category': category_filter or 'all',
                'transaction_type': transaction_type
            },
            'summary': {
                'income': float(income_total),
                'expense': float(expense_total),
                'net_savings': net_savings,
                'savings_rate': round(savings_rate, 1),
                'transaction_count': base_query.count(),
                'income_count': base_query.filter(category_type='income').count(),
                'expense_count': base_query.filter(category_type='expense').count()
            },
            'category_breakdown': breakdown_data,
            'transactions': transactions_data
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_financial_report_pdf(request):
    """
    Generate professional PDF by delegating to Report Service
    Report Service handles all PDF and chart generation
    """
    try:
        # Get filter parameters
        month = request.query_params.get('month') if hasattr(request, 'query_params') else request.GET.get('month')
        year = request.query_params.get('year') if hasattr(request, 'query_params') else request.GET.get('year')
        category_filter = request.query_params.get('category') if hasattr(request, 'query_params') else request.GET.get('category')
        transaction_type = request.query_params.get('transaction_type', 'all') if hasattr(request, 'query_params') else request.GET.get('transaction_type', 'all')
        
        # Set defaults
        if month and year:
            month = int(month)
            year = int(year)
        else:
            current_date = now()
            month = current_date.month
            year = current_date.year
        
        user = request.user
        
        # Build base query with filtering (same as financial_report endpoint)
        base_query = Transaction.objects.filter(
            user=user,
            date__month=month,
            date__year=year
        )
        
        # Apply category filter if specified
        if category_filter and category_filter.lower() != 'all':
            base_query = base_query.filter(category__name__iexact=category_filter)
        
        # Apply transaction type filter
        if transaction_type.lower() != 'all':
            base_query = base_query.filter(category_type=transaction_type.lower())
        
        # Calculate totals
        income_total = base_query.filter(category_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = base_query.filter(category_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        net_savings = float(income_total) - float(expense_total)
        savings_rate = (net_savings / float(income_total) * 100) if float(income_total) > 0 else 0
        
        # Get expense breakdown by category
        expense_breakdown = base_query.filter(
            category_type='expense'
        ).values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Format breakdown for response
        breakdown_data = []
        for item in expense_breakdown:
            category_name = item['category__name'] or 'Uncategorized'
            amount = float(item['total'])
            count = item['count']
            percentage = (amount / float(expense_total) * 100) if float(expense_total) > 0 else 0
            breakdown_data.append({
                'category': category_name,
                'amount': amount,
                'count': count,
                'percentage': round(percentage, 1)
            })
        
        # Get all transactions for the report
        transactions = base_query.select_related('category').order_by('-date')
        transactions_data = []
        for trans in transactions:
            transactions_data.append({
                'id': trans.id,
                'date': trans.date.strftime('%Y-%m-%d'),
                'description': trans.description or '',
                'category': trans.category.name if trans.category else 'Uncategorized',
                'type': trans.category_type,
                'amount': float(trans.amount)
            })
        
        # Build report data structure for Report Service
        report_data = {
            'month': month,
            'year': year,
            'user_name': user.get_full_name() or user.username,
            'user_email': user.email,
            'summary': {
                'income': float(income_total),
                'expense': float(expense_total),
                'net_savings': net_savings,
                'savings_rate': round(savings_rate, 1),
                'transaction_count': base_query.count(),
                'income_count': base_query.filter(category_type='income').count(),
                'expense_count': base_query.filter(category_type='expense').count()
            },
            'category_breakdown': breakdown_data,
            'transactions': transactions_data
        }
        
        # Call Report Service to generate PDF
        report_client = get_report_client()
        
        # Check if Report Service is available
        if not report_client.health_check():
            logger.error("Report Service is not available")
            return Response(
                {'error': 'Report Service is temporarily unavailable. Please try again later.'},
                status=503
            )
        
        # Generate PDF via Report Service
        pdf_bytes = report_client.generate_pdf(report_data)
        
        if not pdf_bytes:
            logger.error("Failed to generate PDF from Report Service")
            return Response(
                {'error': 'Failed to generate PDF. Please try again.'},
                status=500
            )
        
        # Get month name for filename
        month_name = datetime(year, month, 1).strftime('%B')
        
        # Return PDF as file download
        return FileResponse(
            BytesIO(pdf_bytes),
            as_attachment=True,
            filename=f'Financial_Report_{month_name}_{year}.pdf',
            content_type='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error in export_financial_report_pdf: {e}", exc_info=True)
        return Response({'error': str(e)}, status=400)
