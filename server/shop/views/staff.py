from rest_framework.decorators import api_view, permission_classes
from authsystem.permissions import IsStaffUserRole
from rest_framework import status
from rest_framework.response import Response
from shop.models import Order
from shop.serializers import StaffOrderDashboardSerializer


@api_view(["GET"])
@permission_classes([IsStaffUserRole])
# @permission_classes([IsAdminUser])  # Ensures only logged-in staff access
def staff_dashboard_orders(request):
    branch_id = request.query_params.get("branch_id", 1)

    # Base query for today's active orders
    orders_qs = Order.objects.filter(branch_id=branch_id).prefetch_related(
        "items__product", "items__flavors", "items__extras"
    )

    # 1. Left Sidebar: Pending/Unpaid orders
    unpaid_orders = orders_qs.filter(status="pending")

    # 2. Center Grid: Active cooking cards ("preparing")
    active_orders = orders_qs.filter(status="preparing")

    # 3. Right Sidebar: Paid orders queued to be cooked ("paid")
    queued_orders = orders_qs.filter(status="paid")

    serializer_context = {"request": request}

    return Response(
        {
            "unpaid_orders": StaffOrderDashboardSerializer(
                unpaid_orders, many=True, context=serializer_context
            ).data,
            "active_orders": StaffOrderDashboardSerializer(
                active_orders, many=True, context=serializer_context
            ).data,
            "queued_orders": StaffOrderDashboardSerializer(
                queued_orders, many=True, context=serializer_context
            ).data,
        }
    )


@api_view(["PATCH"])
@permission_classes([IsStaffUserRole])
# @permission_classes([IsAdminUser])
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        return Response({"message": "Status updated", "status": order.status})

    return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
