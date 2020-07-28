from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter

from ducatus_voucher.vouchers.views import VoucherViewSet
from ducatus_voucher.transfers.views import TransferRequest
from ducatus_voucher.vouchers.views import get_withdraw_info, get_frozen_vouchers
from ducatus_voucher.staking.views import generate_deposit, get_deposits


schema_view = get_schema_view(
    openapi.Info(
        title="Ducatus vouchers API",
        default_version='v1',
        description="API for ducatus voucher program",
        contact=openapi.Contact(email="ephdtrg@mintyclouds.in"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter(trailing_slash=True)
router.register(r'vouchers', VoucherViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/v1/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^api/v1/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/v1/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'^api/v1/transfer/', TransferRequest.as_view()),
    url(r'^api/v1/transfer/', TransferRequest.as_view()),
    url(r'^api/v1/get_withdraw_info/', get_withdraw_info),
    url(r'^api/v1/get_frozen_vouchers/', get_frozen_vouchers),
    url(r'^api/v1/generate_deposit/', generate_deposit),
    url(r'^api/v1/get_deposits/', get_deposits),
    url(r'^api/v1/', include(router.urls)),
    # url(r'^api/v1/vouchers_list/', VoucherListRequest.as_view()),
    url(r'^api/v1/rest-auth/', include('rest_auth.urls')),
]
