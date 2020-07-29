from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound

from ducatus_voucher.freezing.api import generate_cltv
from ducatus_voucher.staking.models import Deposit
from ducatus_voucher.staking.serializers import DepositSerializer
from ducatus_voucher.consts import DIVIDENDS_INFO


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'duc_address': openapi.Schema(type=openapi.TYPE_STRING),
            'duc_public_key': openapi.Schema(type=openapi.TYPE_STRING),
            'wallet_id': openapi.Schema(type=openapi.TYPE_STRING),
            'lock_months': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
        required=['duc_address', 'duc_public_key', 'wallet_id', 'lock_months']
    ),
    responses={200: DepositSerializer()},
)
@api_view(http_method_names=['POST'])
def generate_deposit(request):
    duc_address = request.data.get('duc_address')
    user_public_key = request.data.get('duc_public_key')
    wallet_id = request.data.get('wallet_id')
    lock_months = request.data.get('lock_months')

    if lock_months not in DIVIDENDS_INFO:
        raise ValidationError('lock months must be in [5, 8, 13]')

    cltv_details = generate_cltv(user_public_key, {'minutes': lock_months})

    deposit = Deposit()
    deposit.cltv_details = cltv_details
    deposit.wallet_id = wallet_id
    deposit.lock_months = lock_months
    deposit.user_duc_address = duc_address
    deposit.dividends = DIVIDENDS_INFO[lock_months]
    deposit.save()

    response_data = DepositSerializer().to_representation(deposit)

    return Response(response_data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[openapi.Parameter('wallet_ids', openapi.IN_QUERY, type=openapi.TYPE_ARRAY,
                                         items=openapi.Items(type=openapi.TYPE_STRING))],
    responses={200: DepositSerializer()},
)
@api_view(http_method_names=['GET'])
def get_deposits(request):
    wallet_ids = request.query_params.get('wallet_ids').split(',')
    deposits = Deposit.objects.filter(wallet_id__in=wallet_ids, cltv_details__withdrawn=False)

    response_data = DepositSerializer(many=True).to_representation(deposits)

    return Response(response_data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[openapi.Parameter('deposit_id', openapi.IN_QUERY, type=openapi.TYPE_STRING)],
    responses={200: DepositSerializer()},
)
@api_view(http_method_names=['GET'])
def get_deposit_info(request: Request):
    deposit_id = request.query_params.get('deposit_id')

    try:
        deposit = Deposit.objects.get(id=deposit_id)
    except Deposit.DoesNotExist:
        raise NotFound

    response_data = DepositSerializer().to_representation(deposit)

    return Response(response_data)
