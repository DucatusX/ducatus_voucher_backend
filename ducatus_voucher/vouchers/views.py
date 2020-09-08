from django.db.utils import IntegrityError

from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied

from ducatus_voucher.vouchers.models import Voucher, FreezingVoucher
from ducatus_voucher.vouchers.serializers import VoucherSerializer, FreezingVoucherSerializer
from ducatus_voucher.freezing.api import get_unused_frozen_vouchers
from ducatus_voucher.litecoin_rpc import DucatuscoreInterface, JSONRPCException
from ducatus_voucher.vouchers.models import UnlockVoucherTx
from ducatus_voucher.settings import API_KEY


class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'voucher_code': openapi.Schema(type=openapi.TYPE_STRING),
                'usd_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'lock_days': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['voucher_code', 'usd_amount']
        ),
        responses={200: VoucherSerializer()},
    )
    def create(self, request: Request, *args, **kwargs):
        if isinstance(request.data, list):
            voucher_list = request.data
            for voucher in voucher_list:
                serializer = self.get_serializer(data=voucher)
                if serializer.is_valid():
                    self.perform_create(serializer)
                else:
                    raise ValidationError(detail={'description': serializer.errors, 'voucher': voucher})
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        else:
            return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'voucher_code': openapi.Schema(type=openapi.TYPE_STRING),
                'usd_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'lock_days': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['voucher_code', 'usd_amount']
        ),
        responses={200: VoucherSerializer()},
    )
    def update(self, request: Request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


@swagger_auto_schema(
    method='get',
    manual_parameters=[openapi.Parameter('voucher_id', openapi.IN_QUERY, type=openapi.TYPE_STRING)],
    responses={200: FreezingVoucherSerializer()},
)
@api_view(http_method_names=['GET'])
def get_withdraw_info(request: Request):
    voucher_id = request.query_params.get('voucher_id')

    try:
        frozen_voucher = FreezingVoucher.objects.get(id=voucher_id)
    except FreezingVoucher.DoesNotExist:
        raise NotFound

    response_data = FreezingVoucherSerializer().to_representation(frozen_voucher)

    return Response(response_data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[openapi.Parameter('wallet_ids', openapi.IN_QUERY, type=openapi.TYPE_ARRAY,
                                         items=openapi.Items(type=openapi.TYPE_STRING))],
    responses={200: FreezingVoucherSerializer()},
)
@api_view(http_method_names=['GET'])
def get_frozen_vouchers(request: Request):
    wallet_ids = request.query_params.get('wallet_ids').split(',')

    unused_frozen_vouchers = get_unused_frozen_vouchers(wallet_ids)
    response_data = FreezingVoucherSerializer(many=True).to_representation(unused_frozen_vouchers)

    return Response(response_data)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'raw_tx_hex': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['raw_tx_hex']
    ),
)
@api_view(http_method_names=['POST'])
def send_raw_transaction(request):
    raw_tx_hex = request.data.get('raw_tx_hex')

    try:
        interface = DucatuscoreInterface()
        tx_hash = interface.rpc.sendrawtransaction(raw_tx_hex)
        print('unlock tx hash', tx_hash, flush=True)
        unlock_tx = UnlockVoucherTx(tx_hash=tx_hash)
        unlock_tx.save()
    except IntegrityError:
        raise PermissionDenied(detail='-27: transaction already in block chain')
    except JSONRPCException as err:
        raise PermissionDenied(detail=str(err))

    return Response({'success': True, 'tx_hash': tx_hash})


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'api_key': openapi.Schema(type=openapi.TYPE_STRING),
            'voucher_code': openapi.Schema(type=openapi.TYPE_STRING),
            'usd_amount': openapi.Schema(type=openapi.TYPE_INTEGER),
            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'lock_days': openapi.Schema(type=openapi.TYPE_INTEGER),
            'charge_id': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        },
        required=['api_key', 'voucher_code', 'usd_amount']
    ),
    responses={200: VoucherSerializer()}
)
@api_view(http_method_names=['POST'])
def register_voucher(request: Request):
    api_key = request.data.get('api_key')
    if api_key != API_KEY:
        raise PermissionDenied(detail='invalid api key')

    request.data.pop('api_key')
    voucher_data = request.data

    serializer = VoucherSerializer(data=voucher_data)
    if serializer.is_valid():
        serializer.save()
    else:
        raise ValidationError(detail={'description': serializer.errors, 'voucher': voucher_data})

    return Response(serializer.data)
