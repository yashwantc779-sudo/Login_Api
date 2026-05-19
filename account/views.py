import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import *


class RegisterAPIView(APIView):

    def get(self, request, pk=None):

        # Get single user
        if pk:

            try:
                user = User.objects.get(id=pk)

                serializer = RegisterSerializer(user)

                return Response(serializer.data)

            except User.DoesNotExist:

                return Response(
                    {"message": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Get all users
        users = User.objects.all()

        serializer = RegisterSerializer(users, many=True)

        return Response(serializer.data)

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        return Response(
            {
                "message": "Account created successfully.",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED,
        )
    
class LoginAPIView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # check_password is provided by AbstractBaseUser — no manual hashing needed
        if not user.check_password(password):
            return Response(
                {"message": "Invalid credentials."},  # Same message — don't leak which field is wrong
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return user data. In a real project, issue a JWT or session token here.
        return Response(
            {"message": "Login successful.", "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )


# class ChangePasswordAPIView(APIView):
#     """
#     Requires the user to be authenticated.
#     The user is identified from the auth token — NOT from a request body email.
#     """

#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = ChangePasswordSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         user = request.user  # Authenticated user from token — safe

#         if not user.check_password(serializer.validated_data["old_password"]):
#             return Response(
#                 {"message": "Old password is incorrect."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user.set_password(serializer.validated_data["new_password"])  # Hashes automatically
#         user.save()

#         return Response(
#             {"message": "Password changed successfully."},
#             status=status.HTTP_200_OK,
#         )


# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token

from .serializers import *


class ChangePasswordAPIView(APIView):

    def post(self, request):

        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        token = request.headers.get("Authorization")

        if not token:
            return Response(
                {"message": "Token required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = token.split(" ")[1]

        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user

        except Token.DoesNotExist:
            return Response(
                {"message": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(
            serializer.validated_data["old_password"]
        ):
            return Response(
                {"message": "Old password is incorrect"}
            )

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )


class ForgotPasswordAPIView(APIView):

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=serializer.validated_data["email"])
        except User.DoesNotExist:
            # Always return 200 — don't reveal whether an email is registered
            return Response(
                {"message": "If that email exists, a reset link has been sent."},
                status=status.HTTP_200_OK,
            )

        user.forgot_password_token = uuid.uuid4()
        user.save()

        # TODO: Send reset email here, e.g.:
        # send_reset_email(user.email, user.forgot_password_token)

        return Response(
            {"message": "If that email exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordAPIView(APIView):

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]

        try:
            user = User.objects.get(forgot_password_token=token)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["password"])
        user.forgot_password_token = None  # Invalidate token after use
        user.save()

        return Response(
            {"message": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )