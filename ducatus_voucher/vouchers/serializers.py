from rest_framework import serializers

from ducatus_voucher.vouchers.models import Voucher, FreezingVoucher
from ducatus_voucher.freezing.api import get_duc_transfer_fee
from ducatus_voucher.consts import DECIMALS


class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ('id', 'voucher_code', 'activation_code', 'usd_amount', 'is_active', 'is_used', 'publish_date',
                  'activation_date', 'lock_days',)
        extra_kwargs = {
            'id': {'read_only': True},
            'activation_code': {'read_only': True},
            'is_used': {'read_only': True},
            'publish_date': {'read_only': True},
            'activation_date': {'read_only': True}
        }


class FreezingVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezingVoucher
        fields = '__all__'

    def to_representation(self, instance):
        res = super().to_representation(instance)

        cltv_instance = res.cltv_details
        res['withdrawn'] = cltv_instance.withdrawn
        res['lock_time'] = cltv_instance.lock_time
        res['redeem_script'] = cltv_instance.redeem_script
        res['locked_duc_address'] = cltv_instance.locked_duc_address
        res['user_public_key'] = cltv_instance.user_public_key
        res['frozen_at'] = cltv_instance.frozen_at

        transfer_instance = instance.voucher.transfer_set.first()
        res['duc_amount'] = int(transfer_instance.duc_amount) // DECIMALS['DUC']
        res['usd_amount'] = instance.voucher.usd_amount
        res['tx_hash'] = transfer_instance.tx_hash
        res['vout_number'] = transfer_instance.vout_number
        res['sending_amount'] = int(transfer_instance.duc_amount - get_duc_transfer_fee())

        return res
