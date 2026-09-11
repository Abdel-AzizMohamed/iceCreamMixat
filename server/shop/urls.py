from django.urls import path
from .views.shop import (
    categories,
    languages,
    product_items,
    product_options,
    products_by_category,
    featured_offer_product,
    create_order,
    get_order_details,
    get_multiple_orders,
    search_products,
)
from .views.category import (
    category_dashboard,
    delete_category,
    insert_category,
    category_edit_data,
    edit_category,
)
from .views.product import (
    product_dashboard,
    delete_product,
    insert_product,
    product_edit_data,
    edit_product,
)
from .views.flavor import (
    flavor_dashboard,
    delete_flavor,
    insert_flavor,
    flavor_edit_data,
    edit_flavor,
)
from .views.extra import (
    extra_dashboard,
    delete_extra,
    insert_extra,
    extra_edit_data,
    edit_extra,
)
from .views.staff import staff_dashboard_orders, update_order_status
from .views.dashboard import admin_analytics_dashboard


urlpatterns = [
    path("categories/", categories, name="categories"),
    path("languages/", languages, name="languages"),
    path("product-items/", product_items, name="product-items"),
    path(
        "categories/<int:category_id>/products/",
        products_by_category,
        name="products-by-category",
    ),
    path(
        "products/featured-offer/",
        featured_offer_product,
        name="featured-offer-product",
    ),
    path(
        "products/search/",
        search_products,
        name="search-products",
    ),
    path(
        "products/<int:product_id>/options/",
        product_options,
        name="product-options",
    ),
    path("orders/create/", create_order, name="create-order"),
    path("orders/<int:order_id>/", get_order_details, name="get-order-details"),
    path("orders/batch/", get_multiple_orders, name="get-multiple-orders"),
    path(
        "staff/dashboard/orders/",
        staff_dashboard_orders,
        name="staff-dashboard-orders",
    ),
    # 2. Update order status (e.g., mark as paid, start cooking, or done)
    path(
        "staff/orders/<int:order_id>/status/",
        update_order_status,
        name="staff-update-order-status",
    ),
]

urlpatterns += [
    path("dashboard/categories/", category_dashboard,
         name="dashboard-categories"),
    path(
        "dashboard/categories/create/",
        insert_category,
        name="dashboard-create-category",
    ),
    path(
        "dashboard/categories/delete/",
        delete_category,
        name="dashboard-category-delete",
    ),
    path(
        "dashboard/categories/<int:category_id>/",
        category_edit_data,
        name="dashboard-category-edit-data",
    ),
    path(
        "dashboard/categories/edit/",
        edit_category,
        name="dashboard-category-edit",
    ),
    path(
        "dashboard/analytics/",
        admin_analytics_dashboard,
        name="admin-analytics-dashboard",
    ),
]

urlpatterns += [
    path("dashboard/products/", product_dashboard, name="dashboard-products"),
    path(
        "dashboard/products/create/",
        insert_product,
        name="dashboard-create-product",
    ),
    path(
        "dashboard/products/delete/",
        delete_product,
        name="dashboard-product-delete",
    ),
    path(
        "dashboard/products/<int:product_id>/",
        product_edit_data,
        name="dashboard-product-edit-data",
    ),
    path(
        "dashboard/products/edit/",
        edit_product,
        name="dashboard-product-edit",
    ),
]

urlpatterns += [
    path("dashboard/flavors/", flavor_dashboard, name="dashboard-flavors"),
    path(
        "dashboard/flavors/create/",
        insert_flavor,
        name="dashboard-create-flavor",
    ),
    path(
        "dashboard/flavors/delete/",
        delete_flavor,
        name="dashboard-flavor-delete",
    ),
    path(
        "dashboard/flavors/<int:flavor_id>/",
        flavor_edit_data,
        name="dashboard-flavor-edit-data",
    ),
    path(
        "dashboard/flavors/edit/",
        edit_flavor,
        name="dashboard-flavor-edit",
    ),
]

urlpatterns += [
    path("dashboard/extras/", extra_dashboard, name="dashboard-extras"),
    path(
        "dashboard/extras/create/",
        insert_extra,
        name="dashboard-create-extra",
    ),
    path(
        "dashboard/extras/delete/",
        delete_extra,
        name="dashboard-extra-delete",
    ),
    path(
        "dashboard/extras/<int:extra_id>/",
        extra_edit_data,
        name="dashboard-extra-edit-data",
    ),
    path(
        "dashboard/extras/edit/",
        edit_extra,
        name="dashboard-extra-edit",
    ),
]
