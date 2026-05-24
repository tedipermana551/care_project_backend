from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError

from core.exceptions import success_response
from .serializers import RegisterSerializer, UserSerializer

class AuthRateThrottle(AnonRateThrottle):
    """Strict per-IP throttle applied only to auth endpoints: 10 requests/hour."""
    scope = 'auth'

class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            message='Registration successful.',
            status=201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        from django.contrib.auth import authenticate
        from django.contrib.auth.models import User
        from rest_framework import status
        from rest_framework.response import Response

        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')

        if not email or not password:
            return Response(
                {'success': False, 'message': 'Email and password are required.', 'errors': {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # username == email (set during registration)
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {'success': False, 'message': 'Invalid email or password.', 'errors': {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        outstanding_qs = OutstandingToken.objects.filter(user=user)
        for token in outstanding_qs:
            BlacklistedToken.objects.get_or_create(token=token)

        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            message='Login successful.',
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from rest_framework import status
        from rest_framework.response import Response

        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'success': False, 'message': 'Refresh token is required.', 'errors': {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {'success': False, 'message': 'Invalid or expired token.', 'errors': {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(message='Logged out successfully.')
