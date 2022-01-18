from unittest import mock

from django.core import management
from django.test import TestCase

from slackbot import models


class Test(TestCase):
    @mock.patch('slack_sdk.WebClient')
    def test_resync_command(self, wc_mock):
        api_mock = wc_mock.return_value
        api_mock.users_list.return_value = {'members': [{'id': 'x', 'name': 'user.name', 'profile': {}}]}
        management.call_command('resync_slack')
        wc_mock.assert_called_once()
        api_mock.users_list.assert_called_once_with(cursor=None)

        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(models.User.objects.first().username, 'user.name')
