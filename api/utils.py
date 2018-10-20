# -*- coding: utf-8 -*-
from django.conf import settings
import onesignal as onesignal_sdk

def enviar_notificacao(notificacao):

    onesignal_client = onesignal_sdk.Client(
        user_auth_key = settings.ONESIGNAL_AUTH_ID,
        app = { 
            'app_auth_key': settings.ONESIGNAL_API_KEY,
            'app_id': settings.ONESIGNAL_APP_ID
        }
    )

    # create a notification
    nova_notificacao = onesignal_sdk.Notification(
        contents = {
            'en': notificacao['mensagem'],
            'pt-br': notificacao['mensagem']
        }
    )
    nova_notificacao.set_parameter(
        'headings', {
            'en': notificacao['titulo'],
            'pt-br': notificacao['titulo']
        }
    )
    nova_notificacao.set_parameter('url', settings.APP_URL + notificacao['url'])
    nova_notificacao.set_target_devices([notificacao['user_id']])

    # send notification, it will return a response
    onesignal_response = onesignal_client.send_notification(nova_notificacao)
    print(onesignal_response.status_code)
    print(onesignal_response.json())