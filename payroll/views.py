from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import SalaryCalculatorForm, UserRegisterForm
from .models import SalaryCalculation


def register_view(request):
	if request.user.is_authenticated:
		return redirect("dashboard")

	if request.method == "POST":
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Регистрация успешно выполнена.")
			return redirect("dashboard")
	else:
		form = UserRegisterForm()

	return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard_view(request):
	if request.method == "POST":
		form = SalaryCalculatorForm(request.POST, user=request.user)
		if form.is_valid():
			calculation = form.save(commit=False)

			if request.user.is_superuser or request.user.has_perm("payroll.calculate_for_others"):
				calculation.employee = form.cleaned_data["employee"]
			else:
				calculation.employee = request.user

			calculation.calculated_by = request.user
			calculation.save()

			messages.success(request, "Расчёт сохранён.")
			return redirect("dashboard")
	else:
		form = SalaryCalculatorForm(user=request.user)

	if request.user.is_superuser or request.user.has_perm("payroll.view_all_calculations"):
		calculations = SalaryCalculation.objects.select_related("employee", "calculated_by")
	else:
		calculations = request.user.salary_calculations.select_related("employee", "calculated_by")

	context = {
		"form": form,
		"calculations": calculations[:20],
	}
	return render(request, "payroll/dashboard.html", context)
