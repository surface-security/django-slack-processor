from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model as get_auth_user_model

from slackbot import get_user_model


class UserMixin:
    def convert_to_auth_user(self):
        return get_auth_user_model().objects.filter(email__iexact=self.email).first()

    def has_perm(self, perm):
        auth_user = self.convert_to_auth_user()
        # no user, no check, no pass
        if not auth_user:
            return False

        return auth_user.has_perm(perm)

    @classmethod
    def user_id_has_perm(cls, ext_id, perm):
        user = get_user_model().objects.filter(ext_id=ext_id).first()
        if not user:
            return False
        return user.has_perm(perm)

    @classmethod
    def update_with_slack_data(cls, members_list, cmd):
        sync_stamp = timezone.now()

        for user in members_list:
            if user.get('deleted', False):
                # save minimal data only
                cls.objects.update_or_create(
                    ext_id=user['id'],
                    defaults={
                        'username': user['name'],
                        'active': False,
                        'is_bot': user.get('is_bot', False),
                        'is_admin': user.get('is_admin', False),
                        'last_seen': sync_stamp,
                    },
                )
            else:
                photo = user['profile'].get('image_72')
                # try to find better photo (as full version)
                for img_key in ['image_original', 'image_1024', 'image_512', 'image_192']:
                    if img_key in user['profile']:
                        photo = user['profile'][img_key]
                        break

                cls.objects.update_or_create(
                    ext_id=user['id'],
                    defaults={
                        'username': user['name'],
                        'active': True,
                        'is_bot': user.get('is_bot', False),
                        'is_admin': user.get('is_admin', False),
                        'last_seen': sync_stamp,
                        'name': user['profile'].get('real_name_normalized', ''),
                        'photo_thumb': user['profile'].get('image_72'),
                        'photo': photo,
                        'email': user['profile'].get('email'),
                    },
                )

        cls.objects.filter(active=True, last_seen__lt=sync_stamp).update(active=False)


class User(UserMixin, models.Model):
    ext_id = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(db_index=True, null=True, blank=True)
    photo_thumb = models.CharField(max_length=255, blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    is_bot = models.BooleanField(default=False, db_index=True)
    is_admin = models.BooleanField(default=False, db_index=True)

    active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return f'{self.username} [{self.ext_id}]'
