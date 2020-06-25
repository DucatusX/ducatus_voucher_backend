from rest_framework import serializers

from ducatus_voucher.transfers.models import Transfer


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['duc_address', 'duc_amount', 'tx_hash', 'transfer_status']
        extra_kwargs = {
            'tx_hash': {'read_only': True},
            'transfer_status': {'read_only': True},
        }
