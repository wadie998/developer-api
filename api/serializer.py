from models.model import JhiUser
from rest_framework import serializers


class DefaultSerializer(serializers.Serializer):
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class AuthenticateSerializer(DefaultSerializer):
    username = serializers.CharField(
        max_length=255,
    )
    password = serializers.CharField(
        max_length=255,
    )


class ApiResponseViewSerializer(DefaultSerializer):
    sort = serializers.CharField(max_length=255, required=False)
    filter_param = serializers.CharField(max_length=255, required=False)
    page = serializers.IntegerField(default=0)
    size = serializers.IntegerField(default=3)


class JhiSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    image_url = serializers.CharField()
    activated = serializers.CharField()
    lang_key = serializers.CharField()
    activation_key = serializers.BooleanField()

    class Meta:
        model = JhiUser
