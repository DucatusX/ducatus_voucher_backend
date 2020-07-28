import os
import sys
import time
import json
import traceback
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ducatus_voucher.settings')
import django

django.setup()

from django.utils import timezone

from ducatus_voucher.litecoin_rpc import DucatuscoreInterface
from ducatus_voucher.freezing.models import CltvDetails
from ducatus_voucher.vouchers.models import FreezingVoucher, VoucherInput
from ducatus_voucher.staking.models import Deposit, DepositInput
from ducatus_voucher.settings import WITHDRAW_CHECKER_TIMEOUT

DUC_API_URL = 'https://ducapi.rocknblock.io/api/DUC/mainnet/address/{duc_address}'


def voucher_checker():
    vouchers_to_withdraw = FreezingVoucher.objects.filter(cltv_details__withdrawn=False,
                                                          cltv_details__lock_time__lt=timezone.now().timestamp())

    if not vouchers_to_withdraw:
        print('all vouchers have withdrawn at {}\n'.format(timezone.now()), flush=True)

    for voucher in vouchers_to_withdraw:
        lock_address = voucher.cltv_details.locked_duc_address
        tx_inputs = json.loads(requests.get(DUC_API_URL.format(duc_address=lock_address)).content.decode())

        for tx_input in tx_inputs:
            mint_tx_hash = tx_input['mintTxid']
            spent_tx_hash = tx_input['spentTxid']
            try:
                voucher_input = VoucherInput.objects.get(mint_tx_hash=mint_tx_hash)
                if not voucher_input.spent_tx_hash:
                    voucher_input.spent_tx_hash = spent_tx_hash
            except VoucherInput.DoesNotExist:
                voucher_input = VoucherInput()
                voucher_input.deposit = voucher
                voucher_input.mint_tx_hash = mint_tx_hash
                voucher_input.tx_vout = tx_input['mintIndex']
                voucher_input.amount = tx_input['value']
                if spent_tx_hash:
                    voucher_input.spent_tx_hash = spent_tx_hash

            voucher_input.save()

        if all([deposit_input.spent_tx_hash for deposit_input in voucher.depositinput_set.all()]):
            voucher.cltv_details.withdrawn = False
            voucher.cltv_details.save()
            print('deposit with id {id} withdrawn at {time}\n'.format(id=voucher.id, time=timezone.now()), flush=True)
        else:
            print('not all inputs spent in deposit with {id} at {time}\n'.format(id=voucher.id, time=timezone.now()),
                  flush=True)


def deposit_checker():
    deposits_to_withdraw = Deposit.objects.filter(cltv_details__withdrawn=False,
                                                  cltv_details__lock_time__lt=timezone.now().timestamp())

    if not deposits_to_withdraw:
        print('all deposits have withdrawn at {}\n'.format(timezone.now()), flush=True)

    for deposit in deposits_to_withdraw:
        lock_address = deposit.cltv_details.locked_duc_address
        tx_inputs = json.loads(requests.get(DUC_API_URL.format(duc_address=lock_address)).content.decode())

        for tx_input in tx_inputs:
            mint_tx_hash = tx_input['mintTxid']
            spent_tx_hash = tx_input['spentTxid']
            try:
                deposit_input = DepositInput.objects.get(mint_tx_hash=mint_tx_hash)
                if not deposit_input.spent_tx_hash:
                    deposit_input.spent_tx_hash = spent_tx_hash
            except DepositInput.DoesNotExist:
                deposit_input = DepositInput()
                deposit_input.deposit = deposit
                deposit_input.mint_tx_hash = mint_tx_hash
                deposit_input.tx_vout = tx_input['mintIndex']
                deposit_input.amount = tx_input['value']
                if spent_tx_hash:
                    deposit_input.spent_tx_hash = spent_tx_hash

            deposit_input.save()

        if all([deposit_input.spent_tx_hash for deposit_input in deposit.depositinput_set.all()]):
            deposit.cltv_details.withdrawn = False
            deposit.cltv_details.save()
            print('deposit with id {id} withdrawn at {time}\n'.format(id=deposit.id, time=timezone.now()), flush=True)
        else:
            print('not all inputs spent in deposit with {id} at {time}\n'.format(id=deposit.id, time=timezone.now()),
                  flush=True)


if __name__ == '__main__':
    while True:
        deposit_checker()
        voucher_checker()
        time.sleep(WITHDRAW_CHECKER_TIMEOUT)
