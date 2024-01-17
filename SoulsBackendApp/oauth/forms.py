from django import forms

from . import validators


class GenerateCodeForm(forms.Form):
    email = forms.EmailField(validators=[validators.user_email_exists])


class VerifyCodeForm(forms.Form):
    id = forms.CharField(validators=[validators.user_id_exists])
    auth_code = forms.CharField(min_length=8, max_length=8)
