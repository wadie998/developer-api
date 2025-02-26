import uuid

from django.db import models

from api.enum import RequestStatus, SendMoneyServiceOperationTypes


class LinkedAccount(models.Model):
    partner_tracking_id = models.UUIDField(editable=False, primary_key=True)  # The mapping id given to the partner
    account_tracking_id = models.UUIDField()
    phone_number = models.CharField(unique=False, null=False, max_length=15)
    merchant_id = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now_add=True)  # Time the link between the accounts was done.
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Linked Account"
        verbose_name_plural = "Linked Accounts"

    def __str__(self):
        return f"{self.partner_tracking_id}"


class PartnerTransaction(models.Model):
    operation_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    operation_type = models.CharField(max_length=50, null=True, choices=SendMoneyServiceOperationTypes.get_choices())
    sender = models.ForeignKey(
        LinkedAccount, on_delete=models.PROTECT, blank=True, null=True, related_name="sender_transactions"
    )  # the partner
    receiver = models.ForeignKey(
        LinkedAccount, on_delete=models.PROTECT, blank=True, null=True, related_name="receiver_transactions"
    )  # the partner
    amount_in_millimes = models.IntegerField()
    operation_payload = models.JSONField(blank=True, null=True, default=dict)
    operation_status = models.CharField(
        max_length=20, choices=RequestStatus.get_choices(), default=RequestStatus.PENDING
    )
    blockchain_ref = models.CharField(max_length=255, null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def set_operation_status(self, operation_status):
        self.operation_status = operation_status
        self.save(update_fields=["operation_status"])
