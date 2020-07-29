from django.db import models
import secrets

from ducatus_voucher.freezing.models import CltvDetails
from ducatus_voucher.consts import MAX_DIGITS


class FreezingVoucher(models.Model):
    wallet_id = models.CharField(max_length=50)
    cltv_details = models.OneToOneField(CltvDetails, null=True, default=None, on_delete=models.CASCADE)
    user_duc_address = models.CharField(max_length=50)


class Voucher(models.Model):
    voucher_code = models.CharField(max_length=50, unique=True)
    activation_code = models.CharField(max_length=50, unique=True, default=secrets.token_urlsafe)
    usd_amount = models.FloatField()
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    publish_date = models.DateTimeField(auto_now_add=True)
    activation_date = models.DateTimeField(null=True, default=None)
    lock_days = models.IntegerField(default=0)
    freezing_details = models.OneToOneField(
        FreezingVoucher,
        on_delete=models.SET_NULL,
        null=True, default=None,
        related_name='voucher'
    )


class VoucherInput(models.Model):
    voucher = models.ForeignKey(FreezingVoucher, on_delete=models.CASCADE)
    tx_vout = models.IntegerField()
    mint_tx_hash = models.CharField(max_length=100)
    spent_tx_hash = models.CharField(max_length=100, null=True, default=None)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=0)
    minted_at = models.DateTimeField(auto_now_add=True)
    spent_at = models.DateTimeField(null=True, default=None)
