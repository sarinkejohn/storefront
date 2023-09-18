from django.db import models
from django.contrib.auth.models import User
from product.models import Product

# Create your models here.


class OrderStatus(models.TextChoices):
    PROCESSING = 'PROCESSING'
    SHIPPED = 'SHIPPED'
    DELIVERD = 'DELIVERD'


class PaymentStatus(models.TextChoices):
    PAID = 'PAID'
    UNPAID = 'UNPAID'


class PaymentMethode(models.TextChoices):
    COD = 'COD'
    CARD = 'CARD'


class Order(models.Model):
    street = models.CharField(max_length=100, default="", blank=False)
    city = models.CharField(max_length=100, default="", blank=False)
    state = models.CharField(max_length=100, default="", blank=False)
    zip_code = models.CharField(max_length=100, default="", blank=False)
    country = models.CharField(max_length=100, default="", blank=False)
    phone_no = models.CharField(max_length=100, default="", blank=False)
    total_amount = models.CharField(max_length=100, default="", blank=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethode.choices,
        default=PaymentMethode.COD
    )
    order_status = models.CharField(
        max_length=25,
        choices=OrderStatus.choices,
        default=OrderStatus.PROCESSING

    )

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='orderitems')
    quantity = models.IntegerField(default=1,)
    name = models.CharField(max_length=200, default="", blank=False)
    price = models.DecimalField(
        decimal_places=2, max_digits=7, blank=False)
    images = models.CharField(max_length=500, default="", blank=False)

    def __str__(self):
        return str(self.name)
