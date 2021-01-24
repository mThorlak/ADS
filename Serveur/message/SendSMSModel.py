from Serveur.secrets import twilio_credentials
from twilio.rest import Client


class SendSMSModel:
    account_sid = ""
    auth_token = ""
    content = ""

    def __init__(self):
        self.account_sid = twilio_credentials.ACCOUNT_SID
        self.auth_token = twilio_credentials.AUTH_TOKEN

        # print(message.sid)

    def sendMessage(self, content):
        if isinstance(content, str):
            client = Client(self.account_sid, self.auth_token)
            message = client.messages \
                .create(
                body =content,
                from_=twilio_credentials.SENDER_PHONE_NUMBER,
                to=twilio_credentials.RECIPIENTS_PHONE_NUMBER
            )

            print("message sending... " + message.sid)

        else:
            print("Cannot send a non string message")
