from rest_framework import serializers

from ducatus_voucher.freezing.models import FreezingVoucher


class FreezingVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezingVoucher
        fields = '__all__'
