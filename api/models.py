# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid

from django.db import models

from api.enum import AppStatus


class App(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=100)
    public_token = models.UUIDField(default=uuid.uuid4, unique=True)
    wallet = models.CharField(max_length=35)
    status = models.CharField(choices=AppStatus.get_choices(), default=AppStatus.VERIFIED, max_length=20)
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
    revoke_number = models.IntegerField(blank=True, null=True)
    last_revoke_date = models.DateField(blank=True, null=True)
    app_id = models.UUIDField(blank=True, null=True)
    merchant_id = models.BigIntegerField()

    class Meta:
        # managed = False
        db_table = "app"
        unique_together = (("user", "name"),)

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
        self.save(update_fields=["private_token"])


class JhiUser(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    login = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=60)
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
        # managed = False
        db_table = "jhi_user"
