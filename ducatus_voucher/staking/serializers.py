from rest_framework import serializers

from ducatus_voucher.staking.models import Deposit, DepositInput
from ducatus_voucher.freezing.serializers import CltvDetailsSerializer


class DepositInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositInput
        fields = '__all__'


class DepositSerializer(serializers.ModelSerializer):
    cltv_details = CltvDetailsSerializer(read_only=True)
    deposit_inputs = DepositInputSerializer(many=True, read_only=True)

    class Meta:
        model = Deposit
        fields = ('id', 'wallet_id', 'cltv_details', 'lock_days', 'dividends', 'user_duc_address', 'deposit_inputs')
