from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создаёт базовые роли и назначает права доступа"

    def handle(self, *args, **options):
        roles = {
            "HR": [
                "view_user",
                "add_user",
                "change_user",
                "view_salarycalculation",
                "view_all_calculations",
            ],
            "Accountant": [
                "add_salarycalculation",
                "change_salarycalculation",
                "view_salarycalculation",
                "view_all_calculations",
                "calculate_for_others",
            ],
            "Manager": [
                "view_salarycalculation",
                "view_all_calculations",
            ],
            "Employee": [
                "add_salarycalculation",
                "view_salarycalculation",
            ],
        }

        for role, codename_list in roles.items():
            group, _ = Group.objects.get_or_create(name=role)
            permissions = Permission.objects.filter(codename__in=codename_list)
            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f"Роль {role} настроена"))

        self.stdout.write(self.style.SUCCESS("Роли и права успешно инициализированы."))
