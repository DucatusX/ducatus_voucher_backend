from django.db import models

from ducatus_voucher.freezing.models import CltvDetails


class Deposit(models.Model):
    wallet_id = models.CharField(max_length=50)
    cltv_details = models.OneToOneField(CltvDetails, null=True, default=None, on_delete=models.CASCADE)
    lock_days = models.IntegerField()
    dividends = models.IntegerField(default=5)
    user_duc_address = models.CharField(max_length=50)
