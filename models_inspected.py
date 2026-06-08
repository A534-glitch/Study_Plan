# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('HomeUser', models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class HomeBargain(models.Model):
    student_price = models.PositiveIntegerField(blank=True, null=True)
    alumni_price = models.PositiveIntegerField(blank=True, null=True)
    final_price = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    alumni = models.ForeignKey('HomeUser', models.DO_NOTHING)
    product = models.ForeignKey('HomeProduct', models.DO_NOTHING)
    student = models.ForeignKey('HomeUser', models.DO_NOTHING, related_name='homebargain_student_set')

    class Meta:
        managed = False
        db_table = 'home_bargain'


class HomeBuyorder(models.Model):
    price = models.PositiveIntegerField()
    status = models.CharField(max_length=10)
    ordered_at = models.DateTimeField()
    approved_at = models.DateTimeField(blank=True, null=True)
    alumni = models.ForeignKey('HomeUser', models.DO_NOTHING)
    product = models.ForeignKey('HomeProduct', models.DO_NOTHING)
    student = models.ForeignKey('HomeUser', models.DO_NOTHING, related_name='homebuyorder_student_set')

    class Meta:
        managed = False
        db_table = 'home_buyorder'


class HomeLeaserequest(models.Model):
    status = models.CharField(max_length=10)
    requested_at = models.DateTimeField()
    alumni = models.ForeignKey('HomeUser', models.DO_NOTHING)
    product = models.ForeignKey('HomeProduct', models.DO_NOTHING)
    student = models.ForeignKey('HomeUser', models.DO_NOTHING, related_name='homeleaserequest_student_set')
    approved_at = models.DateTimeField(blank=True, null=True)
    rent = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_leaserequest'


class HomePayment(models.Model):
    amount = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=10)
    paid_at = models.DateTimeField()
    buyer = models.ForeignKey('HomeUser', models.DO_NOTHING, blank=True, null=True)
    receiver = models.ForeignKey('HomeUser', models.DO_NOTHING, related_name='homepayment_receiver_set', blank=True, null=True)
    product = models.ForeignKey('HomeProduct', models.DO_NOTHING, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_payment'


class HomeProduct(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField(blank=True, null=True)
    category = models.CharField(max_length=20)
    image = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    seller = models.ForeignKey('HomeUser', models.DO_NOTHING)
    previous_status = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_product'


class HomeUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    course = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    year_of_study_from = models.IntegerField(blank=True, null=True)
    year_of_study_to = models.IntegerField(blank=True, null=True)
    user_type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_user'


class HomeUserGroups(models.Model):
    user = models.ForeignKey(HomeUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'home_user_groups'
        unique_together = (('user', 'group'),)


class HomeUserUserPermissions(models.Model):
    user = models.ForeignKey(HomeUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'home_user_user_permissions'
        unique_together = (('user', 'permission'),)


class HomeWallet(models.Model):
    balance = models.FloatField(blank=True, null=True)
    user = models.OneToOneField(HomeUser, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    spent_amount = models.FloatField(blank=True, null=True)
    topup_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_wallet'
