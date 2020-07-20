import os
import datetime
from django.utils import timezone

from ducatus_voucher.vouchers.models import Voucher
from ducatus_voucher.freezing.models import FreezingVoucher
from ducatus_voucher.bip32_ducatus import DucatusWallet
from ducatus_voucher.settings import duc_xpublic_key
from ducatus_voucher.settings import CLTV_DIR


def get_unused_frozen_vouchers(wallet_id):
    vouchers = FreezingVoucher.objects.filter(wallet_id=wallet_id, withdrawn=False)
    return vouchers


def get_redeem_info(voucher_id):
    frozen_voucher = FreezingVoucher.objects.get(voucher_id)

    withdraw_date = frozen_voucher.frozen_at + datetime.timedelta(days=frozen_voucher.voucher.lock_days)
    redeem_info = {
        'redeem_script_hex': frozen_voucher.redeem_script,
        'lock_time': int(withdraw_date.timestamp()),
    }

    return redeem_info


def generate_child_public_key(voucher_id):
    duc_root_key = DucatusWallet.deserialize(duc_xpublic_key)
    duc_child = duc_root_key.get_child(voucher_id, is_prime=False)
    duc_child_public = duc_child.get_public_key_hex().decode()

    return duc_child_public


def save_cltv_data(wallet_id, frozen_at, redeem_script, locked_duc_address, user_duc_address, user_public_key,
                   backend_public_key, voucher, lock_time):
    frozen_voucher = FreezingVoucher()
    frozen_voucher.wallet_id = wallet_id
    frozen_voucher.frozen_at = frozen_at
    frozen_voucher.redeem_script = redeem_script
    frozen_voucher.locked_duc_address = locked_duc_address
    frozen_voucher.user_duc_address = user_duc_address
    frozen_voucher.user_public_key = user_public_key
    frozen_voucher.backend_public_key = backend_public_key
    frozen_voucher.lock_time = lock_time
    frozen_voucher.save()

    voucher.freezing_details = frozen_voucher
    voucher.save()

    print('voucher is frozen', frozen_voucher.__dict__, flush=True)


def generate_cltv(receiver_public_key: str, voucher: Voucher, user_duc_address, wallet_id):
    backend_public_key = generate_child_public_key(voucher.id)
    frozen_at = timezone.now()
    lock_date = frozen_at + datetime.timedelta(days=voucher.lock_days)
    lock_time = int(lock_date.timestamp())

    bash_command = 'node {script_path} {receiver_public_key} {backend_public_key} {lock_time} {voucher_id} {files_dir}' \
        .format(script_path=os.path.join(CLTV_DIR, 'cltv_generation.js'), receiver_public_key=receiver_public_key,
                backend_public_key=backend_public_key, lock_time=lock_time, voucher_id=voucher.id, files_dir=CLTV_DIR)
    if os.system(bash_command):
        raise Exception('error due redeem script generation')

    redeem_script_file = 'redeemScript-{}.txt'.format(voucher.id)
    lock_address_file = 'lockAddress-{}.txt'.format(voucher.id)

    with open(os.path.join(CLTV_DIR, redeem_script_file), 'r') as file:
        redeem_script = file.read()
    with open(os.path.join(CLTV_DIR, lock_address_file), 'r') as file:
        lock_address = file.read()

    os.remove(os.path.join(CLTV_DIR, redeem_script_file))
    os.remove(os.path.join(CLTV_DIR, lock_address_file))

    save_cltv_data(wallet_id, frozen_at, redeem_script, lock_address, user_duc_address, receiver_public_key,
                   backend_public_key, voucher, lock_time)

    return lock_address
