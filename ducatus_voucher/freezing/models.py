from django.db import models


class CltvDetails(models.Model):
    withdrawn = models.BooleanField(default=False)
    lock_time = models.BigIntegerField()
    redeem_script = models.TextField()
    locked_duc_address = models.CharField(max_length=50)
    user_public_key = models.CharField(max_length=80)
    frozen_at = models.DateTimeField()
