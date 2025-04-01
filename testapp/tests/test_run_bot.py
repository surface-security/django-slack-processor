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


if __name__ == "__main__":
    unittest.main()
