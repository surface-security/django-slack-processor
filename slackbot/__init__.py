from functools import lru_cache

__version__ = '0.0.3'

# set default_app_config when using django earlier than 3.2
try:
    import django

    if django.VERSION < (3, 2):
        default_app_config = 'slackbot.apps.SlackbotConfig'
except ImportError:
    pass


@lru_cache
def get_user_model():
    """
    use settings.SLACKBOT_USER_MODEL to use your own model for Slack users
    pretty much like django.contrib.auth.get_user_model
    """
    # all imports inside so package can be imported without django
    from django.apps import apps
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    try:
        return apps.get_model(settings.SLACKBOT_USER_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("SLACKBOT_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "SLACKBOT_USER_MODEL refers to model '%s' that has not been installed" % settings.SLACKBOT_USER_MODEL
        )
