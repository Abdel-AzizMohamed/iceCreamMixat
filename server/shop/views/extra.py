from rest_framework.decorators import api_view, parser_classes, permission_classes
from authsystem.permissions import IsAdminUserRole
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from shop.models import Extra


@api_view(["POST"])
@permission_classes([IsAdminUserRole])
def extra_dashboard(request):
    page = request.data.get("page")

    data = []
    category = Extra.objects.all()
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
        price = item.price
        available = item.available

        data.append(
            {
                "id": item.id,
                "name": name,
                "price": price,
                "available": available,
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
def delete_extra(request):
    ids_to_delete = request.data.get("ids")

    if not ids_to_delete:
        return Response(
            {"message": "Flavor IDs are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not isinstance(ids_to_delete, list):
        return Response(
            {"message": "Please provide a valid list of ids"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing = Extra.objects.filter(id__in=ids_to_delete)
    count = existing.count()

    if count != len(ids_to_delete):
        return Response(
            {"message": "Some extra IDs were not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    existing.delete()

    return Response(
        {"message": f"successfully deleted {count} records"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAdminUserRole])
@parser_classes([MultiPartParser, FormParser])
def insert_extra(request):
    image = request.FILES.get("image")
    name_en = request.data.get("nameEn")
    name_ru = request.data.get("nameRu", "")
    name_tr = request.data.get("nameTr", "")
    name_pl = request.data.get("namePl", "")
    name_it = request.data.get("nameIt", "")
    price = request.data.get("price")
    available = request.data.get("available")

    Extra.objects.create(
        name_en=name_en,
        name_ru=name_ru,
        name_tr=name_tr,
        name_pl=name_pl,
        name_it=name_it,
        image=image,
        available=available,
        price=price,
    )

    return Response(
        {"message": "Successfully inserted the Extra."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAdminUserRole])
def extra_edit_data(request, extra_id):
    try:
        extra = Extra.objects.get(id=extra_id)
    except Extra.DoesNotExist:
        return Response({"message": "Invalid extra id."}, status=400)

    name_en = extra.name_en
    name_ru = extra.name_ru
    name_tr = extra.name_tr
    name_pl = extra.name_pl
    name_it = extra.name_it
    if not extra.image:
        image = ""
    else:
        image = request.build_absolute_uri(extra.image.url)
    price = extra.price
    available = extra.available

    return Response(
        {
            "data": {
                "nameEn": name_en,
                "nameRu": name_ru,
                "nameTr": name_tr,
                "namePl": name_pl,
                "nameIt": name_it,
                "image": image,
                "available": available,
                "price": price,
            }
        }
    )


@api_view(["PUT"])
@permission_classes([IsAdminUserRole])
@parser_classes([MultiPartParser, FormParser])
def edit_extra(request):
    extra_id = request.data.get("extraId")
    price = request.data.get("price")
    available = request.data.get("available")

    try:
        extra = Extra.objects.get(id=extra_id)
    except Extra.DoesNotExist:
        return Response({"message": "Invalid extra id."}, status=400)

    image = request.FILES.get("image", extra.image)
    name_en = request.data.get("nameEn", extra.name)
    name_ru = request.data.get("nameRu", extra.name_ru)
    name_tr = request.data.get("nameTr", extra.name_tr)
    name_pl = request.data.get("namePl", extra.name_pl)
    name_it = request.data.get("nameIt", extra.name_it)

    extra.name_en = name_en
    extra.name_ru = name_ru
    extra.name_tr = name_tr
    extra.name_pl = name_pl
    extra.name_it = name_it
    extra.image = image
    extra.price = price
    extra.available = available

    extra.save()

    return Response({"message": "Successfully updated the Extra."}, status=200)
