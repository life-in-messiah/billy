#!/usr/bin/env python
"""
Billy - A Slackbot for integrating with realtime messaging platforms
"""
import os
from flask import Flask, request, Response
from slackclient import SlackClient
from twilio import twiml
from twilio.rest import TwilioRestClient

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", None)
SLACK_WEBHOOK_SECRET = os.environ.get("SLACK_WEBHOOK_SECRET", None)
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER", None)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", None)
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", None)

BOT = SlackClient(SLACK_BOT_TOKEN)
SMS = TwilioRestClient()
app = Flask(__name__)

def known_channels():
    response = BOT.api_call("channels.list")
    for channel in response['channels']:
        yield "#" + channel['name']

def archived_channels():
    pass #TODO

def safe_call(action, **kwargs):
    res = BOT.api_call(action, username="billy", icon_emoji=":iphone:", **kwargs)
    if not res['ok']:
        raise Exception("API call did not return OK: " + str(res))

def _log(message):
    safe_call("chat.postMessage",
              channel="#search-dev",
              text=message)

@app.route("/twilio", methods=["POST"])
def receive_message():
    response = twiml.Response()
    message = request.form["Body"]
    channel_name = "#sms_" + request.form["From"].replace("+", "")
    if channel_name not in known_channels():
        try:
            safe_call("channels.create", name=channel_name)
            #TODO: invite anybody active who is not a robot
            safe_call("chat.postMessage",
                      channel=channel_name,
                      text="Received: "+message)
            safe_call("chat.postMessage",
                      channel="#search-chats",
                      text="New message at: " + channel_name + \
                           "\nMessage: " + message,
                      link_names=1)
        except Exception as e:
            _log("Error while creating channel:\n" + str(e))
    else:
        #TODO: if the channel is archived, unarchive it and invite anybody active who is not a robot
        safe_call("chat.postMessage",
                  channel=channel_name,
                  text="Received: "+message)
    return Response(response.toxml(), mimetype="text/xml"), 200

@app.route("/slack", methods=["POST"])
def send_message():
    #if request.form["token"] == SLACK_WEBHOOK_SECRET:
        channel = request.form['channel_name']
        text = request.form['text'].replace("@billy ", "")
        if channel.startswith("sms_"):
            to_number = "+" + channel.replace("sms_", "")
            _log("Sending text to " + to_number)
            SMS.messages.create(to=to_number, from_=TWILIO_NUMBER, body=text)
            safe_call("chat.postMessage",
                      channel="#"+channel,
                      text="Sent: "+text)
        else:
            safe_call("chat.postMessage",
                      channel=channel,
                      text="Not a valid channel to send text messages from")
        return Response(), 200
    #_log("Encountered a 403")
    #return Response(), 403

if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.run()
