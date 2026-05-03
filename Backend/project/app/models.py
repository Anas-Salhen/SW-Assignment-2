from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    isCustom = models.BooleanField(default=False)

    def __str__(self): return self.name

class Transaction(models.Model): # الـ Class الأب
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True 

class Income(Transaction):
    source = models.CharField(max_length=100)

class Expense(Transaction):
    paymentMethod = models.CharField(max_length=100)

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()