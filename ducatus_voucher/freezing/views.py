from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ducatus_voucher.freezing.serializers import FreezingVoucherSerializer
from ducatus_voucher.freezing.api import get_redeem_info, get_unused_frozen_vouchers


@swagger_auto_schema(
        method='get',
        manual_parameters=[openapi.Parameter('voucher_id', openapi.IN_QUERY, type=openapi.TYPE_STRING)],
        responses={200: FreezingVoucherSerializer()},
    )
@api_view(http_method_names=['GET'])
def get_withdraw_info(request: Request):
    voucher_id = request.query_params.get('voucher_id')

    frozen_voucher = get_redeem_info(voucher_id)
    response_data = FreezingVoucherSerializer().to_representation(frozen_voucher)

    return Response(response_data)


@swagger_auto_schema(
        method='get',
        manual_parameters=[openapi.Parameter('wallet_id', openapi.IN_QUERY, type=openapi.TYPE_STRING)],
        responses={200: FreezingVoucherSerializer()},
    )
@api_view(http_method_names=['GET'])
def get_frozen_vouchers(request: Request):
    wallet_id = request.query_params.get('wallet_id')

    unused_frozen_vouchers = get_unused_frozen_vouchers(wallet_id)
    response_data = FreezingVoucherSerializer(many=True).to_representation(unused_frozen_vouchers)

    return Response(response_data)
