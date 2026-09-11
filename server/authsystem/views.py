from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from authsystem.serializers import UserSerializer


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    debug = getattr(settings, "DEBUG", False)

    if not email or not password:
        return Response(
            {"Message": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(email=email, password=password)

    if user is not None:
        # Generate token with embedded role/branch claims
        refresh_token = RefreshToken.for_user(user)
        refresh_token["role"] = user.role
        refresh_token["branch_id"] = user.branch_id

        access_token = refresh_token.access_token
        access_token["role"] = user.role
        access_token["branch_id"] = user.branch_id

        response = Response(
            {
                "Message": "Login successful!",
                "accessToken": str(access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "branch_id": user.branch_id,
                },
            },
            status=status.HTTP_200_OK,
        )

        # response.set_cookie(
        #     key="refresh_token",
        #     value=str(refresh_token),
        #     httponly=True,
        #     secure=not debug,
        #     samesite="Lax" if debug else "None",
        #     max_age=1 * 24 * 60 * 60,
        # )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token),
            httponly=True,
            secure=True,
            samesite="None",
            max_age=1 * 24 * 60 * 60,
        )

        return response

    return Response(
        {"Message": "Invalid email or password."},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(["POST"])
def refresh_access_token_from_cookie(request):
    refresh_token = request.COOKIES.get("refresh_token")

    if refresh_token is None:
        return Response(
            {"detail": "Refresh token not found in cookie."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token

        return Response(
            {
                "access": str(access_token),
                "access_expires_at": access_token["exp"],
            },
            status=status.HTTP_200_OK,
        )
    except TokenError:
        return Response(
            {"detail": "Invalid or expired refresh token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.COOKIES.get("refresh_token")

    if not refresh_token:
        return Response(
            {"Message": "No refresh token found."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response(
            {"Message": "Invalid or expired refresh token."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    response = Response(
        {"Message": "Logged out successfully."},
        status=status.HTTP_205_RESET_CONTENT,
    )
    response.delete_cookie("refresh_token")

    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response({"data": serializer.data}, status=200)
