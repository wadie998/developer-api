import uuid
from datetime import datetime

from django.db import models


class App(models.Model):
    class AppStatus(models.TextChoices):
        VERIFIED = "VERIFIED", "Verified"
        UNVERIFIED = "UNVERIFIED", "Unverified"

    id = models.BigAutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=100)
    public_token = models.UUIDField(default=uuid.uuid4, unique=True)
    wallet = models.CharField(max_length=35)
    status = models.CharField(choices=AppStatus.choices, default=AppStatus.VERIFIED, max_length=20)
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField()
    user = models.ForeignKey("JhiUser", models.PROTECT, blank=True, null=True)
    webhook = models.CharField(max_length=255, blank=True, null=True)
    sms_key = models.CharField(max_length=6, blank=True, null=True)
    test = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    private_token = models.UUIDField(unique=True, default=uuid.uuid4, max_length=36, blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    gross = models.DecimalField(max_digits=38, decimal_places=0, blank=True, null=True)
    transaction_number = models.BigIntegerField(blank=True, null=True)
    revoke_number = models.IntegerField(blank=True, null=True, default=0)
    last_revoke_date = models.DateField(blank=True, null=True)
    app_id = models.UUIDField(blank=True, null=True)
    merchant_id = models.BigIntegerField()

    class Meta:
        db_table = "app"


class JhiUser(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    login = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=60, editable=False)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=191, blank=True, null=True, unique=False)
    image_url = models.CharField(max_length=1000, blank=True, null=True)
    activated = models.BooleanField(default=True)
    lang_key = models.CharField(max_length=10, blank=True, null=True)
    activation_key = models.CharField(max_length=20, blank=True, null=True)
    reset_key = models.CharField(max_length=20, blank=True, null=True)
    created_by = models.CharField(max_length=50, default="system")
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    reset_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.CharField(max_length=50, default="system")
    last_modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    tmp_email = models.CharField(max_length=191, blank=True, null=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    sms_key = models.CharField(max_length=6, blank=True, null=True)
    email_validated = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    user_id = models.UUIDField(blank=True, null=True)

    class Meta:
        db_table = "jhi_user"


class FlouciApp(models.Model):
    class AppStatus(models.TextChoices):
        VERIFIED = "VERIFIED", "Verified"
        UNVERIFIED = "UNVERIFIED", "Unverified"

    id = models.BigAutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=100)
    app_id = models.UUIDField(default=uuid.uuid4, unique=True, blank=True, null=True)
    public_token = models.UUIDField(default=uuid.uuid4, unique=True)
    private_token = models.UUIDField(unique=True, default=uuid.uuid4, max_length=36, blank=True, null=True)
    tracking_id = models.UUIDField(blank=True, null=True, editable=False)
    wallet = models.CharField(max_length=35)
    status = models.CharField(choices=AppStatus.choices, default=AppStatus.VERIFIED, max_length=20)
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    webhook = models.URLField(max_length=1000, blank=True, null=True)
    test = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    gross = models.DecimalField(max_digits=38, decimal_places=0, blank=True, null=True)
    # Keeping this, but it's not used to be removed once front makes changes
    transaction_number = models.BigIntegerField(blank=True, null=True)
    revoke_number = models.IntegerField(blank=True, null=True)
    last_revoke_date = models.DateField(blank=True, null=True)
    merchant_id = models.BigIntegerField(blank=True, null=True)
    has_partner_access = models.BooleanField(default=False)
    has_advanced_payments_access = models.BooleanField(default=False)

    class Meta:
        db_table = "flouciapp"

    def get_app_details(self):
        return {
            "id": str(self.app_id),
            "name": self.name,
            "token": str(self.public_token),
            "secret": str(self.private_token),
            "status": self.status,
            "active": self.active,
            "test": self.test,
            "date_created": self.date_created.isoformat(),
            "description": self.description,
            "transaction_number": self.transaction_number,
            "gross": self.gross,
        }

    def revoke_keys(self):
        self.private_token = uuid.uuid4()
        self.revoke_number += 1
        self.last_revoke_date = datetime.now()
        self.save(update_fields=["private_token", "revoke_number", "last_revoke_date"])
