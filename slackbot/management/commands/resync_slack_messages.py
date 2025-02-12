import time
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from logbasecommand.base import LogBaseCommand
from slackbot.models import SlackMessage, User


class Command(LogBaseCommand):
    help = "Get all the details and messages from Slack from the channels in scope"

    def handle(self, *args, **options) -> None:
        client = WebClient(token=settings.SLACKBOT_BOT_TOKEN)
        timestamp_limit = time.mktime(time.strptime("2024-01-01", "%Y-%m-%d"))
        next_cursor = None

        for channel, channel_id in settings.SLACKBOT_SLACK_CHANNELS.items():
            next_cursor = None
            while True:
                try:
                    response = client.conversations_history(
                        channel=channel_id,
                        cursor=next_cursor,
                        limit=20,
                        oldest=timestamp_limit,
                    )
                    last_h = 0
                    for message in response["messages"]:
                        thread_response = None
                        aware_thread_timestamp = None
                        text = message["text"]
                        message_from = message.get("user_profile", {}).get("display_name", "Unknown User")
                        time_stamp = datetime.fromtimestamp(float(message["ts"]))
                        aware_timestamp = timezone.make_aware(time_stamp, timezone.get_default_timezone())
                        now_h = time_stamp.strftime("%Y-%m-%d %H")
                        if last_h != now_h:
                            last_h = now_h

                        if aware_timestamp < timezone.now() - timezone.timedelta(days=365):
                            continue

                        try:
                            if message.get("bot_id"):
                                if message["bot_id"] in settings.SLACKBOT_BOT_EXCLUSIONS.values():
                                    continue

                                message_from_id = message["text"].split("<@")[1].split(">")[0]
                                if user := User.objects.filter(ext_id=message_from_id).first():
                                    message_from = user.name
                                else:
                                    message_from = "Unknown User"

                                text_list = str(message["text"]).split("*Description:*", 1)

                                if len(text_list) == 2:
                                    text = text_list[1]
                                else:
                                    text = "-"
                        except Exception as e:
                            self.log_warning("Error processing bot %s", message["bot_id"], e)

                        replies = []
                        if "thread_ts" in message:
                            thread_response = client.conversations_replies(channel=channel_id, ts=message["thread_ts"])
                            thread_response = thread_response["messages"][1:]
                            thread_timestamp = datetime.fromtimestamp(float(message["thread_ts"]))
                            aware_thread_timestamp = timezone.make_aware(
                                thread_timestamp, timezone.get_default_timezone()
                            )
                        if thread_response is not None:
                            for each in thread_response:
                                user = User.objects.filter(ext_id=each.get("user", "")).first()
                                if user:
                                    user = user.name
                                else:
                                    user = "Unknown"
                                replies.append({"user": user, "text": each["text"]})
                        reactions = []
                        for each in message.get("reactions", ""):
                            user = User.objects.filter(ext_id__in=each["users"]).first()
                            if user:
                                user = user.name
                            else:
                                user = "Unknown"
                            reactions.append(
                                {
                                    "name": each["name"],
                                    "users": user,
                                    "count": each["count"],
                                }
                            )

                        reply_users = list(
                            User.objects.filter(ext_id__in=message.get("reply_users", "")).values_list(
                                "name", flat=True
                            )
                        )
                        SlackMessage.objects.update_or_create(
                            ts=message["ts"],
                            channel=channel,
                            defaults={
                                "channel_id": channel_id,
                                "client_msg_id": message.get("client_msg_id", ""),
                                "time_stamp": aware_timestamp,
                                "reactions": reactions,
                                "reply_count": message.get("reply_count", 0),
                                "reply_users": reply_users,
                                "reply_users_count": message.get("reply_users_count", 0),
                                "team": message.get("team", ""),
                                "text": text,
                                "thread_timestamp": aware_thread_timestamp,
                                "type": message["type"],
                                "user": message["user"],
                                "message_from": message_from,
                                "user_team": message.get("user_team", ""),
                                "thread_message": replies,
                            },
                        )

                    next_cursor = response.get("response_metadata", {}).get("next_cursor")
                    if not next_cursor:
                        break
                except SlackApiError as e:
                    if e.response["error"] == "ratelimited":
                        retry_after = int(e.response.headers["Retry-After"])
                        self.log_warning("Rate limit hit. Retrying....")
                        time.sleep(retry_after)
                    else:
                        self.log_exception("Error fetching history: %s", e.response["error"])
                        break

        SlackMessage.objects.filter(time_stamp__lt=timezone.now() - timezone.timedelta(days=365)).delete()
