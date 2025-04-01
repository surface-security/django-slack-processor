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
