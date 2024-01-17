from unittest.mock import MagicMock

import pytest
from django.test import TestCase
from slackbot.base import ExitSlackCommand, MessageProcessor, NoMatchSlackCommand, SlackArgumentParser


class Test(TestCase):
    def test_arg_parser(self):
        rtm_client = MagicMock()
        web_client = MagicMock()
        processor = MessageProcessor(rtm_client, web_client)

        parser = SlackArgumentParser(
            "cmd",
            description="Some description",
            message_processor=processor,
            channel="#channel",
            ts=None,
        )

        parser.add_argument("str", help="some string")

        with pytest.raises(NoMatchSlackCommand):
            parser.parse_args("someothercmd bla bla")

        with pytest.raises(NoMatchSlackCommand):
            parser.parse_args("cmdnot bla bla")

        with pytest.raises(ExitSlackCommand, match=".*the following arguments are required: str.*"):
            parser.parse_args("cmd")

        parser.parse_args("cmd yolo")
