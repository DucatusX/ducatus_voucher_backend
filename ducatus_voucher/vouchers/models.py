from django.db import models
import secrets


class Voucher(models.Model):
    voucher_code = models.CharField(max_length=50, unique=True)
    activation_code = models.CharField(max_length=50, unique=True, default=secrets.token_urlsafe)
    usd_amount = models.FloatField()
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    publish_date = models.DateTimeField(auto_now_add=True)
    activation_date = models.DateTimeField(null=True, default=None)
