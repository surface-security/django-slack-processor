from functools import lru_cache

__version__ = "0.1.7"


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


@lru_cache
def get_message_model():
    """
    use settings.SLACKBOT_MESSAGE_MODEL to use your own model for Slack messages
    """
    # all imports inside so package can be imported without django
    from django.apps import apps
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    try:
        return apps.get_model(settings.SLACKBOT_MESSAGE_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("SLACKBOT_MESSAGE_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "SLACKBOT_MESSAGE_MODEL refers to model '%s' that has not been installed" % settings.SLACKBOT_MESSAGE_MODEL
        )
