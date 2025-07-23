from rest_framework.generics import GenericAPIView
from .serializers import FileUploadSerializer, LoginSerializer, TokenResponseSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import User
from rest_framework import status
from .utils import get_tokens_for_user
from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Auth'], responses={200: TokenResponseSerializer})
class GetTokenView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"message": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({"message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_active:
            return Response({"message": "User is not active"}, status=status.HTTP_400_BAD_REQUEST)
        
        tokens = get_tokens_for_user(user)

        return Response({'message': 'Login successful', 'tokens': tokens}, status=status.HTTP_200_OK)


class FileUploadView(GenericAPIView):
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()
