import datetime as dt

from django.db import models


class CltvDetails(models.Model):
    withdrawn = models.BooleanField(default=False)
    lock_time = models.BigIntegerField()
    redeem_script = models.TextField()
    locked_duc_address = models.CharField(max_length=50)
    user_public_key = models.CharField(max_length=80)
    frozen_at = models.DateTimeField()
    private_path = models.CharField(max_length=20, default='')

    def total_days(self):
        start = self.frozen_at.replace(microsecond=0, tzinfo=None)
        finish_timestamp = self.lock_time
        finish = dt.datetime.fromtimestamp(finish_timestamp)
        timedelta = finish - start
        days = timedelta.days
        return days
