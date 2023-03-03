from rest_framework import serializers


class PublishSerializer(serializers.Serializer):
    """
    推送 notify 輸入
    """
    message = serializers.CharField(label="要發送的訊息")


class WebhookSerializer(serializers.Serializer):
    """
    Line notify webhook use
    """
    code = serializers.CharField()
    state = serializers.UUIDField()
