from rest_framework import serializers


class DefaultSerializer(serializers.Serializer):
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class AuthenticateSerializer(DefaultSerializer):
    username = serializers.UUIDField()
    password = serializers.UUIDField()
