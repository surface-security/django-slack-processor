import unittest
from unittest.mock import patch, MagicMock
from slackbot.management.commands.run_bot import Command
from slack_sdk.socket_mode.request import SocketModeRequest


class TestSlackBotCommand(unittest.TestCase):
    def setUp(self):
        self.command = Command()
        self.command.web = MagicMock()
        self.command.client = MagicMock()
        self.command.my_id = "U123456"
        self.command.my_id_match = "<@U123456>"
        self.command.processors = []

    @patch("slackbot.management.commands.run_bot.close_old_connections")
    def test_handle_message(self, mock_close_old_connections):
        payload = {
            "event": {
                "channel": "C12345",
                "user": "U67890",
                "text": "Hello, bot!",
                "ts": "123456.789",
            }
        }
        result = self.command.handle_message(**payload)
        self.assertFalse(result)  # No processors, so should return False

    @patch("threading.Event.wait", return_value=None)
    @patch("slackbot.management.commands.run_bot.SocketModeClient")
    @patch("slackbot.management.commands.run_bot.settings")
    def test_handle(self, mock_settings, mock_socket_client, mock_event_wait):
        mock_settings.SLACKBOT_BOT_TOKEN = "xoxb-123"
        mock_settings.SLACKBOT_APP_TOKEN = "xapp-123"

        mock_client_instance = mock_socket_client.return_value
        self.command.set_up = MagicMock()
        self.command.handle()

        self.command.set_up.assert_called_once()
        mock_client_instance.connect.assert_called_once()

    def test_handle_reaction(self):
        payload = {
            "event": {
                "type": "reaction_added",
                "item": {"channel": "C12345"},
                "user": "U67890",
                "event_ts": "123456.789",
            }
        }
        result = self.command.handle_reaction(**payload)
        self.assertFalse(result)  # No processors, so should return False

    def test_process_event_message(self):
        request = SocketModeRequest(
            type="events_api",
            envelope_id="envelope123",
            payload={"event": {"type": "message", "subtype": None, "text": "Hello!"}},
        )

        self.command.handle_message = MagicMock(return_value=True)
        result = self.command.process(self.command.client, request)

        self.command.handle_message.assert_called_once()
        self.assertTrue(result)

    def test_post_message(self):
        self.command.post_message(channel="C12345", text="Hello!")
        self.command.web.chat_postMessage.assert_called_once_with(channel="C12345", text="Hello!", as_user=1)

    def test_post_ephemeral(self):
        self.command.post_ephemeral(channel="C12345", text="Hello!", user="U67890")
        self.command.web.chat_postEphemeral.assert_called_once_with(
            channel="C12345", text="Hello!", user="U67890", as_user=True
        )

    @patch(
        "slackbot.management.commands.run_bot.unicodedata.normalize",
        return_value="Hello bot!",
    )
    def test_handle_message_really_reacts_when_no_processors(self, mock_normalize):
        self.command.web.reactions_add = MagicMock()
        self.command.post_ephemeral = MagicMock()

        payload = {
            "event": {
                "channel": "D12345",
                "user": "U67890",
                "text": "Hello!",
                "ts": "123456.789",
                "team": "T123",
            }
        }

        self.command.handle_message_really(**payload)

        self.command.web.reactions_add.assert_called_once_with(
            name="surface_not_found", channel="D12345", timestamp="123456.789"
        )
        self.command.post_ephemeral.assert_called_once()


if __name__ == "__main__":
    unittest.main()
