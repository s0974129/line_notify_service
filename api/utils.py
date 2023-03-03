import requests
from django.conf import settings
from api.models import Subscriber


def getAccessTokenFromLine(subscriber: Subscriber) -> str:
    """
    向Line取access token
    employee: employee model

    return: str(access token)
    """
    token_url = "https://notify-bot.line.me/oauth/token"
    post_data = {
        "grant_type": "authorization_code",
        "redirect_uri": settings.REDIRECT_URI,
        "client_id": settings.LINE_CLIENT_ID,
        "client_secret": settings.LINE_CLIENT_SECRET,
        "code": subscriber.code,
    }
    token_response = requests.post(
        token_url,
        data=post_data
    )
    if token_response.status_code == 200:
        token_response_json = token_response.json()
        access_token = token_response_json["access_token"]

        return access_token
    else:
        print(token_response.status_code)
        print(token_response.text)
        return ""
