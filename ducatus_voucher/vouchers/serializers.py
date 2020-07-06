from rest_framework import serializers

from ducatus_voucher.vouchers.models import Voucher
from ducatus_voucher.transfers.serializers import TransferSerializer
from ducatus_voucher.consts import DECIMALS


class VoucherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voucher
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'activation_code': {'read_only': True},
            'is_used': {'read_only': True},
            'publish_date': {'read_only': True},
            'activation_date': {'read_only': True}
        }
