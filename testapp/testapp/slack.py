import logging

from django.contrib.auth import get_user_model, models

from slackbot.base import MessageProcessor


logger = logging.getLogger(__name__)


class DemoProcessor(MessageProcessor):
    def handle(self, message, user=None, channel=None, ts=None, raw=None):
        if not channel or channel[0] != 'D':
            return

        if 'echo' in message.lower():
            self.post_message(
                channel=channel, text=f'ECHO: {message[5:]}', thread_ts=ts
            )
            return self.PROCESSED
        
        if message.lower() == 'users':
            if self.user_has_perm(user, 'auth.view_user'):
                objs = ', '.join(list(get_user_model().objects.values_list('username', flat=True)))
                self.post_message(
                    channel=channel, text=f'Existing users\n```{objs}```', thread_ts=ts
                )
            else:
                self.post_message(
                    channel=channel, text=f'Nothing for you to see :no_entry:', thread_ts=ts
                )
            return self.PROCESSED

        if message.lower() == 'groups':
            if self.user_has_perm(user, 'auth.view_group'):
                objs = ', '.join(list(models.Group.objects.values_list('name', flat=True)))
                if not objs:
                    self.post_message(
                        channel=channel, text=f'no groups', thread_ts=ts
                    )
                else:
                    self.post_message(
                        channel=channel, text=f'Existing groups\n```{objs}```', thread_ts=ts
                    )
            else:
                self.post_message(
                    channel=channel, text=f'Nothing for you to see :no_entry:', thread_ts=ts
                )
            return self.PROCESSED
