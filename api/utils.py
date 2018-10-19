import config
import onesignal as onesignal_sdk


def enviar_notificacao(notificacao = None):

    onesignal_client = onesignal_sdk.Client(user_auth_key="YmNlOWYwNTctYTI1MC00Mjc0LThmMjQtNmYxODg1NWEyMjVi",
                                        app={"app_auth_key": config.onesignal_rest_api_key, "app_id": config.onesignal_app_id})


    # create a notification
    new_notification = onesignal_sdk.Notification(contents={"en": "Message"})
    new_notification.set_parameter("headings", {"en": "Title"})

    # set target Segments
    new_notification.set_included_segments(["All"])
    new_notification.set_excluded_segments(["Inactive Users"])

    # send notification, it will return a response
    onesignal_response = onesignal_client.send_notification(new_notification)
    print(onesignal_response.status_code)
    print(onesignal_response.json())