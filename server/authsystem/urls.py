from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path(
        "token/refresh/", views.refresh_access_token_from_cookie, name="token-refresh"
    ),
    path("me/", views.me, name="me"),
]
