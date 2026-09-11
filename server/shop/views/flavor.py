from rest_framework.decorators import api_view, parser_classes, permission_classes
from authsystem.permissions import IsAdminUserRole
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from shop.models import Flavor


@api_view(["POST"])
@permission_classes([IsAdminUserRole])
def flavor_dashboard(request):
    page = request.data.get("page")

    data = []
    category = Flavor.objects.all()
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
        extra_price = item.extra_price
        available = item.available

        data.append(
            {
                "id": item.id,
                "name": name,
                "extraPrice": extra_price,
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
def delete_flavor(request):
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

    existing = Flavor.objects.filter(id__in=ids_to_delete)
    count = existing.count()

    if count != len(ids_to_delete):
        return Response(
            {"message": "Some flavor IDs were not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    existing.delete()

    return Response(
        {"message": f"successfully deleted {count} records"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAdminUserRole])
@parser_classes([MultiPartParser, FormParser])
def insert_flavor(request):
    image = request.FILES.get("image")
    name_en = request.data.get("nameEn")
    name_ru = request.data.get("nameRu", "")
    name_tr = request.data.get("nameTr", "")
    name_pl = request.data.get("namePl", "")
    name_it = request.data.get("nameIt", "")
    extra_price = request.data.get("extraPrice")
    available = request.data.get("available")

    Flavor.objects.create(
        name_en=name_en,
        name_ru=name_ru,
        name_tr=name_tr,
        name_pl=name_pl,
        name_it=name_it,
        image=image,
        available=available,
        extra_price=extra_price,
    )

    return Response(
        {"message": "Successfully inserted the Flavor."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAdminUserRole])
def flavor_edit_data(request, flavor_id):
    try:
        flavor = Flavor.objects.get(id=flavor_id)
    except Flavor.DoesNotExist:
        return Response({"message": "Invalid flavor id."}, status=400)

    name_en = flavor.name_en
    name_ru = flavor.name_ru
    name_tr = flavor.name_tr
    name_pl = flavor.name_pl
    name_it = flavor.name_it
    if not flavor.image:
        image = ""
    else:
        image = request.build_absolute_uri(flavor.image.url)
    extra_price = flavor.extra_price
    available = flavor.available

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
                "extraPrice": extra_price,
            }
        }
    )


@api_view(["PUT"])
@permission_classes([IsAdminUserRole])
@parser_classes([MultiPartParser, FormParser])
def edit_flavor(request):
    flavor_id = request.data.get("flavorId")
    extra_price = request.data.get("extraPrice")
    available = request.data.get("available")

    try:
        flavor = Flavor.objects.get(id=flavor_id)
    except Flavor.DoesNotExist:
        return Response({"message": "Invalid flavor id."}, status=400)

    image = request.FILES.get("image", flavor.image)
    name_en = request.data.get("nameEn", flavor.name)
    name_ru = request.data.get("nameRu", flavor.name_ru)
    name_tr = request.data.get("nameTr", flavor.name_tr)
    name_pl = request.data.get("namePl", flavor.name_pl)
    name_it = request.data.get("nameIt", flavor.name_it)

    flavor.name_en = name_en
    flavor.name_ru = name_ru
    flavor.name_tr = name_tr
    flavor.name_pl = name_pl
    flavor.name_it = name_it
    flavor.image = image
    flavor.extra_price = extra_price
    flavor.available = available

    flavor.save()

    return Response({"message": "Successfully updated the Category."}, status=200)
