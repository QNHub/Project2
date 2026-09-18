from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["body"]
        labels = {"body": ""}
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Write a message...",
                    "class": "form-control",
                }
            ),
        }
