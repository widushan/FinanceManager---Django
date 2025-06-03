from django.db import models
from datetime import datetime
# Create your models here.

class Account(models.Model):
    name = models.CharField(max_length=100) 
    expense = models.FloatField(default=0)
    income = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    expense_list = models.ManyToManyField('Expense', blank=True)
    income_list = models.ManyToManyField('Income', blank=True)
    
class Expense(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    date = models.DateField(null=False, default=datetime.now().date())
    long_term = models.BooleanField(default=False)
    interest_rate = models.FloatField(default=0, null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    monthly_expenses = models.FloatField(default=0, null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.long_term:
            self.monthly_expenses = self.calculate_monthly_expenses()
        super(Expense, self).save(*args, **kwargs)

    def calculate_monthly_expenses(self):
        if self.long_term:
            if self.interest_rate == 0:
                return self.amount/((self.end_date - self.date).days/30)
            else:
                months = (self.end_date.year - datetime.now().year) * 12 + self.end_date.month - datetime.now().month
                monthly_rate = self.interest_rate / 12 / 100
                monthly_expense = (self.amount * monthly_rate) / (1 - (1 + monthly_rate) ** (-months))
                return monthly_expense
        else:
            return self.amount  # For non-long-term expenses, just return the amount




class Income(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    date = models.DateField(null=False, default=datetime.now().date())
    monthly_income = models.FloatField(default=0, null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
