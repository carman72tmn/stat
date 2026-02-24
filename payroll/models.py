from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class EmployeeProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
	position = models.CharField(max_length=120, blank=True)
	department = models.CharField(max_length=120, blank=True)

	def __str__(self):
		return f"{self.user.get_full_name() or self.user.username}"


class SalaryCalculation(models.Model):
	employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="salary_calculations")
	period_start = models.DateField()
	period_end = models.DateField()

	base_salary = models.DecimalField(max_digits=12, decimal_places=2)
	worked_hours = models.DecimalField(max_digits=8, decimal_places=2)
	standard_hours = models.DecimalField(max_digits=8, decimal_places=2, default=160)
	overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	overtime_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.50)

	bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)

	tax_rate = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		default=13.00,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
	)
	insurance_rate = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		default=0,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
	)

	gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	calculated_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="created_salary_calculations",
	)

	class Meta:
		ordering = ["-created_at"]
		permissions = [
			("view_all_calculations", "Can view all salary calculations"),
			("calculate_for_others", "Can calculate salary for other users"),
		]

	def __str__(self):
		return f"{self.employee.username}: {self.period_start} - {self.period_end}"

	def recalculate(self):
		hourly_rate = self.base_salary / self.standard_hours if self.standard_hours else 0
		regular_amount = hourly_rate * self.worked_hours
		overtime_amount = hourly_rate * self.overtime_hours * self.overtime_multiplier

		self.gross_salary = regular_amount + overtime_amount + self.bonus + self.allowance - self.deductions
		self.tax_amount = self.gross_salary * self.tax_rate / 100
		self.insurance_amount = self.gross_salary * self.insurance_rate / 100
		self.net_salary = self.gross_salary - self.tax_amount - self.insurance_amount

	def save(self, *args, **kwargs):
		self.recalculate()
		super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
	if created:
		EmployeeProfile.objects.get_or_create(user=instance)
