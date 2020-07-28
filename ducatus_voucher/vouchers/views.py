from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view

from ducatus_voucher.vouchers.models import Voucher
from ducatus_voucher.vouchers.serializers import VoucherSerializer, FreezingVoucherSerializer
from ducatus_voucher.freezing.api import get_redeem_info, get_unused_frozen_vouchers


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

    frozen_voucher = get_redeem_info(voucher_id)
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
