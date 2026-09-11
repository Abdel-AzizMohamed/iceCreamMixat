import json
from rest_framework.decorators import api_view, parser_classes, permission_classes
from authsystem.permissions import IsAdminUserRole
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from shop.models import Product, Category


@api_view(["POST"])
@permission_classes([IsAdminUserRole])
def product_dashboard(request):
    page = request.data.get("page")

    data = []
    category = Product.objects.all()
    paginate = Paginator(category, 5)

    try:
        page = paginate.page(page)
    except Exception as e:
        return Response({"message": str(e)}, status=400)

    for item in list(page):
        name = item.name
        name_ru = item.name_ru
        name_it = item.name_it
        name_pl = item.name_pl
        name_tr = item.name_tr

        if not name and name_ru:
            name = name_ru
        elif not name and name_it:
            name = name_it
        elif not name and name_pl:
            name = name_pl
        else:
            name = name if name else name_tr

        base_price = item.base_price
        category = item.category.name
        available = item.available
        offer = item.offer
        offer_precent = item.offer_precent

        data.append(
            {
                "id": item.id,
                "name": name,
                "basePrice": base_price,
                "category": category,
                "available": available,
                "offer": offer,
                "offer_precent": offer_precent,
            }
        )

    return Response(
        {
            "data": data,
            "currentPage": page.number,
            "totalPages": paginate.num_pages,
            "hasNext": page.has_next(),
            "hasPrevious": page.has_previous(),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAdminUserRole])
def delete_product(request):
    ids_to_delete = request.data.get("ids")

    if not ids_to_delete:
        return Response(
            {"message": "Product IDs are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not isinstance(ids_to_delete, list):
        return Response(
            {"message": "Please provide a valid list of ids"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing = Product.objects.filter(id__in=ids_to_delete)
    count = existing.count()

    if count != len(ids_to_delete):
        return Response(
            {"message": "Some product IDs were not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    existing.delete()

    return Response(
        {"message": f"successfully deleted {count} records"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAdminUserRole])
@parser_classes([MultiPartParser, FormParser])
def insert_product(request):
    name_en = request.data.get("nameEn")
    name_ru = request.data.get("nameRu", "")
    name_tr = request.data.get("nameTr", "")
    name_pl = request.data.get("namePl", "")
    name_it = request.data.get("nameIt", "")

    description_en = request.data.get("descriptionEn")
    description_ru = request.data.get("descriptionRu", "")
    description_tr = request.data.get("descriptionTr", "")
    description_pl = request.data.get("descriptionPl", "")
    description_it = request.data.get("descriptionIt", "")

    base_price = request.data.get("basePrice", 0)
    if isinstance(base_price, str):
        base_price = 0

    category_id = request.data.get("categoryId")
    category = Category.objects.get(id=category_id)

    available = request.data.get("available", False)
    offer = request.data.get("offer", False)
    try:
        offer_percent = float(request.data.get("offerPercent", 0))
    except (ValueError, TypeError):
        offer_percent = 0.0
    flavors = json.loads(request.data.get("flavorsIds", "[]"))
    extras = json.loads(request.data.get("extrasIds", "[]"))

    image = request.FILES.get("image")

    product = Product.objects.create(
        name_en=name_en,
        name_ru=name_ru,
        name_tr=name_tr,
        name_pl=name_pl,
        name_it=name_it,
        description_en=description_en,
        description_ru=description_ru,
        description_tr=description_tr,
        description_pl=description_pl,
        description_it=description_it,
        base_price=base_price,
        category=category,
        available=available,
        offer=offer,
        offer_precent=offer_percent,
        image=image,
    )

    product.flavors.set(flavors)
    product.extras.set(extras)

    return Response(
        {"message": "Successfully inserted the Product."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAdminUserRole])
def product_edit_data(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Category.DoesNotExist:
        return Response({"message": "Invalid category id."}, status=400)

    name_en = product.name_en
    name_ru = product.name_ru
    name_tr = product.name_tr
    name_pl = product.name_pl
    name_it = product.name_it

    description_en = product.description_en
    description_ru = product.description_ru
    description_tr = product.description_tr
    description_pl = product.description_pl
    description_it = product.description_it

    category = product.category.name
    base_price = product.base_price
    available = product.available
    offer = product.offer
    offer_precent = product.offer_precent
    flavors = [
        {"id": flavor.id, "name": flavor.name} for flavor in product.flavors.all()
    ]
    extras = [{"id": extra.id, "name": extra.name} for extra in product.extras.all()]

    if not product.image:
        image = ""
    else:
        image = request.build_absolute_uri(product.image.url)

    return Response(
        {
            "data": {
                "nameEn": name_en,
                "nameRu": name_ru,
                "nameTr": name_tr,
                "namePl": name_pl,
                "nameIt": name_it,
                "descriptionEn": description_en,
                "descriptionRu": description_ru,
                "descriptionTr": description_tr,
                "descriptionPl": description_pl,
                "descriptionIt": description_it,
                "category": category,
                "basePrice": base_price,
                "avaiable": available,
                "offer": offer,
                "offerPrecent": offer_precent,
                "flavors": flavors,
                "extras": extras,
                "image": image,
            }
        }
    )


@api_view(["PUT"])
@permission_classes([IsAdminUserRole])
@parser_classes([MultiPartParser, FormParser])
def edit_product(request):
    product_id = request.data.get("productId")

    base_price = request.data.get("basePrice")

    category_id = request.data.get("categoryId")
    category = Category.objects.get(id=category_id)

    available = request.data.get("available")
    offer = request.data.get("offer")
    try:
        offer_percent = float(request.data.get("offerPrecent", 0))
    except (ValueError, TypeError):
        offer_percent = 0.0
    flavors = json.loads(request.data.get("flavorsIds", "[]"))
    extras = json.loads(request.data.get("extrasIds", "[]"))

    product = Product.objects.get(id=product_id)

    image = request.FILES.get("image", product.image)

    name_en = request.data.get("nameEn", product.name)
    name_ru = request.data.get("nameRu", product.name_ru)
    name_tr = request.data.get("nameTr", product.name_tr)
    name_pl = request.data.get("namePl", product.name_pl)
    name_it = request.data.get("nameIt", product.name_it)

    description_en = request.data.get("descriptionEn", product.description)
    description_ru = request.data.get("descriptionRu", product.description_ru)
    description_tr = request.data.get("descriptionTr", product.description_tr)
    description_pl = request.data.get("descriptionPl", product.description_pl)
    description_it = request.data.get("descriptionIt", product.description_it)

    product.name_en = name_en
    product.name_ru = name_ru
    product.name_tr = name_tr
    product.name_pl = name_pl
    product.name_it = name_it
    product.image = image

    product.name_en = name_en
    product.name_ru = name_ru
    product.name_tr = name_tr
    product.name_pl = name_pl
    product.name_it = name_it

    product.description_en = description_en
    product.description_ru = description_ru
    product.description_tr = description_tr
    product.description_pl = description_pl
    product.description_it = description_it

    product.category = category
    product.base_price = base_price
    product.available = available
    product.offer = offer
    product.offer_precent = offer_percent

    product.flavors.set(flavors)
    product.extras.set(extras)

    product.save()

    return Response({"message": "Successfully updated the Product."}, status=200)
