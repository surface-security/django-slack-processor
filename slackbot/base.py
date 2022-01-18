import argparse
import shlex
from typing import NoReturn, Optional, Sequence, Union
from slackbot import get_user_model


class MessageProcessor:
    STOP = 1
    PROCESSED = 2

    handle_bot_messages = False

    def __init__(self, rtm_client, web_client) -> None:
        self.client = rtm_client
        self.web = web_client

    @staticmethod
    def user_has_perm(user, perm):
        return get_user_model().user_id_has_perm(user, perm)

    def post_message(self, **kwargs):
        kwargs["as_user"] = kwargs.get("as_user", 1)
        return self.web.chat_postMessage(**kwargs)

    def post_ephemeral(self, **kwargs):
        kwargs["as_user"] = kwargs.get("as_user", 1)
        return self.web.chat_postEphemeral(**kwargs)

    def process(self, message, **kw) -> Optional[Union[int, tuple[int, int]]]:
        """
        :return: None, self.STOP, self.PROCESSED, or tuple PROCESSED,STOP

        PROCESSED if anything was done with input
        STOP if no other processor should be called after this one

        any other value will be ignored
        """
        if not self.handle_bot_messages and "bot_id" in kw.get("raw", {}):
            return
        return self.handle(message, **kw)

    def handle(self, message, user=None, channel=None, ts=None, raw=None) -> Optional[Union[int, tuple[int, int]]]:
        """
        :return: None, self.STOP, self.PROCESSED, or tuple PROCESSED,STOP

        PROCESSED if anything was done with input
        STOP if no other processor should be called after this one

        any other value will be ignored
        """
        raise NotImplementedError("abstract method")


class NoMatchSlackCommand(Exception):
    pass


class ExitSlackCommand(Exception):
    def __init__(self, message: Optional[str]) -> None:
        super().__init__(message)


class SlackArgumentParser(argparse.ArgumentParser):
    def __init__(
        self,
        command: Optional[str],
        description: Optional[str],
        message_processor: MessageProcessor,
        channel: Optional[str],
        ts: Optional[str],
    ) -> None:
        self.message_processor = message_processor
        self.channel = channel
        self.ts = ts
        super().__init__(prog=command, description=description, exit_on_error=False)

    def parse_args(self, args: Optional[Union[str, Sequence[str]]] = None, namespace=None):
        if not args:
            raise NoMatchSlackCommand

        prog = self.prog.lower()

        if isinstance(args, str):
            if not args.lower().startswith(prog):
                raise NoMatchSlackCommand
            args = shlex.split(args)
        elif args[0].lower() != prog:
            raise NoMatchSlackCommand

        return super().parse_args(args[1:], namespace)

    def exit(self, status: int = 0, message: Optional[str] = None) -> NoReturn:
        if message:
            self._print_message(message)
        raise ExitSlackCommand(message)

    def _print_message(self, message: str, file=None) -> None:
        if message:
            self.message_processor.post_message(channel=self.channel, text=message, thread_ts=self.ts)

    def print_usage(self, file=None) -> None:
        self._print_message("```\n" + self.format_usage() + "```", file)

    def print_help(self, file=None) -> None:
        self._print_message("```\n" + self.format_help() + "```", file)
