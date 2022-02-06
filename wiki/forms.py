from .models import Argument
from django import forms
from django.contrib.admin import widgets


class ArgumentSearchForm(forms.Form):
    search_text = forms.CharField(
                    required=False,
                    label='Search argument:',
                    widget=forms.TextInput(attrs={'placeholder': 'search here!'})
                  )

    search_date_start = forms.DateField(
                    required=False,
                    label='Published From:',
                    widget=widgets.AdminDateWidget()
                  )

    search_date_end = forms.DateField(
                    required=False,
                    label='To:',
                    widget=widgets.AdminDateWidget()
                  )

    search_isSupportive = forms.BooleanField(
                    required=False,
                    label='Supportive'
                  )

    search_isAttacking = forms.BooleanField(
                    required=False,
                    label='Attacking'
                )

    search_acceptance_min = forms.DecimalField(
                    required=False,
                    decimal_places=2,
                    label='From acceptability'
                  )

    search_acceptance_max = forms.DecimalField(
                    required=False,
                    decimal_places=2,
                    label='To'
                  )

    search_language = forms.CharField(
                    required=False,
                    label='Language'
                  )