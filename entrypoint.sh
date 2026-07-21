#!/bin/sh

set -e

echo "Running Django database migrations..."
python manage.py migrate --noinput

echo "Collecting Django static files..."
python manage.py collectstatic --noinput

echo "Creating demo banking data..."
python manage.py shell <<'PYTHON'
from decimal import Decimal

from banking.models import BankAccount


accounts = [
    {
        "customer_name": "Rahul Sharma",
        "account_number": "SB100001",
        "account_type": "SAVINGS",
        "balance": Decimal("125000.00"),
    },
    {
        "customer_name": "Priya Singh",
        "account_number": "SB100002",
        "account_type": "SAVINGS",
        "balance": Decimal("85000.00"),
    },
    {
        "customer_name": "ABC Enterprises",
        "account_number": "CA200001",
        "account_type": "CURRENT",
        "balance": Decimal("450000.00"),
    },
]

for account_data in accounts:
    BankAccount.objects.get_or_create(
        account_number=account_data["account_number"],
        defaults=account_data,
    )

print("Demo accounts are ready.")
PYTHON

echo "Starting Django banking application..."

exec "$@"