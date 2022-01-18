from django.conf import settings

from slackbot import get_user_model
from logbasecommand.base import LogBaseCommand


class Command(LogBaseCommand):
    help = 'Re-sync Slack Users'

    def handle(self, *args, **options):
        # heavy import, delay for faster cold boot
        import slack_sdk

        # https://api.slack.com/docs/oauth-test-tokens
        sc = slack_sdk.WebClient(token=settings.SLACKBOT_BOT_TOKEN)

        all_members = []
        cursor = None

        while True:
            response = sc.users_list(cursor=cursor)
            cursor = response.get('response_metadata', {}).get('next_cursor')

            self.log('Retrieved %d', len(response['members']))
            all_members.extend(response['members'])
            if not cursor:
                break

        get_user_model().update_with_slack_data(all_members, self)
