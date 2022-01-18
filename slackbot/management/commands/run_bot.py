import unicodedata

from database_locks import locked
from django.conf import settings
from django.db import close_old_connections
from logbasecommand.base import LogBaseCommand
from slackbot.base import MessageProcessor

from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.builtin.client import SocketModeClient


@locked
class Command(LogBaseCommand):
    help = 'Run Slack bot.'
    client = None
    web = None
    my_name = None
    my_id = None
    my_id_match = None
    processors = []

    def add_arguments(self, parser):
        parser.add_argument('-t', '--token', action='store', help='Use TOKEN instead of the one in settings')

    def post_message(self, **kwargs):
        kwargs['as_user'] = kwargs.get('as_user', 1)
        return self.web.chat_postMessage(**kwargs)

    def post_ephemeral(self, **kwargs):
        kwargs['as_user'] = kwargs.get('as_user', True)
        return self.web.chat_postEphemeral(**kwargs)

    def handle_message(self, **payload):
        # same as requests, before and after processing
        close_old_connections()
        self.handle_message_really(**payload)

    def handle_message_really(self, **payload):
        event = payload.get('event')

        channel = event.get('channel')
        user = event.get('user')
        if not channel:
            return False

        team = event.get('team')
        ts = event.get('event_ts', event.get('ts', ''))
        message = event.get('text', '')
        message = unicodedata.normalize("NFKD", message)  # normalize stuff like non-breaking spaces (/xa0)

        # if `as_user=True`, check user to make sure we do not reply to `self`
        if user == self.my_id:
            return False

        # FIXME: too spammy to have this check commented out...
        # # D for DM, G for private channel and group DM, C for channel
        # # not need to mention if in DM
        # if channel[0] != 'D' and self.my_id_match not in message:
        #     return

        processed_at_least_one = False
        for p in self.processors:
            try:
                r = p.process(message, user=user, channel=channel, ts=ts, raw=event)
                if r:
                    if not isinstance(r, tuple):
                        r = (r,)
                    if MessageProcessor.PROCESSED in r:
                        processed_at_least_one = True
                    if MessageProcessor.STOP in r:
                        break
            except Exception as exc:
                self.log_exception(f'Processor {str(p)} failed with {str(exc)} for message {message}')

        # If private DM
        if channel[0] == 'D':
            if not team:
                return False

            # check if message was hidden, can't react to hidden messages
            if not processed_at_least_one and not event.get('hidden'):
                # React to User message with emojis if no results are found.
                self.web.reactions_add(name='surface_not_found', channel=channel, timestamp=ts)
                # FIXME generic message here please
                self.post_ephemeral(
                    channel=channel,
                    text='SurfaceBot will respond based on the context, so try to include IPs, Hostnames, Applications Name in the message.',
                    user=user,
                )

        return processed_at_least_one

    def set_up(self, **payload):
        data = self.web.auth_test()
        self.my_id = data.get("user_id")
        self.my_id_match = '<@%s>' % self.my_id
        self.my_name = data.get("user")

        self.processors = [x(self.client, self.web) for x in MessageProcessor.__subclasses__()]
        self.stdout.write(f'Connected as {self.my_name}')
        self.stdout.write(
            f"Processors: {','.join(f'{x.__class__.__module__}.{x.__class__.__name__}' for x in self.processors)}"
        )

    def process(self, client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)

            if req.payload["event"]["type"] == "message" and req.payload["event"].get("subtype") is None:
                return self.handle_message(**req.payload)

    def handle(self, *args, **options):
        # faster cold boot
        from slack_sdk.web.client import WebClient

        self.web = WebClient(token=settings.SLACKBOT_BOT_TOKEN)
        self.client = SocketModeClient(app_token=settings.SLACKBOT_APP_TOKEN, web_client=self.web, logger=self.logger)
        self.set_up()
        self.client.socket_mode_request_listeners.append(self.process)
        self.stdout.write('Connecting...\n')
        self.client.connect()

        # don't stop this process.
        from threading import Event

        Event().wait()
