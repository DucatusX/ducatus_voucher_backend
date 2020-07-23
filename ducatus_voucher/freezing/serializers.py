from rest_framework import serializers

from ducatus_voucher.freezing.models import FreezingVoucher
from ducatus_voucher.freezing.api import get_duc_transfer_fee
from ducatus_voucher.consts import DECIMALS


class FreezingVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezingVoucher
        fields = '__all__'

    def to_representation(self, instance):
        res = super().to_representation(instance)
        transfer_instance = instance.voucher.transfer_set.first()
        res['duc_amount'] = int(transfer_instance.duc_amount) // DECIMALS['DUC']
        res['usd_amount'] = instance.voucher.usd_amount
        res['tx_hash'] = transfer_instance.tx_hash
        res['vout_number'] = transfer_instance.tx_hash
        res['sending_amount'] = int(transfer_instance.duc_amount - get_duc_transfer_fee())

        return res
