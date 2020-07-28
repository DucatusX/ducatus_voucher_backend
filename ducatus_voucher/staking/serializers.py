from rest_framework import serializers

from ducatus_voucher.staking.models import Deposit
from ducatus_voucher.freezing.serializers import CltvDetailsSerializer


class DepositSerializer(serializers.ModelSerializer):
    cltv_details = CltvDetailsSerializer()

    class Meta:
        model = Deposit
        fields = ('id', 'wallet_id', 'cltv_details', 'lock_days', 'dividends', 'user_duc_address')
