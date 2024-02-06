# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models import Model


class Databasechangelog(Model):
    id = models.CharField(primary_key=True, max_length=255)
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


class Databasechangeloglock(Model):
    id = models.IntegerField(primary_key=True)
    locked = models.BooleanField()
    lockgranted = models.DateTimeField(blank=True, null=True)
    lockedby = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "databasechangeloglock"


class JhiAuthority(Model):
    name = models.CharField(primary_key=True, max_length=50)

    class Meta:
        managed = True
        db_table = "jhi_authority"


class JhiUser(Model):
    id = models.BigIntegerField(primary_key=True)
    login = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=60)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(unique=True, max_length=191, blank=True, null=True)
    image_url = models.CharField(max_length=256, blank=True, null=True)
    activated = models.BooleanField()
    lang_key = models.CharField(max_length=10, blank=True, null=True)
    activation_key = models.CharField(max_length=20, blank=True, null=True)
    reset_key = models.CharField(max_length=20, blank=True, null=True)
    created_by = models.CharField(max_length=50)
    created_date = models.DateTimeField(blank=True, null=True)
    reset_date = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.CharField(max_length=50, blank=True, null=True)
    last_modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "jhi_user"


class JhiUserAuthority(Model):
    user = models.OneToOneField(
        JhiUser, models.DO_NOTHING, primary_key=True
    )  # The composite primary key (user_id, authority_name) found, that is not supported. The first column is selected.
    authority_name = models.ForeignKey(JhiAuthority, models.DO_NOTHING, db_column="authority_name")

    class Meta:
        managed = True
        db_table = "jhi_user_authority"
        unique_together = (("user", "authority_name"),)
