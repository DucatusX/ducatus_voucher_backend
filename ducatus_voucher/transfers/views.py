from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from ducatus_voucher.transfers.api import validate_voucher, make_transfer
from ducatus_voucher.transfers.serializers import TransferSerializer


class TransferRequest(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'activation_code': openapi.Schema(type=openapi.TYPE_STRING),
                'duc_address': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['activation_code', 'duc_address']
        ),
        responses={200: TransferSerializer()},
    )
    def post(self, request):
        activation_code = request.data.get('activation_code')
        duc_address = request.data.get('duc_address')

        voucher = validate_voucher(activation_code)
        transfer = make_transfer(voucher, duc_address)

        return Response(TransferSerializer().to_representation(transfer))
