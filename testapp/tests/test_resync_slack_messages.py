from unittest import mock
from django.core import management
from django.test import TestCase
from slackbot import models

SLACK_RESPONSE = {
    "ok": True,
    "messages": [
        {
            "user": "XXXXX",
            "type": "message",
            "ts": "1739613553.162449",
            "client_msg_id": "1",
            "text": "Good morning, please could I have access to this repo if this is the right place?  <https://test.com> thank you",
            "team": "YYYYY",
            "user_team": "YYYYY",
            "source_team": "YYYYY",
            "user_profile": {
                "avatar_hash": "zzzzz",
                "image_72": "https://avatars.slack-edge.com/zzzzz",
                "first_name": "Joe",
                "real_name": "Joe Doe",
                "display_name": "Joe Doe",
                "team": "a",
                "name": "bo",
                "is_restricted": False,
                "is_ultra_restricted": False,
            },
            "thread_ts": "1739613553.162449",
            "reply_count": 11,
            "reply_users_count": 2,
            "latest_reply": "1739626662.712709",
            "reply_users": ["test1", "test2"],
            "is_locked": False,
            "subscribed": False,
            "blocks": [
                {
                    "type": "rich_text",
                    "block_id": "CDI6a",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Good morning, please could I have access to this repo if this is the right place?",
                                },
                                {
                                    "type": "link",
                                    "url": "https://github.com/x",
                                },
                                {"type": "text", "text": " thank you"},
                            ],
                        }
                    ],
                }
            ],
            "reactions": [{"name": "tick", "users": ["test1"], "count": 1}],
        },
        {
            "user": "s",
            "type": "message",
            "ts": "1739613625.366299",
            "client_msg_id": "2",
            "text": "hello <@s>, what is your github username?",
            "team": "b",
            "user_team": "b",
            "source_team": "b",
            "user_profile": {
                "avatar_hash": "1",
                "image_72": "https://avatars.slack-edge.com/1",
                "first_name": "Joe",
                "real_name": "Joe Doe",
                "display_name": "test",
                "team": "y",
                "name": "00",
                "is_restricted": False,
                "is_ultra_restricted": False,
            },
            "thread_ts": "1739613553.162449",
            "parent_user_id": "U04",
            "blocks": [
                {
                    "type": "rich_text",
                    "block_id": "OeaW8",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {"type": "text", "text": "hello "},
                                {"type": "user", "user_id": "U040"},
                                {
                                    "type": "text",
                                    "text": ", what is your github username?",
                                },
                            ],
                        }
                    ],
                }
            ],
        },
    ],
    "has_more": False,
}


SLACK_RESPONSE_WITH_BOT = {
    "ok": True,
    "messages": [
        {
            "bot_id": "ABCD",
            "user": "U040",
            "type": "message",
            "ts": "1739626662.712709",
            "text": "<@BOTUSER> *Description:* This is a test message",
            "team": "TEAM",
        },
        {
            "bot_id": "EXCLUDED",
            "user": "U01B",
            "type": "message",
            "ts": "1739626662.712709",
            "text": "This should be skipped",
            "team": "TEAM",
        },
    ],
    "has_more": False,
}


class TestResyncSlackMessages(TestCase):
    def setUp(self):
        models.SlackMessage.objects.all().delete()
        self.user = models.User.objects.create(ext_id="BOTUSER", name="Test User")

    @mock.patch("slack_sdk.WebClient")
    def test_resync_command(self, wc_mock):
        api_mock = wc_mock.return_value
        api_mock.conversations_history.return_value = SLACK_RESPONSE
        management.call_command("resync_slack_messages")
        wc_mock.assert_called_once()
        api_mock.conversations_history.assert_any_call(channel=mock.ANY, cursor=None, limit=20, oldest=mock.ANY)
        self.assertEqual(models.SlackMessage.objects.count(), 2)

    @mock.patch("slackbot.management.commands.resync_slack_messages.WebClient")
    @mock.patch("django.conf.settings.SLACKBOT_BOT_EXCLUSIONS", {"Excluded Bot": "EXCLUDED"})
    def test_resync_command_with_bot_messages(self, wc_mock):
        api_mock = wc_mock.return_value
        api_mock.conversations_history.return_value = SLACK_RESPONSE_WITH_BOT

        management.call_command("resync_slack_messages")

        wc_mock.assert_called_once()
        api_mock.conversations_history.assert_any_call(channel=mock.ANY, cursor=None, limit=20, oldest=mock.ANY)

        self.assertEqual(models.SlackMessage.objects.count(), 1)

        slack_msg = models.SlackMessage.objects.first()
        self.assertEqual(slack_msg.message_from, "Test User")
        self.assertEqual(slack_msg.text, " This is a test message")
