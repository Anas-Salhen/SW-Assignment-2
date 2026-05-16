from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    fullName  = models.CharField(max_length=200, blank=True, default='')
    currency  = models.CharField(max_length=10,  blank=True, default='USD')
    language  = models.CharField(max_length=10,  blank=True, default='en')

    def updateProfile(self, fullName=None, email=None):
        """Update the user's display name and/or email."""
        if fullName is not None:
            self.fullName = fullName
        if email is not None:
            self.email = email
        self.save()

    def updateSettings(self, currency=None, language=None):
        """Update the user's currency and/or language preference."""
        if currency is not None:
            self.currency = currency
        if language is not None:
            self.language = language
        self.save()

    def __str__(self):
        return self.username




class Category(models.Model):
    id       = models.AutoField(primary_key=True)
    name     = models.CharField(max_length=100)
    isCustom = models.BooleanField(default=False)

    def __str__(self):
        return self.name



class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title            = models.CharField(max_length=200)
    amount           = models.DecimalField(max_digits=10, decimal_places=2)
    description      = models.TextField(blank=True, default='')
    transaction_type = models.CharField(
        max_length=10,
        choices=[('income', 'Income'), ('expense', 'Expense')],
    )
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Income(Transaction):
    source = models.CharField(max_length=100)


class Expense(Transaction):
    paymentMethod = models.CharField(max_length=100)
    # Issue #7 — category FK is present and will now be set in services.py
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )



class Budget(models.Model):

    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('active',   'Active'),
        ('modified', 'Modified'),
        ('paused',   'Paused'),
        ('closed',   'Closed'),
        ('archived', 'Archived'),
    ]

    user           = models.ForeignKey(User, on_delete=models.CASCADE)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    category       = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_date     = models.DateField()
    end_date       = models.DateField()
    alertThreshold = models.IntegerField(default=80)   # percentage (e.g. 80 → warn at 80 %)
    status         = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )

    def calculateRemaining(self):
        """Return how much budget is left for this category."""
        from django.db.models import Sum
        total_spent = Expense.objects.filter(
            user=self.user,
            category=self.category,
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        return float(self.amount) - float(total_spent)

    def __str__(self):
        return f"{self.category.name} budget ({self.user.username})"




class SavingsGoal(models.Model):
    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name          = models.CharField(max_length=200)
    targetAmount  = models.DecimalField(max_digits=10, decimal_places=2)
    currentAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline      = models.DateField()

    def calculateProgress(self) -> float:
        """Return completion percentage (0.0 – 100.0)."""
        if self.targetAmount == 0:
            return 0.0
        return round(float(self.currentAmount) / float(self.targetAmount) * 100, 2)

    def __str__(self):
        return f"{self.name} ({self.calculateProgress()}%)"



class Notification(models.Model):
    user      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    type      = models.CharField(max_length=50)   # e.g. 'budget_warning', 'goal_update'
    message   = models.TextField()
    isRead    = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def markAsRead(self):
        self.isRead = True
        self.save()

    def __str__(self):
        return f"[{self.type}] {self.message[:50]}"