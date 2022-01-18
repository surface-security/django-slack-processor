from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import autodiscover_modules

# IMPORT do not use "app_settings.py strategy" as that is not compatible with @override_settings (unittests)
# this strategy is
APP_SETTINGS = dict(
    BOT_TOKEN=None,
    APP_TOKEN=None,
    USER_MODEL='slackbot.User',
)


class SlackbotConfig(AppConfig):
    name = 'slackbot'

    def __init__(self, app_name: str, app_module) -> None:
        super().__init__(app_name, app_module)
        for k, v in APP_SETTINGS.items():
            _k = 'SLACKBOT_%s' % k
            if not hasattr(settings, _k):
                setattr(settings, _k, v)

    def ready(self):
        autodiscover_modules('slack')
