from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from .models import BankAccount, Transaction


class BankingModelTests(TestCase):
    def setUp(self):
        self.sender = BankAccount.objects.create(
            customer_name="Rahul Sharma",
            account_number="SB100001",
            account_type="SAVINGS",
            balance=Decimal("10000.00"),
        )

        self.receiver = BankAccount.objects.create(
            customer_name="Priya Singh",
            account_number="SB100002",
            account_type="SAVINGS",
            balance=Decimal("5000.00"),
        )

    def test_bank_account_creation(self):
        self.assertEqual(self.sender.customer_name, "Rahul Sharma")
        self.assertEqual(self.sender.balance, Decimal("10000.00"))

    def test_account_string_representation(self):
        expected = "Rahul Sharma (SB100001)"
        self.assertEqual(str(self.sender), expected)


class BankingViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.sender = BankAccount.objects.create(
            customer_name="Rahul Sharma",
            account_number="SB100001",
            account_type="SAVINGS",
            balance=Decimal("10000.00"),
        )

        self.receiver = BankAccount.objects.create(
            customer_name="Priya Singh",
            account_number="SB100002",
            account_type="SAVINGS",
            balance=Decimal("5000.00"),
        )

    def test_dashboard_returns_success(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Digital Banking Dashboard")

    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "UP")
        self.assertEqual(
            response.json()["service"],
            "django-banking-app",
        )

    def test_successful_money_transfer(self):
        response = self.client.post(
            reverse("transfer"),
            {
                "sender": self.sender.id,
                "receiver": self.receiver.id,
                "amount": "2000.00",
                "description": "Test transfer",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.sender.refresh_from_db()
        self.receiver.refresh_from_db()

        self.assertEqual(
            self.sender.balance,
            Decimal("8000.00"),
        )

        self.assertEqual(
            self.receiver.balance,
            Decimal("7000.00"),
        )

        self.assertEqual(Transaction.objects.count(), 1)

        transaction = Transaction.objects.first()

        self.assertEqual(
            transaction.amount,
            Decimal("2000.00"),
        )

        self.assertEqual(transaction.status, "SUCCESS")

    def test_transfer_with_insufficient_balance(self):
        response = self.client.post(
            reverse("transfer"),
            {
                "sender": self.sender.id,
                "receiver": self.receiver.id,
                "amount": "20000.00",
                "description": "Invalid transfer",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.sender.refresh_from_db()
        self.receiver.refresh_from_db()

        self.assertEqual(
            self.sender.balance,
            Decimal("10000.00"),
        )

        self.assertEqual(
            self.receiver.balance,
            Decimal("5000.00"),
        )

        self.assertEqual(Transaction.objects.count(), 0)