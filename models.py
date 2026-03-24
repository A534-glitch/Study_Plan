from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    user_type = models.CharField(max_length=10)
    year_of_study_from = models.IntegerField(null=True, blank=True)
    year_of_study_to = models.IntegerField(null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.username


class Product(models.Model):
    seller = models.ForeignKey(User,on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField(null=True)
    category = models.CharField(max_length=20)
    image = models.ImageField(upload_to='media/')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, null=True)
    previous_status = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


class Payment(models.Model):

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments_made", null=True
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments_received", null=True
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    amount = models.PositiveIntegerField(null=True)
    status = models.CharField(max_length=10)
    paid_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, null=True)  # 'buy' or 'lease'

    def __str__(self):
        return f"{self.buyer.username} → {self.receiver.username} : {self.amount}"

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

class Wallet(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0, null=True)
    topup_amount = models.FloatField(default=0,null=True)
    spent_amount = models.FloatField(default=0, null=True)
    created_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"


class Bargain(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_bargains")
    alumni = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alumni_bargains")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    student_price = models.PositiveIntegerField(null=True, blank=True)
    alumni_price = models.PositiveIntegerField(null=True, blank=True)
    final_price = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=10, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.student.username} ↔ {self.alumni.username}"


class LeaseRequest(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE,related_name="lease_student")
    alumni = models.ForeignKey(User,on_delete=models.CASCADE,related_name="lease_alumni")
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    rent = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=10, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.student} → {self.product.name}"

class BuyOrder(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buy_student")
    alumni = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buy_alumni")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    price = models.PositiveIntegerField()
    status = models.CharField(max_length=10, default='pending')

    ordered_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} → {self.product.name} ({self.status})"
