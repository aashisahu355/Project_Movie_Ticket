from django.contrib.auth.models import User
from django.db import models

from theatreApp.models import Show
import random

# User otp model
class OTP(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000,999999))

# seat locking
class SeatLock(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    seat = models.CharField(max_length=10)
    user_id = models.IntegerField()
    locked_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.locked_at < timezone.now() - timedelta(minutes=15)


# user booking model
class Booking(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    show = models.ForeignKey(Show,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    seats = models.JSONField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    BOOKING_STATUS = (
        ("pending", "Pending Payment"),
        ("confirmed", "Confirmed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default="pending")

# user orders
class Order(models.Model):
    STATUS_CHOICES = [
        ("created","Created"),
        ("paid","Paid"),
        ("failed","Failed"),
        ("refunded","Refunded")
    ]
    book_id = models.ForeignKey(Booking,on_delete=models.CASCADE)
    amount = models.IntegerField()
    currency = models.CharField(max_length=10,default='INR')
    razorpay_order_id =  models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100)
    razorpay_signature = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, default='created')



