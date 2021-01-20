from Serveur.Message import SendSMSModel


def main():
    sms = SendSMSModel.SendSMSModel()
    sms.sendMessage('Test de ou guedin')


main()
