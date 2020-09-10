import secrets

import requests
from django.db import models

from ducatus_voucher import settings_local
from ducatus_voucher.consts import MAX_DIGITS
from ducatus_voucher.freezing.models import CltvDetails


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
    # Filled only if it was created by card payment. If yes, it will register in lottery
    charge_id = models.IntegerField(null=True)

    def register_in_lottery_by_charge(self, transfer):
        print(f'Try to register Voucher {self.id} in lottery', flush=True)
        domain = getattr(settings_local, 'EXCHANGE_DOMAIN', None)
        if not domain:
            raise NameError(f'Cant register in lottery voucher with id {self.id}, '
                            'EXCHANGE_DOMAIN should be defined in settings_local.py')

        url = 'https://{}/api/v1/register_voucher_in_lottery/'.format(domain)
        data = {
            "charge_id": self.charge_id,
            "transfer": {
                "duc_address": transfer.duc_address,
                "tx_hash": transfer.tx_hash,
                "amount": int(transfer.duc_amount),
            },
        }
        r = requests.post(url, json=data)
        if r.status_code == 200:
            print(f'Voucher {self.id} register in lottery successfully', flush=True)
        else:
            print(f'Warning! Cant register voucher {self.id} in lottery!', flush=True)


class VoucherInput(models.Model):
    voucher = models.ForeignKey(FreezingVoucher, on_delete=models.CASCADE)
    tx_vout = models.IntegerField()
    mint_tx_hash = models.CharField(max_length=100)
    spent_tx_hash = models.CharField(max_length=100, null=True, default=None)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=0)
    minted_at = models.DateTimeField(auto_now_add=True)
    spent_at = models.DateTimeField(null=True, default=None)


class UnlockVoucherTx(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    tx_hash = models.CharField(max_length=100, unique=True)
