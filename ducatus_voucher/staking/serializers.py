import datetime
from django.utils import timezone

from rest_framework import serializers

from ducatus_voucher.staking.models import Deposit, DepositInput
from ducatus_voucher.freezing.serializers import CltvDetailsSerializer
from ducatus_voucher.freezing.api import get_duc_transfer_fee


class DepositInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositInput
        fields = ('tx_vout', 'mint_tx_hash', 'spent_tx_hash', 'amount')


class DepositSerializer(serializers.ModelSerializer):
    cltv_details = CltvDetailsSerializer(read_only=True)
    depositinput_set = DepositInputSerializer(many=True, read_only=True)

    class Meta:
        model = Deposit
        fields = ('id', 'wallet_id', 'cltv_details', 'lock_months', 'dividends', 'user_duc_address', 'depositinput_set')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['tx_fee'] = get_duc_transfer_fee()
        res['ready_to_withdraw'] = instance.cltv_details.lock_time < (
                    timezone.now() + datetime.timedelta(minutes=10)).timestamp()
        return res
