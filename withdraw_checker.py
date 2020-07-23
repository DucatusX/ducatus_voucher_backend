import os
import sys
import time
import traceback
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ducatus_voucher.settings')
import django

django.setup()

from django.utils import timezone

from ducatus_voucher.litecoin_rpc import DucatuscoreInterface
from ducatus_voucher.freezing.models import FreezingVoucher
from ducatus_voucher.settings import WITHDRAW_CHECKER_TIMEOUT

if __name__ == '__main__':
    while True:
        frozen_vouchers = FreezingVoucher.objects.filter(withdrawn=False, lock_time__lt=timezone.now().timestamp())
        if not frozen_vouchers:
            print('all frozen vouchers have withdrawn at {}\n'.format(datetime.datetime.now()), flush=True)

        interface = DucatuscoreInterface()
        for frozen_voucher in frozen_vouchers:
            try:
                transfer_instance = frozen_voucher.voucher.transfer_set.first()
                tx_hash = transfer_instance.tx_hash
                if tx_hash:
                    vout_number = transfer_instance.vout_number
                    unspent_tx = interface.rpc.gettxout(tx_hash, vout_number)
                    if not unspent_tx:
                        frozen_voucher.withdrawn = True
                        frozen_voucher.save()
                        print('voucher with id {id} withdrawn at {time}\n'.format(id=frozen_voucher.id,
                                                                                  time=datetime.datetime.now()),
                              flush=True)
                    else:
                        print('voucher with id {id} not withdrawn yet at {time}\n'.format(id=frozen_voucher.id,
                                                                                          time=datetime.datetime.now()),
                              flush=True)
            except Exception as e:
                print('\n'.join(traceback.format_exception(*sys.exc_info())), flush=True)

        time.sleep(WITHDRAW_CHECKER_TIMEOUT)
