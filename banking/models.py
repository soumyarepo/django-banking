from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ("SAVINGS", "Savings"),
        ("CURRENT", "Current"),
    ]

    customer_name = models.CharField(max_length=100)
    account_number = models.CharField(
        max_length=20,
        unique=True,
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
        default="SAVINGS",
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.customer_name} "
            f"({self.account_number})"
        )


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    sender = models.ForeignKey(
        BankAccount,
        related_name="sent_transactions",
        on_delete=models.PROTECT,
    )
    receiver = models.ForeignKey(
        BankAccount,
        related_name="received_transactions",
        on_delete=models.PROTECT,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.00"))],
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SUCCESS",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.sender.account_number} → "
            f"{self.receiver.account_number}: "
            f"₹{self.amount}"
        )