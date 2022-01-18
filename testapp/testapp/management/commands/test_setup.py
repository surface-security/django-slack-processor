from django.conf import settings
from django.contrib.auth import get_user_model, models
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

DEFAULT_PASSWORD = 'password'


class Command(BaseCommand):
    help = 'Add test users and groups (LOCAL DEV DB ONLY)'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--force', action='store_true', help='Skip safety checks and create users anyway')

    def handle(self, *args, **options):
        self.stdout.write(f'Default password: {DEFAULT_PASSWORD}')

        u, _ = get_user_model().objects.update_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
            },
        )
        u.set_password(DEFAULT_PASSWORD)
        u.save()
        self.stdout.write(f'Created user {u}')

        u, _ = get_user_model().objects.update_or_create(
            username='user',
            defaults={
                'first_name': 'Normal',
                'last_name': 'User',
                'is_staff': True,
                'is_active': True,
                'email': settings.TEST_USER_SLACK_EMAIL,
            },
        )
        u.set_password(DEFAULT_PASSWORD)
        u.save()
        self.stdout.write(f'Created user {u}')

        content_type = ContentType.objects.get_for_model(get_user_model())
        permission = models.Permission.objects.get(
            codename='view_user',
            content_type=content_type,
        )
        u.user_permissions.add(permission)
