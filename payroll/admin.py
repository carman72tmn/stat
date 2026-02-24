from django.contrib import admin

from .models import EmployeeProfile, SalaryCalculation


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "position", "department")
	search_fields = ("user__username", "user__first_name", "user__last_name", "position", "department")


@admin.register(SalaryCalculation)
class SalaryCalculationAdmin(admin.ModelAdmin):
	list_display = (
		"employee",
		"period_start",
		"period_end",
		"gross_salary",
		"tax_amount",
		"insurance_amount",
		"net_salary",
		"calculated_by",
		"created_at",
	)
	list_filter = ("period_start", "period_end", "created_at")
	search_fields = ("employee__username", "employee__first_name", "employee__last_name")
	readonly_fields = ("gross_salary", "tax_amount", "insurance_amount", "net_salary", "created_at")


admin.site.site_header = "Панель администрирования Payroll"
admin.site.site_title = "Payroll Admin"
admin.site.index_title = "Управление пользователями и расчётами"
