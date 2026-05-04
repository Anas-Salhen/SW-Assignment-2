from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    isCustom = models.BooleanField(default=False)

    def __str__(self): return self.name
    
class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10, 
        choices=[('income', 'Income'), ('expense', 'Expense')]
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Income(Transaction):
    source = models.CharField(max_length=100)

class Expense(Transaction):
    paymentMethod = models.CharField(max_length=100)

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()