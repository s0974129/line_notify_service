import requests
from uuid import uuid4
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from api.models import Subscriber
from api.serializers import PublishSerializer
from api.utils import getAccessTokenFromLine


class EmployeeViewSet(viewsets.ViewSet):
    """
    employee api
    """

    @swagger_auto_schema(
        operation_summary='訂閱line notify服務',
        responses={
            200:
                """
                ```
                    { 
                        "url" : 訂閱連結
                    }
                ```
                """,
            409:
                """
                ```
                    {
                        "message" : 錯誤訊息，該帳號已有資料
                    }
                ```
                """
        }
    )
    @action(detail=False, methods=["GET"], url_path="subscribe/(?P<account>[a-zA-z0-9]+)")
    def subscribe(self, request, account):
        """
        訂閱 line notify 服務
        ---
        * account : 訂閱者帳號
        """
        state = uuid4()
        subscribe_url = ("https://notify-bot.line.me/oauth/authorize?response_type=code&scope=notify"
                         "&response_mode=form_post&client_id={}"
                         "&redirect_uri={}&state={}").format(settings.LINE_CLIENT_ID, settings.REDIRECT_URI, state)

        subscriber, created = Subscriber.objects.get_or_create(account=account.upper())
        Subscriber.objects.filter(id=subscriber.id).update(state=state)

        if created:
            return Response(data={"url": subscribe_url}, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "該帳號已有訂閱資料"}, status=status.HTTP_409_CONFLICT)

    @swagger_auto_schema(
        operation_summary='發送 notify',
        request_body=PublishSerializer,
        responses={
            200:
                """
                ```
                    { 
                        "result" : 傳送結果
                    }
                ```
                """
        }
    )
    @action(detail=False, methods=["POST"], url_path="publish/(?P<account>[a-zA-z0-9]+)")
    def publish(self, request, account):
        """
        發送訊息給特定用戶
        """
        employee_data = Subscriber.objects.filter(account=account.upper())

        # print(request.data)

        serializer = PublishSerializer(data=request.data)

        if serializer.is_valid():
            response_status = 200
            response_message = ""
            notify_url = "https://notify-api.line.me/api/notify"
            for employee in employee_data:
                # 有access token的話直接用，沒有的話取access token
                access_token = employee.access_token
                if employee.access_token == "":
                    # call Line 取 access token
                    if employee.code != "":
                        access_token = getAccessTokenFromLine(employee)
                        if access_token == "":
                            response_status = 500
                            response_message = "跟Line取token失敗"
                        else:
                            Subscriber.objects.filter(id=employee.id).update(access_token=access_token)
                    else:
                        response_status = 400
                        response_message = "此員工未訂閱"

                if access_token != "":
                    notify_headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": "Bearer " + access_token
                    }
                    notify_data = {
                        "message": serializer.data["message"].replace('\\n', '\n').replace('\\t', '\t')
                    }

                    notify_response = requests.post(
                        notify_url,
                        data=notify_data,
                        headers=notify_headers,
                    )

                    if notify_response.status_code == 200:
                        notify_response_json = notify_response.json()
                        print(notify_response_json)
                    elif notify_response.status_code == 401:
                        # 表示user已解除連動導致token失效
                        # 刪除該employee
                        employee.delete()
                        response_status = 500
                        response_message = "發布失敗(使用者已取消訂閱)"

                        notify_response_json = notify_response.json()
                        print(notify_response_json)
                    else:
                        print(notify_response.status_code)
                        print(notify_response.text)
                        response_status = 500
                        response_message = "發布失敗"

            return Response(data={"status": response_status, "message": response_message}, status=response_status)

        else:
            return Response({'message': '輸入欄位錯誤'}, status=status.HTTP_400_BAD_REQUEST)
