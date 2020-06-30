from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

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
                'duc_amount': openapi.Schema(type=openapi.TYPE_INTEGER),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
            required=['voucher_code', 'duc_amount']
        ),
        responses={200: VoucherSerializer()},
    )
    def create(self, request, *args, **kwargs):
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
                'duc_amount': openapi.Schema(type=openapi.TYPE_INTEGER),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
            required=['voucher_code', 'duc_amount']
        ),
        responses={200: VoucherSerializer()},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
