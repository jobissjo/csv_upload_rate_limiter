from rest_framework.generics import GenericAPIView
from .serializers import FileUploadSerializer, LoginSerializer, TokenResponseSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import User
from rest_framework import status
from .utils import get_tokens_for_user, ServiceError
from drf_spectacular.utils import extend_schema
from .constants import CLIENT_ERROR_TYPE, VALIDATION_ERROR_TYPE
import pandas as pd


@extend_schema(tags=["Auth"], responses={200: TokenResponseSerializer})
class GetTokenView(GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ServiceError(
                detail="User with this email does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
                error_type=CLIENT_ERROR_TYPE,
            )

        if not user.check_password(password):
            raise ServiceError(
                detail="Invalid password",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type=CLIENT_ERROR_TYPE,
            )

        if not user.is_active:
            raise ServiceError(
                detail="User is inactive",
                status_code=status.HTTP_403_FORBIDDEN,
                error_type=CLIENT_ERROR_TYPE,
            )

        tokens = get_tokens_for_user(user)

        return Response(
            {"message": "Login successful", "tokens": tokens}, status=status.HTTP_200_OK
        )


@extend_schema(tags=["File Upload"])
class FileUploadView(GenericAPIView):
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)
    REQUIRED_COLUMNS = {'name', 'email', 'age'}

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ServiceError(
                detail="Validation error",
                detail_error_response=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type=VALIDATION_ERROR_TYPE,
            )
        
        file = serializer.validated_data["file"]
        df = pd.read_csv(file)
        if set(df.columns) != self.REQUIRED_COLUMNS:
            raise ServiceError(
                detail="Invalid columns",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type=VALIDATION_ERROR_TYPE,
            )
        
        return Response(serializer.data, status=status.HTTP_200_OK)
