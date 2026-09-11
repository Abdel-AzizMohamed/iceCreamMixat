from rest_framework.decorators import api_view, parser_classes, permission_classes
from authsystem.permissions import IsAdminUserRole
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from shop.models import Category


@api_view(["POST"])
@permission_classes([IsAdminUserRole])
def category_dashboard(request):
    page = request.data.get("page")

    data = []
    category = Category.objects.all()
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


        products_count = item.products.count()

        data.append(
            {
                "id": item.id,
                "name": name,
                "productCount": products_count,
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
def delete_category(request):
    ids_to_delete = request.data.get("ids")

    if not ids_to_delete:
        return Response(
            {"message": "Category IDs are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not isinstance(ids_to_delete, list):
        return Response(
            {"message": "Please provide a valid list of ids"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing = Category.objects.filter(id__in=ids_to_delete)
    count = existing.count()

    if count != len(ids_to_delete):
        return Response(
            {"message": "Some category IDs were not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    existing.delete()

    return Response(
        {"message": f"successfully deleted {count} records"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAdminUserRole])
@parser_classes([MultiPartParser, FormParser])
def insert_category(request):
    image = request.FILES.get("image")
    name_en = request.data.get("nameEn")
    name_ru = request.data.get("nameRu", "")
    name_tr = request.data.get("nameTr", "")
    name_pl = request.data.get("namePl", "")
    name_it = request.data.get("nameIt", "")

    Category.objects.create(
        name_en=name_en,
        name_ru=name_ru,
        name_tr=name_tr,
        name_pl=name_pl,
        name_it=name_it,
        image=image,
    )

    return Response(
        {"message": "Successfully inserted the Category."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAdminUserRole])
def category_edit_data(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({"message": "Invalid category id."}, status=400)

    name_en = category.name_en
    name_ru = category.name_ru
    name_tr = category.name_tr
    name_pl = category.name_pl
    name_it = category.name_it
    if not category.image:
        image = ""
    else:
        image = request.build_absolute_uri(category.image.url)

    return Response(
        {
            "data": {
                "nameEn": name_en,
                "nameRu": name_ru,
                "nameTr": name_tr,
                "namePl": name_pl,
                "nameIt": name_it,
                "image": image
            }
        }
    )


@api_view(["PUT"])
@permission_classes([IsAdminUserRole])
@parser_classes([MultiPartParser, FormParser])
def edit_category(request):
    category_id = request.data.get("categoryId")

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({"message": "Invalid category id."}, status=400)

    image = request.FILES.get("image", category.image)

    name_en = request.data.get("nameEn", category.name)
    name_ru = request.data.get("nameRu", category.name_ru)
    name_tr = request.data.get("nameTr", category.name_tr)
    name_pl = request.data.get("namePl", category.name_pl)
    name_it = request.data.get("nameIt", category.name_it)

    category.name_en = name_en
    category.name_ru = name_ru
    category.name_tr = name_tr
    category.name_pl = name_pl
    category.name_it = name_it
    category.image = image

    category.save()

    return Response({"message": "Successfully updated the Category."}, status=200)
