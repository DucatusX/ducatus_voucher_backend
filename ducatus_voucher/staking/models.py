from django.db import models

from ducatus_voucher.freezing.models import CltvDetails
from ducatus_voucher.consts import MAX_DIGITS


class Deposit(models.Model):
    wallet_id = models.CharField(max_length=50)
    cltv_details = models.OneToOneField(CltvDetails, null=True, default=None, on_delete=models.CASCADE)
    lock_days = models.IntegerField()
    dividends = models.IntegerField(default=5)
    user_duc_address = models.CharField(max_length=50)


class DepositInput(models.Model):
    deposit = models.ForeignKey(Deposit, on_delete=models.CASCADE)
    tx_vout = models.IntegerField()
    mint_tx_hash = models.CharField(max_length=100)
    spent_tx_hash = models.CharField(max_length=100, null=True, default=None)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=0)
