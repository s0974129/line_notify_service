import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from api.models import Subscriber


@csrf_exempt
@require_http_methods(["GET", "POST"])
def welcome(request):
    """
    web hook for Line
    """
    if request.method == "POST":
        data = request.POST
        # print(data)
        if "state" in data and "code" in data:
            Subscriber.objects.filter(state=data["state"]).update(code=data["code"])
            return render(request, "welcome.html", context={"notify_name": settings.LINE_NOTIFY_NAME})
        else:
            html = "<html><body>請勿拍打餵食</body></html>"
            return HttpResponse(html)
    elif request.method == "GET":
        html = "<html><body>首頁</body></html>"
        return HttpResponse(html)


def index(request):
    """
    首頁
    """
    employees = Subscriber.objects.all().values("id", "account", "message")
    employees = json.dumps(list(employees))
    # print(employees)

    return render(request, "index.html", context={"employees": employees, "notify_name": settings.LINE_NOTIFY_NAME})
