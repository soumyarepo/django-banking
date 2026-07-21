from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.http import JsonResponse

from .forms import TransferForm
from .models import BankAccount, Transaction


def dashboard(request):
    accounts = BankAccount.objects.all().order_by("account_number")
    transactions = Transaction.objects.select_related(
        "sender",
        "receiver",
    )[:10]

    total_balance = sum(
        account.balance for account in accounts
    )

    context = {
        "accounts": accounts,
        "transactions": transactions,
        "total_balance": total_balance,
    }

    return render(
        request,
        "banking/dashboard.html",
        context,
    )


def transfer_money(request):
    if request.method == "POST":
        form = TransferForm(request.POST)

        if form.is_valid():
            sender_id = form.cleaned_data["sender"].id
            receiver_id = form.cleaned_data["receiver"].id
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data["description"]

            try:
                with transaction.atomic():
                    sender = BankAccount.objects.select_for_update().get(
                        id=sender_id
                    )
                    receiver = BankAccount.objects.select_for_update().get(
                        id=receiver_id
                    )

                    if sender.balance < amount:
                        raise ValueError(
                            "Insufficient account balance."
                        )

                    sender.balance -= amount
                    receiver.balance += amount

                    sender.save(update_fields=["balance"])
                    receiver.save(update_fields=["balance"])

                    Transaction.objects.create(
                        sender=sender,
                        receiver=receiver,
                        amount=amount,
                        status="SUCCESS",
                        description=description,
                    )

                messages.success(
                    request,
                    f"₹{amount} transferred successfully.",
                )

                return redirect("dashboard")

            except ValueError as exc:
                messages.error(request, str(exc))

    else:
        form = TransferForm()

    return render(
        request,
        "banking/transfer.html",
        {"form": form},
    )


def health_check(request):
    return JsonResponse(
        {
            "status": "UP",
            "service": "django-banking-app",
        }
    )