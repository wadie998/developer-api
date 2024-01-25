from rest_framework import serializers


class DefaultSerializer(serializers.Serializer):
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class AuthenticateSerializer(DefaultSerializer):
    username = serializers.UUIDField()
    password = serializers.UUIDField()


class ApiResponseViewSerializer(DefaultSerializer):
    sort = serializers.CharField(max_length=255, required=False)
    filter_param = serializers.CharField(max_length=255, required=False)
    page = serializers.IntegerField(default=1)
    size = serializers.IntegerField(default=10)
