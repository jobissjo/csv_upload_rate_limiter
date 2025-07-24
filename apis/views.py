from rest_framework.generics import GenericAPIView
from .serializers import FileUploadSerializer, LoginSerializer, TokenResponseSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import User
from rest_framework import status
from .utils import (
    get_tokens_for_user,
    ServiceError,
    get_formatted_response,
    is_valid_email,
)
from drf_spectacular.utils import extend_schema
from .constants import CLIENT_ERROR_TYPE, VALIDATION_ERROR_TYPE
import pandas as pd
from django.db.models.functions import Lower
import logging

logger = logging.getLogger(__name__)


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
        response = get_formatted_response(data=tokens, message="Login successful")

        return Response(response, status=status.HTTP_200_OK)


@extend_schema(tags=["File Upload"])
class FileUploadView(GenericAPIView):
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)
    REQUIRED_COLUMNS = {"name", "email", "age"}

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

        try:
            df = pd.read_csv(file)
        except Exception as e:
            logger.error(
                f"METHOD: {request.method}, PATH: {request.path}, MESSAGE: {e}"
            )
            raise ServiceError(
                detail="Unable to read a uploaded csv file",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type=VALIDATION_ERROR_TYPE,
            )
        df.columns = df.columns.str.strip().str.lower()
        if df.columns.duplicated().any():
            raise ServiceError(
                detail="Duplicate column names found in uploaded csv file",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type=CLIENT_ERROR_TYPE,
            )
        if not self.REQUIRED_COLUMNS.issubset(set(df.columns)):
            missing_columns = self.REQUIRED_COLUMNS - set(df.columns)
            raise ServiceError(
                detail=f"Missing required columns: {', '.join(missing_columns)}",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type=VALIDATION_ERROR_TYPE,
            )
        

        self._init_required_variables()

        USER_OBJS = []
        try:
            for index, row in df.iterrows():
                is_skipped, normalized_email = self._check_email_validation(row.get("email", ""))
                if is_skipped:
                    continue
                name = row.get("name", "")
                if self._is_invalid_name(name):
                    self.NAME_VALIDATION_FAILED_COUNT += 1
                    continue

                age = row.get("age")
                is_skipped, age = self.check_age_validation(age)
                if is_skipped:
                    continue

                USER_OBJS.append(
                    User(email=normalized_email, name=name, age=age)
                )
                self.EXISTING_MAILS.add(normalized_email)


            User.objects.bulk_create(USER_OBJS)
            detail = {
                "success": [f"{len(USER_OBJS)} user records uploaded successfully"],
                "failed": [
                    f"{self.NULL_EMAIL_VALIDATION_FAILED_COUNT} user records failed due to null email",
                    f"{self.EXISTING_EMAIL_VALIDATION_FAILED_COUNT} user records failed due to existing email",
                    f"{self.NAME_VALIDATION_FAILED_COUNT} user records failed due to invalid name",
                    f"{self.VALID_EMAIL_FAILED_COUNT} user records failed due to invalid email",
                    f"{self.AGE_VALIDATION_FAILED_COUNT} user records failed due to invalid age",
                    f"{self.NULL_EMAIL_VALIDATION_FAILED_COUNT + self.EXISTING_EMAIL_VALIDATION_FAILED_COUNT + self.NAME_VALIDATION_FAILED_COUNT + self.VALID_EMAIL_FAILED_COUNT + self.AGE_VALIDATION_FAILED_COUNT} total user records skipped",
                ],
            }

            response = get_formatted_response(
                data=None, message="File uploaded successfully", detail=detail
            )
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                f"METHOD: {request.method}, PATH: {request.path}, MESSAGE: {e}"
            )
            raise ServiceError(
                detail="Unable to read a uploaded csv file",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type=VALIDATION_ERROR_TYPE,
            )

    def _init_required_variables(self):
        """Initialize required variables"""

        self.NULL_EMAIL_VALIDATION_FAILED_COUNT = 0
        self.EXISTING_EMAIL_VALIDATION_FAILED_COUNT = 0
        self.VALID_EMAIL_FAILED_COUNT = 0
        self.NAME_VALIDATION_FAILED_COUNT = 0
        self.AGE_VALIDATION_FAILED_COUNT = 0
        self.EXISTING_MAILS = set(
            User.objects.annotate(lower_email=Lower("email")).values_list(
                "lower_email", flat=True
            )
        )

    def _check_email_validation(self, email: str):
        """Accept Email and check if it is valid or not. If valid return normalized email else return None."""
        if pd.isna(email):
            self.NULL_EMAIL_VALIDATION_FAILED_COUNT += 1
            return True, None
        normalized_email = email.strip().lower()

        if not is_valid_email(normalized_email):
            self.VALID_EMAIL_FAILED_COUNT += 1
            return True, None
        if normalized_email in self.EXISTING_MAILS:
            self.EXISTING_EMAIL_VALIDATION_FAILED_COUNT += 1
            return True,  None
        return False, normalized_email

    def check_age_validation(self, age):
        """Accept age and check if it is valid or not. If valid return age else return None."""
        if pd.isna(age):
            self.AGE_VALIDATION_FAILED_COUNT += 1
            return True, None
        try:
            age = int(age)
            if age >=0 and age <= 120:
                return False, age
            else:
                self.AGE_VALIDATION_FAILED_COUNT += 1
                return True, None
        except (ValueError, TypeError):
            self.AGE_VALIDATION_FAILED_COUNT += 1
            return True, None
    
    def _is_invalid_name(self, name) -> bool:
        """Accept name and check if it is valid or not. If valid return False else return True."""
        return pd.isna(name) or not str(name).strip()
