from django import forms

from .models import BankAccount


class TransferForm(forms.Form):
    sender = forms.ModelChoiceField(
        queryset=BankAccount.objects.all(),
        label="From account",
    )
    receiver = forms.ModelChoiceField(
        queryset=BankAccount.objects.all(),
        label="To account",
    )
    amount = forms.DecimalField(
        min_value=1,
        max_digits=12,
        decimal_places=2,
    )
    description = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Transfer description",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        sender = cleaned_data.get("sender")
        receiver = cleaned_data.get("receiver")
        amount = cleaned_data.get("amount")

        if sender and receiver and sender == receiver:
            raise forms.ValidationError(
                "Sender and receiver cannot be the same."
            )

        if sender and amount and sender.balance < amount:
            raise forms.ValidationError(
                "Insufficient account balance."
            )

        return cleaned_data