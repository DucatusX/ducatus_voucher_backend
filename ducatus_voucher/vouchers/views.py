from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from ducatus_voucher.vouchers.models import Voucher
from ducatus_voucher.vouchers.serializers import VoucherSerializer


class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'voucher_code': openapi.Schema(type=openapi.TYPE_STRING),
                'duc_amount': openapi.Schema(type=openapi.TYPE_STRING),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
            required=['voucher_code', 'duc_amount']
        ),
        responses={200: VoucherSerializer()},
    )
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'voucher_code': openapi.Schema(type=openapi.TYPE_STRING),
                'duc_amount': openapi.Schema(type=openapi.TYPE_STRING),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
            required=['id']
        ),
        responses={200: VoucherSerializer()},
    )
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
