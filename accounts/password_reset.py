from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            generator = PasswordResetTokenGenerator()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = generator.make_token(user)
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}"

            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass

        return Response(
            {
                "message": "If an email is linked to an account, you will receive a password reset link."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST
            )

        generator = PasswordResetTokenGenerator()
        if not generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = request.data.get("new_password")
        if not new_password:
            return Response(
                {"error": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )
