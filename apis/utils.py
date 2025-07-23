from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import APIException


def get_tokens_for_user(user):
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
