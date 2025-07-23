from rest_framework.views import exception_handler
import logging
from rest_framework.response import Response

from apis.utils import ServiceError

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    request = context.get("request")

    if isinstance(exc, ServiceError):
        logger.error(f'METHOD: {request.method}, PATH: {request.path}, STATUS_CODE: {exc.status_code}, MESSAGE: {exc.detail}')

        return Response({
            "message": exc.detail,
            "error_type": exc.error_type,
            "detail": exc.detail_error_response
        }, status=exc.status_code)

    response = exception_handler(exc, context)

    if response is not None:
        logger.error(f'METHOD: {request.method}, PATH: {request.path}, STATUS_CODE: {response.status_code}, MESSAGE: {response.data}')

    return response