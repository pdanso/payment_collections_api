from django.db import models
from django.contrib.postgres.fields import JSONField
from mesika_utils.RandomTransactionIds import generate_sso_token


class Transactions(models.Model):
    STATUS = (
        ("PENDING", "PENDING"),
        ("FAILED", "FAILED"),
        ("SUCCESSFUL", "SUCCESSFUL")
    )

    transaction_id = models.CharField(primary_key=True, default=generate_sso_token, max_length=250, unique=True)
    mesika_reference_number = models.CharField(max_length=250, default=generate_sso_token, unique=True)
    payer_msisdn = models.CharField(max_length=210, null=True, blank=True)
    payer_reference_number = models.CharField(max_length=250, unique=True)
    account_number = models.CharField(max_length=210)
    amount = models.DecimalField(default=0.01, decimal_places=2, max_digits=100)
    processing_charge = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
    provider = models.CharField(max_length=210, default="MTN MOBILE MONEY")
    provider_reference_number = models.CharField(max_length=250, default=generate_sso_token, unique=True)
    status = models.CharField(default="PENDING", choices=STATUS, max_length=50)
    status_description = models.CharField(max_length=250, null=True, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(auto_now=True)

    def get_details(self):

        details = {
            "transaction_id": self.transaction_id,
            "mesika_reference_number": self.mesika_reference_number,
            "payer_msisdn": self.payer_msisdn,
            "payer_reference_number": self.payer_reference_number,
            "account_number": self.account_number,
            "amount": self.amount,
            "processing_charge": self.processing_charge,
            "provider": self.provider,
            "provider_reference_number": self.provider_reference_number,
            "transaction_status": self.status,
            "status_description": self.status_description,
            "date_submitted": self.date_submitted.strftime('%Y-%m-%d %H:%M:%S'),
            "date_completed": self.date_completed.strftime('%Y-%m-%d %H:%M:%S')
        }

        return details

    @property
    def is_paid(self):

        if self.status == "PAID":
            return True
        else:
            return False

    class Meta:
        verbose_name = "Transactions"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.payer_reference_number}-{self.date_submitted}"


class ExtraDetails(models.Model):
    transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE)
    details = JSONField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def get_details(self):

        out_details = {
            "transaction_id": self.transaction.transaction_id,
            "mesika_reference_number": self.transaction.mesika_reference_number,
            "payer_msisdn": self.transaction.payer_msisdn,
            "payer_reference_number": self.transaction.payer_reference_number,
            "account_number": self.transaction.account_number,
            "amount": self.transaction.amount,
            "processing_charge": self.transaction.processing_charge,
            "provider": self.transaction.provider,
            "provider_reference_number": self.transaction.provider_reference_number,
            "transaction_status": self.transaction.status,
            "status_description": self.transaction.status_description,
            "date_submitted": self.transaction.date_submitted.strftime('%Y-%m-%d %H:%M:%S'),
            "date_completed": self.transaction.date_completed.strftime('%Y-%m-%d %H:%M:%S'),
        }

        vdet = self.details
        for k, v in vdet.items():
            vkey = f"{k}"
            vval = f"{v}"
            out_details[vkey] = vval

        return out_details

    class Meta:
        verbose_name = "ExtraDetails"
        verbose_name_plural = "ExtraDetails"

    def __str__(self):
        return f"{self.transaction.payer_reference_number}-{self.details}"


class Jobs(models.Model):
    jobs_id = models.CharField(primary_key=True, max_length=210, default=generate_sso_token, unique=True)
    transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Jobs"
        verbose_name_plural = "Jobs"

    def __str__(self):

        return f"{self.transaction.transaction_id}-{self.jobs_id}"

