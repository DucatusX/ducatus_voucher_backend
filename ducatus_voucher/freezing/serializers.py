from rest_framework import serializers

from ducatus_voucher.freezing.models import FreezingVoucher
from ducatus_voucher.consts import DECIMALS


class FreezingVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezingVoucher
        fields = '__all__'

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['duc_amount'] = int(instance.voucher.transfer_set.first().duc_amount) // DECIMALS['DUC']
        res['usd_amount'] = instance.voucher.usd_amount
