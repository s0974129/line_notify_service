from django.db import models


class Subscriber(models.Model):
    """
    訂閱者
    """
    account = models.CharField(max_length=20)
    state = models.UUIDField(null=True)
    code = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100, default="")
    message = models.CharField(max_length=500, default="")
    subscribed = models.BooleanField(default=False)
