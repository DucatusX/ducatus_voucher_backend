import os

from ducatus_voucher.bip32_ducatus import DucatusWallet
from ducatus_voucher.settings import duc_xpublic_key
from ducatus_voucher.settings import CLTV_DIR


def generate_child_public_key(voucher_id):
    duc_root_key = DucatusWallet.deserialize(duc_xpublic_key)
    duc_child = duc_root_key.get_child(voucher_id, is_prime=False)
    duc_child_public = duc_child.get_private_key_hex()

    return duc_child_public


def generate_cltv(receiver_public_key, backend_public_key, lock_time, voucher_id):
    bash_command = 'node {script_path} {receiver_public_key} {backend_public_key} {lock_time} {voucher_id} {files_dir}' \
        .format(script_path=os.path.join(CLTV_DIR, 'cltv_generation.js'), receiver_public_key=receiver_public_key,
                backend_public_key=backend_public_key, lock_time=lock_time, voucher_id=voucher_id, files_dir=CLTV_DIR)
    if os.system(bash_command):
        raise Exception('error due redeem script generation')

    redeem_script_file = 'redeemScript-{}.txt'.format(voucher_id)
    lock_address_file = 'lockAddress-{}.txt'.format(voucher_id)

    with open(os.path.join(CLTV_DIR, redeem_script_file), 'r') as file:
        redeem_script = file.read()
    with open(os.path.join(CLTV_DIR, lock_address_file), 'r') as file:
        lock_address = file.read()

    os.remove(os.path.join(CLTV_DIR, redeem_script_file))
    os.remove(os.path.join(CLTV_DIR, lock_address_file))

    return redeem_script, lock_address

