"""
Chat forms
"""
from django import forms


class MessageForm(forms.Form):
    """
    Form for sending a chat message
    """
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'message-input',
            'placeholder': 'Type your message...',
            'rows': 3,
            'maxlength': 5000
        }),
        max_length=5000,
        required=True,
        label=''
    )


class SearchUserForm(forms.Form):
    """
    Form for searching users to chat with
    """
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search username...',
            'class': 'search-input',
            'autofocus': True
        }),
        label=''
    )
