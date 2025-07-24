from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import APIException
from .models import User
from typing import Any, Dict, Optional
import re


def get_tokens_for_user(user: User):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class ServiceError(APIException):
    status_code = 500
    default_detail = "Internal Server Error"
    default_code = "server_error"
    error_type = "server_error"

    def __init__(
        self,
        detail=None,
        status_code=None,
        detail_error_response=None,
        error_type=None,
        code=None,
    ):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        if status_code is not None:
            self.status_code = status_code

        self.error_type = error_type
        self.detail_error_response = detail_error_response
        super().__init__(detail, code)


def get_formatted_response(
    data: Any, message: str = None, detail: Optional[Dict[str, Any]] = None
):
    return {"data": data, "message": message, "detail": detail}


EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def is_valid_email(email: str) -> bool:
    return re.match(EMAIL_REGEX, email) is not None
