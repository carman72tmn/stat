from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import SalaryCalculation


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class SalaryCalculatorForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=User.objects.none(), required=False)

    class Meta:
        model = SalaryCalculation
        fields = [
            "employee",
            "period_start",
            "period_end",
            "base_salary",
            "worked_hours",
            "standard_hours",
            "overtime_hours",
            "overtime_multiplier",
            "bonus",
            "allowance",
            "deductions",
            "tax_rate",
            "insurance_rate",
        ]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        can_pick_employee = user.is_superuser or user.has_perm("payroll.calculate_for_others")
        if can_pick_employee:
            self.fields["employee"].queryset = User.objects.filter(is_active=True).order_by("username")
            self.fields["employee"].required = True
        else:
            self.fields.pop("employee")

    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get("period_start")
        period_end = cleaned_data.get("period_end")
        standard_hours = cleaned_data.get("standard_hours")

        if period_start and period_end and period_end < period_start:
            self.add_error("period_end", "Дата окончания периода не может быть раньше даты начала.")

        if standard_hours is not None and standard_hours <= 0:
            self.add_error("standard_hours", "Норма часов должна быть больше нуля.")

        return cleaned_data
