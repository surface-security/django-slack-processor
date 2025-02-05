from unittest import mock
from django.core import management
from django.test import TestCase
from slackbot import models

SLACK_RESPONSE = {
    "ok": True,
    "oldest": "1738713600.000000",
    "messages": [
        {
            "user": "U02MB3L4YBV",
            "type": "message",
            "ts": "1738760392.589109",
            "client_msg_id": "56f29274-afc1-4d86-b8a7-464433e75b3a",
            "text": "Hello, can someone please review and merge this: <https://gitlab.app/cloudflare/-/merge_requests/0000> ? :women_thanks:",
            "team": "XXXXXXXXX",
            "user_team": "XXXXXXXXX",
            "source_team": "XXXXXXXXX",
            "user_profile": {
                "avatar_hash": "0fa9732db392",
                "image_72": "https://avatars.slack-edge.com/2024-01-10/xxxxxx.png",
                "first_name": "Joe",
                "real_name": "Joe Doe",
                "display_name": "Joe Doe",
                "team": "XXXXXXXXX",
                "name": "00u1wwkokbuk29m05417",
                "is_restricted": False,
                "is_ultra_restricted": False,
            },
            "blocks": [
                {
                    "type": "rich_text",
                    "block_id": "2SkH1",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Hello, can someone please review and merge this: ",
                                },
                                {
                                    "type": "link",
                                    "url": "https://gitlab.app/cloudflare/-/merge_requests/0000",
                                },
                                {"type": "text", "text": " ? "},
                                {"type": "emoji", "name": "women_thanks"},
                            ],
                        }
                    ],
                }
            ],
        },
    ],
    "has_more": False,
    "pin_count": 3,
    "channel_actions_ts": 1664441977,
    "channel_actions_count": 0,
}


class TestResyncSlackMessages(TestCase):
    def setUp(self):
        models.SlackMessage.objects.all().delete()

    @mock.patch("slack_sdk.WebClient")
    def test_resync_command(self, wc_mock):
        api_mock = wc_mock.return_value
        api_mock.conversations_history.return_value = SLACK_RESPONSE
        management.call_command("resync_slack_messages")
        wc_mock.assert_called_once()
        api_mock.conversations_history.assert_any_call(channel=mock.ANY, cursor=None, limit=20, oldest=mock.ANY)
        self.assertEqual(models.SlackMessage.objects.count(), 1)
