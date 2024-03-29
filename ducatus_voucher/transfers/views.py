import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone

from ducatus_voucher.transfers.api import validate_voucher, make_voucher_transfer
from ducatus_voucher.transfers.serializers import TransferSerializer
from ducatus_voucher.vouchers.models import FreezingVoucher
from ducatus_voucher.freezing.api import generate_cltv, save_vout_number


class TransferRequest(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'activation_code': openapi.Schema(type=openapi.TYPE_STRING),
                'duc_address': openapi.Schema(type=openapi.TYPE_STRING),
                'duc_public_key': openapi.Schema(type=openapi.TYPE_STRING),
                'wallet_id': openapi.Schema(type=openapi.TYPE_STRING),
                'private_path': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['activation_code', 'duc_address', 'duc_public_key', 'wallet_id', 'private_path']
        ),
        responses={200: TransferSerializer()},
    )
    def post(self, request: Request):
        data = request.data
        print(f'VOUCHER ACTIVATION: received message {data} at {timezone.now()}', flush=True)

        activation_code = data['activation_code']

        if activation_code.startswith('REF'):
            crowdsale_url = 'https://tokenization.centuriongm.com/api/v1/activate_referral_voucher'
            crowdsale_response = requests.post(crowdsale_url, data=data)
            crowdsale_response_status = crowdsale_response.status_code

            if crowdsale_response_status in (200, 403):
                return Response(crowdsale_response.json(), status=crowdsale_response_status)

        voucher = validate_voucher(activation_code)

        duc_address = data['duc_address']
        user_public_key = data['duc_public_key']
        wallet_id = data['wallet_id']
        private_path = data['private_path']


        if not voucher.lock_days:
            transfer = make_voucher_transfer(voucher, duc_address)
            return Response(TransferSerializer().to_representation(transfer))

        cltv_details = generate_cltv(user_public_key, voucher.lock_days, private_path)

        freezing_details = FreezingVoucher()
        freezing_details.cltv_details = cltv_details
        freezing_details.wallet_id = wallet_id
        freezing_details.user_duc_address = duc_address
        freezing_details.save()

        voucher.freezing_details = freezing_details
        voucher.freezing_details_id = freezing_details.pk
        voucher.save()

        transfer = make_voucher_transfer(voucher, cltv_details.locked_duc_address)
        save_vout_number(transfer)

        return Response(TransferSerializer().to_representation(transfer))
