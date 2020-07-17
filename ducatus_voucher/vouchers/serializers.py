from rest_framework import serializers

from ducatus_voucher.vouchers.models import Voucher


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
