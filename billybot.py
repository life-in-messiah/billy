#!/usr/bin/env python
"""
Billy - A Slackbot for integrating with realtime messaging platforms
"""
import os
from slackclient import SlackClient


class Billy:

    def __init__(self):
        self.client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

    def send_slack_message(self, channel, text):
        res = self.client.api_call("chat.postMessage", channel=channel, text=text, as_user=True)
        if not res['ok']:
            raise AttributeError("API call did not return OK: " + str(res))
