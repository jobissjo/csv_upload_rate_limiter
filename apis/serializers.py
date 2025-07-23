from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        if not data.get('email') or not data.get('password'):
            raise serializers.ValidationError("Email and password are required.")
        return data
    

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only .csv files are allowed.")
        return value

class BaseApiResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    success = serializers.BooleanField()

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class TokenResponseSerializer(BaseApiResponseSerializer):
    data = TokenSerializer()



