from __future__ import print_function

import africastalking
from flask import current_app

class SMS:
    def __init__(self):
    # Set your app credentials
        self.username = '*****'
        self.api_key = '****'
        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

    def send(self,recipient,message):
        # Set the numbers you want to send to in international format
        recipients = []
        for rec in recipient:
            if rec.startswith('07'):
                rec = '+254' + rec[1:]
                recipients.append(rec)

        recipient = recipients
        #send the notification
        return self.sms.send(message, recipient)
