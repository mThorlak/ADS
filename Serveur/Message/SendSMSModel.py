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
        client = Client(self.account_sid, self.auth_token)
        message = client.messages \
            .create(
            body='Test pour ADS',
            from_='+14322879550',
            to='+33679524688'
        )

        print(message.sid)

