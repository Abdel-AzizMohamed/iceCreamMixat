from datetime import timedelta
from decimal import Decimal
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from authsystem.permissions import IsAdminUserRole
from rest_framework.response import Response
from shop.models import Order


@api_view(["GET"])
@permission_classes([IsAdminUserRole])
def admin_analytics_dashboard(request):
    branch_id = request.query_params.get("branch_id", 1)
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    seven_days_ago = today - timedelta(days=6)

    # Base query for all branch orders
    branch_orders = Order.objects.filter(branch_id=branch_id)

    # Today's orders queryset
    today_orders = branch_orders.filter(created_at__date=today)

    # 1. Top KPI Summary Cards (Today's counts)
    total_orders_today = today_orders.count()
    pending_orders_today = today_orders.filter(status="pending").count()
    preparing_orders_today = today_orders.filter(status="preparing").count()
    completed_orders_today = today_orders.filter(status="completed").count()

    # Define paid/revenue-valid statuses
    PAID_STATUSES = ["paid", "preparing", "completed"]

    # 2. Revenue Calculations (Only include paid/completed orders)
    today_revenue = (
        today_orders.filter(status__in=PAID_STATUSES).aggregate(
            total=Sum("total_price_base")
        )["total"]
        or Decimal("0.00")
    )

    yesterday_revenue = (
        branch_orders.filter(
            created_at__date=yesterday, status__in=PAID_STATUSES
        ).aggregate(total=Sum("total_price_base"))["total"]
        or Decimal("0.00")
    )

    # Percentage change relative to yesterday
    if yesterday_revenue > 0:
        pct_change = (
            (today_revenue - yesterday_revenue) / yesterday_revenue
        ) * 100
        comparison_percentage = round(float(pct_change), 1)
    else:
        comparison_percentage = 100.0 if today_revenue > 0 else 0.0

    # 3. Bar Chart Data: Last 7 days revenue (Paid/Completed orders only)
    daily_sales = (
        branch_orders.filter(
            created_at__date__gte=seven_days_ago,
            created_at__date__lte=today,
            status__in=PAID_STATUSES,
        )
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(revenue=Sum("total_price_base"), orders_count=Count("id"))
        .order_by("date")
    )

    sales_by_date = {item["date"]: item["revenue"] for item in daily_sales}
    chart_data = []

    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        chart_data.append(
            {
                "day": day.strftime("%b %d"),
                "date": day.isoformat(),
                "revenue": str(sales_by_date.get(day, Decimal("0.00"))),
            }
        )

    # 4. Global Order Status Distribution (All database records)
    all_pending = branch_orders.filter(status="pending").count()
    all_preparing = branch_orders.filter(status="preparing").count()
    all_completed = branch_orders.filter(status="completed").count()
    all_total = branch_orders.count()

    return Response(
        {
            "summary": {
                "total_orders": total_orders_today,
                "pending_orders": pending_orders_today,
                "preparing_orders": preparing_orders_today,
                "completed_orders": completed_orders_today,
            },
            "sales_overview": {
                "currency": "USD",
                "today_revenue": str(today_revenue),
                "yesterday_revenue": str(yesterday_revenue),
                "percentage_change": comparison_percentage,
                "comparison_text": f"{'+' if comparison_percentage >= 0 else ''}{comparison_percentage}% compared to yesterday",
                "daily_sales_chart": chart_data,
            },
            "order_status_distribution": {
                "pending": all_pending,
                "preparing": all_preparing,
                "completed": all_completed,
                "total_orders": all_total,
            },
        }
    )
