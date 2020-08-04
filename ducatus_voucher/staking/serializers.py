import datetime
from django.utils import timezone

from rest_framework import serializers

from ducatus_voucher.staking.models import Deposit, DepositInput
from ducatus_voucher.freezing.serializers import CltvDetailsSerializer
from ducatus_voucher.freezing.api import get_duc_transfer_fee
from ducatus_voucher.consts import DECIMALS


class DepositInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositInput
        fields = ('tx_vout', 'mint_tx_hash', 'spent_tx_hash', 'amount', 'minted_at')


class DepositSerializer(serializers.ModelSerializer):
    cltv_details = CltvDetailsSerializer(read_only=True)
    depositinput_set = DepositInputSerializer(many=True, read_only=True)

    class Meta:
        model = Deposit
        fields = ('id', 'wallet_id', 'cltv_details', 'lock_months', 'dividends', 'user_duc_address', 'depositinput_set')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['tx_fee'] = get_duc_transfer_fee()
        res['ready_to_withdraw'] = False
        if instance.depositinput_set.count() > 0:
            first_input = instance.depositinput_set.order_by('minted_at').first()
            deposit_at = first_input.minted_at
            ended_at = deposit_at + datetime.timedelta(minutes=instance.lock_months)
            if ended_at <= timezone.now():
                res['ready_to_withdraw'] = True
            res['deposited_at'] = deposit_at.timestamp()
            res['ended_at'] = ended_at.timestamp()
            res['duc_amount'] = int(first_input.amount) // DECIMALS['DUC']

        res['depositinput_set'] = sorted(res['depositinput_set'], key=lambda x: x['minted_at'])

        return res
