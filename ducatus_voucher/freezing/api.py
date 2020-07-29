import os
import datetime
from django.utils import timezone

from rest_framework.exceptions import NotFound

from ducatus_voucher.litecoin_rpc import DucatuscoreInterface
from ducatus_voucher.freezing.models import CltvDetails
from ducatus_voucher.transfers.models import Transfer
from ducatus_voucher.vouchers.models import FreezingVoucher
from ducatus_voucher.settings import BACKEND_PUBLIC_KEY
from ducatus_voucher.settings import CLTV_DIR


def get_unused_frozen_vouchers(wallet_ids):
    vouchers = FreezingVoucher.objects.filter(wallet_id__in=wallet_ids, cltv_details__withdrawn=False)
    return vouchers


def save_cltv_data(frozen_at, redeem_script, locked_duc_address, user_public_key, lock_time):
    cltv_details = CltvDetails()
    cltv_details.lock_time = lock_time
    cltv_details.redeem_script = redeem_script
    cltv_details.locked_duc_address = locked_duc_address
    cltv_details.user_public_key = user_public_key
    cltv_details.frozen_at = frozen_at
    cltv_details.save()

    print('cltv generated', cltv_details.__dict__, flush=True)

    return cltv_details


def generate_cltv(receiver_public_key, lock_days):
    backend_public_key = BACKEND_PUBLIC_KEY
    frozen_at = timezone.now()
    lock_date = frozen_at + datetime.timedelta(minutes=lock_days)
    lock_time = int(lock_date.timestamp())

    bash_command = 'node {script_path} {receiver_public_key} {backend_public_key} {lock_time} {files_dir}' \
        .format(script_path=os.path.join(CLTV_DIR, 'cltv_generation.js'), receiver_public_key=receiver_public_key,
                backend_public_key=backend_public_key, lock_time=lock_time, files_dir=CLTV_DIR)
    if os.system(bash_command):
        raise Exception('error due redeem script generation')

    redeem_script_file = 'redeemScript-{}.txt'.format(lock_time)
    lock_address_file = 'lockAddress-{}.txt'.format(lock_time)

    with open(os.path.join(CLTV_DIR, redeem_script_file), 'r') as file:
        redeem_script = file.read()
    with open(os.path.join(CLTV_DIR, lock_address_file), 'r') as file:
        lock_address = file.read()

    os.remove(os.path.join(CLTV_DIR, redeem_script_file))
    os.remove(os.path.join(CLTV_DIR, lock_address_file))

    cltv_details = save_cltv_data(frozen_at, redeem_script, lock_address, receiver_public_key, lock_time)

    return cltv_details


def save_vout_number(transfer: Transfer):
    interface = DucatuscoreInterface()
    tx_data = interface.rpc.gettransaction(transfer.tx_hash)
    vout_number = tx_data['details'][0]['vout']
    transfer.vout_number = vout_number
    transfer.save()


def get_duc_transfer_fee():
    interface = DucatuscoreInterface()
    return interface.rpc.getinfo()['relayfee'] * 10 ** 8
