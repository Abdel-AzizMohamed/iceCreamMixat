from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from shop.models import Category, Product, Order, Flavor, Extra, Language
from django.db.models import Q
from shop.serializers import CategorySerializer
from shop.serializers import (
    ProductSerializer,
    ProductWithOptionsSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderSummarySerializer,
)


@api_view(["GET"])
def languages(request):
    """"""
    langs = [
        {"id": lang.id, "name": lang.name, "prefix": lang.lang_prefix}
        for lang in Language.objects.all()
    ]
    return Response({"data": langs}, status=status.HTTP_200_OK)


@api_view(["GET"])
def categories(request):
    """"""
    categories_qs = Category.objects.all()
    # Passing context={'request': request} ensures DRF returns full absolute URLs
    serializer = CategorySerializer(
        categories_qs, many=True, context={"request": request}
    )

    return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def product_items(request):
    """"""
    flavors = [
        {"id": flavor.id, "name": flavor.name} for flavor in Flavor.objects.all()
    ]
    extras = [{"id": extra.id, "name": extra.name}
              for extra in Extra.objects.all()]

    return Response(
        {"data": {"flavors": flavors, "extras": extras}}, status=status.HTTP_200_OK
    )


# API 1: Get products by Category ID
@api_view(["GET"])
def products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id, available=True)
    serializer = ProductSerializer(
        products, many=True, context={"request": request})
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)


# API 2: Get flavors and extras for a specific Product ID
@api_view(["GET"])
def product_options(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    serializer = ProductWithOptionsSerializer(
        product, context={"request": request})
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def featured_offer_product(request):
    # Fetch the first product where offer=True and available=True
    product = Product.objects.filter(offer=True, available=True).first()

    if not product:
        return Response(
            {"message": "No offer product available at the moment."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProductSerializer(product, context={"request": request})
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_order(request):
    serializer = OrderCreateSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save()
        return Response(
            {
                "message": "Order created successfully",
                "data": {
                    "order_id": order.id,
                    "daily_order_number": order.daily_order_number,
                    "reference_code": order.reference_code,
                    "total_price": order.total_price_base,
                    "status": order.status,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Passing context={"request": request} enables absolute URL resolution
    serializer = OrderDetailSerializer(order, context={"request": request})
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_multiple_orders(request):
    ids_param = request.query_params.get("ids", "")

    if not ids_param:
        return Response(
            {"error": "No order IDs provided. Pass IDs like ?ids=1,2,3"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        order_ids = [
            int(id_str.strip()) for id_str in ids_param.split(",") if id_str.strip()
        ]
    except ValueError:
        return Response(
            {"error": "Invalid order IDs format. IDs must be integers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Prefetch items and product relations to optimize database queries
    orders = Order.objects.filter(
        id__in=order_ids).prefetch_related("items__product")
    serializer = OrderSummarySerializer(
        orders, many=True, context={"request": request})

    return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def search_products(request):
    # Get the search keyword from query params e.g. /api/shop/products/search/?q=ice
    query = request.query_params.get("q", "").strip()

    if not query:
        return Response(
            {"data": []},
            status=status.HTTP_200_OK,
        )

    # Search for products where name OR description contains the keyword (case-insensitive)
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        available=True,
    )

    serializer = ProductSerializer(
        products, many=True, context={"request": request})
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)
