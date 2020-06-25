from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied, APIException
from django.utils import timezone

from ducatus_voucher.vouchers.models import Voucher
from ducatus_voucher.transfers.models import Transfer
from ducatus_voucher.litecoin_rpc import DucatuscoreInterface, DucatuscoreInterfaceException


def validate_voucher(activation_code):
    try:
        voucher = Voucher.objects.get(activation_code=activation_code)
    except ObjectDoesNotExist:
        raise PermissionDenied(detail='Invalid activation code')

    if not voucher.is_active:
        raise PermissionDenied(detail='This voucher is not active')

    if voucher.is_used:
        raise PermissionDenied(detail='This voucher already used')

    return voucher


def make_transfer(voucher, duc_address):
    transfer = Transfer(voucher=voucher, duc_amount=voucher.duc_amount, duc_address=duc_address)
    transfer.save()

    try:
        rpc = DucatuscoreInterface()
        tx_hash = rpc.node_transfer(duc_address, voucher.duc_amount)
    except DucatuscoreInterfaceException as err:
        raise APIException(detail=str(err))

    transfer.tx_hash = tx_hash
    transfer.transfer_status = 'WAITING_FOR_CONFIRM'
    transfer.save()

    voucher.is_used = True
    voucher.activation_date = timezone.now()
    voucher.save()

    return transfer
