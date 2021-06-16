import os
import csv
from datetime import datetime, timedelta
import pytz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ducatus_voucher.settings')
import django
django.setup()

from ducatus_voucher.staking.models import Deposit
from ducatus_voucher.staking.models import DepositInput
from ducatus_voucher.consts import DECIMALS
from ducatus_voucher.settings import BASE_DIR

def write_payments_to_csv(name, deposit_list):
    with open(os.path.join(BASE_DIR, name), 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['user address', 'start time', 'end time', 'amount', 'dividends'])
        for val in deposit_list:
            writer.writerow([val['user_address'], val['start_time'], val['end_time'],  int(val['amount']) / DECIMALS['DUC'],
                             int(val['dividends']) / DECIMALS['DUC']])

if __name__ == '__main__':
    deposits = Deposit.objects.filter(dividends_sent=False)
    deposit_list = []
    for deposit in deposits:
        user_address = deposit.user_duc_address
        start_time = deposit.cltv_details.frozen_at
        end_time = datetime.fromtimestamp(deposit.cltv_details.lock_time)
        end_time = pytz.utc.localize(end_time)
        amount = 0
        for input in DepositInput.objects.filter(deposit=deposit):
            amount += input.amount

        if (end_time - start_time).days < 200:
            months = 5
        elif (end_time - start_time).days < 420:
            months = 13
        else:
            months = 24

        dividends = amount * deposit.dividends / 100 / 12 * months
        deposit_list.append({
            'user_address': user_address,
            'start_time': start_time,
            'end_time': end_time,
            'amount': amount,
            'dividends': dividends
        })

    write_payments_to_csv('deposits', deposit_list)
