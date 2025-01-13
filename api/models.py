# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid

from django.db import models


class App(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=100)
    public_token = models.CharField(unique=True, max_length=60)
    wallet = models.CharField(max_length=35)
    status = models.CharField(max_length=20)
    active = models.BooleanField()
    date_created = models.DateTimeField()
    user = models.ForeignKey("JhiUser", models.PROTECT, blank=True, null=True)
    webhook = models.CharField(max_length=255, blank=True, null=True)
    sms_key = models.CharField(max_length=6, blank=True, null=True)
    test = models.BooleanField()
    description = models.CharField(max_length=255, blank=True, null=True)
    private_token = models.CharField(unique=True, max_length=36, blank=True, null=True)
    image_url = models.CharField(blank=True, null=True)
    deleted = models.BooleanField()
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
            "token": self.public_token,
            "secret": self.private_token,
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


class DailyMetrics(models.Model):
    id = models.BigAutoField(primary_key=True)
    day = models.DateField(blank=True, null=True)
    transactions = models.BigIntegerField(blank=True, null=True)
    app = models.ForeignKey(App, models.DO_NOTHING, blank=True, null=True)
    daily_metrics_id = models.UUIDField(blank=True, null=True)
    amount_sum = models.BigIntegerField(blank=True, null=True)
    fee_sum = models.BigIntegerField(blank=True, null=True)
    amount_average = models.FloatField(blank=True, null=True)
    fee_average = models.FloatField(blank=True, null=True)
    transaction_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "daily_metrics"


class Databasechangelog(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    author = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    dateexecuted = models.DateTimeField()
    orderexecuted = models.IntegerField()
    exectype = models.CharField(max_length=10)
    md5sum = models.CharField(max_length=35, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    tag = models.CharField(max_length=255, blank=True, null=True)
    liquibase = models.CharField(max_length=20, blank=True, null=True)
    contexts = models.CharField(max_length=255, blank=True, null=True)
    labels = models.CharField(max_length=255, blank=True, null=True)
    deployment_id = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "databasechangelog"


class Databasechangeloglock(models.Model):
    id = models.BigAutoField(primary_key=True)
    locked = models.BooleanField()
    lockgranted = models.DateTimeField(blank=True, null=True)
    lockedby = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "databasechangeloglock"


class JhiAuthority(models.Model):
    name = models.CharField(primary_key=True, max_length=50)

    class Meta:
        managed = False
        db_table = "jhi_authority"


class JhiPersistentAuditEvent(models.Model):
    event_id = models.BigIntegerField(primary_key=True)
    principal = models.CharField(max_length=50)
    event_date = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "jhi_persistent_audit_event"


class JhiPersistentAuditEvtData(models.Model):
    event = models.OneToOneField(
        JhiPersistentAuditEvent, models.DO_NOTHING, primary_key=True
    )  # The composite primary key (event_id, name) found, that is not supported. The first column is selected.
    name = models.CharField(max_length=150)
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "jhi_persistent_audit_evt_data"
        unique_together = (("event", "name"),)


class JhiUser(models.Model):
    # CREATE SEQUENCE jhi_user_id_seq;
    # ALTER TABLE jhi_user ALTER COLUMN id SET DEFAULT nextval('jhi_user_id_seq');
    id = models.BigAutoField(primary_key=True, serialize=False)
    login = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=60)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(unique=True, max_length=191, blank=True, null=True)
    image_url = models.CharField(max_length=1000, blank=True, null=True)
    activated = models.BooleanField()
    lang_key = models.CharField(max_length=10, blank=True, null=True)
    activation_key = models.CharField(max_length=20, blank=True, null=True)
    reset_key = models.CharField(max_length=20, blank=True, null=True)
    created_by = models.CharField(max_length=50)
    created_date = models.DateTimeField(blank=True, null=True)
    reset_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.CharField(max_length=50, blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)
    tmp_email = models.CharField(max_length=191, blank=True, null=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    sms_key = models.CharField(max_length=6, blank=True, null=True)
    email_validated = models.BooleanField()
    deleted = models.BooleanField()
    user_id = models.UUIDField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = "jhi_user"


class JhiUserAuthority(models.Model):
    user = models.OneToOneField(
        JhiUser, models.DO_NOTHING, primary_key=True
    )  # The composite primary key (user_id, authority_name) found, that is not supported. The first column is selected.
    authority_name = models.ForeignKey(JhiAuthority, models.DO_NOTHING, db_column="authority_name")

    class Meta:
        managed = False
        db_table = "jhi_user_authority"
        unique_together = (("user", "authority_name"),)


class MetricsLastUpdate(models.Model):
    id = models.BigAutoField(primary_key=True)
    last_update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "metrics_last_update"
