import os
import csv
from django.utils import timezone
from ducatus_voucher.staking.models import DepositInput


def export_deposit_statistics():
    unspent_dividends_inputs = DepositInput.objects.filter(spent_tx_hash=None, deposit__dividends__gt=0)

    if not unspent_dividends_inputs:
        print('All deposits has been withdrawn, nothing to export', flush=True)

    stat_fn = f'staking-{str(timezone.now().date())}.csv'
    with open(os.path.join(os.getcwd(), stat_fn), 'w') as csvfile:
        writer = csv.writer(csvfile)
        for deposit_input in unspent_dividends_inputs:
            writer.writerow(
                [
                    deposit_input.mint_tx_hash,
                    deposit_input.amount,
                    deposit_input.deposit.cltv_details.lock_time
                ]
            )
