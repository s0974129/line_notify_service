"""scepter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from rest_framework.routers import SimpleRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.openapi import Contact
from api.views import EmployeeViewSet
from app.views import welcome, index

schema_view = get_schema_view(
    openapi.Info(
        title='Line notify client API',
        default_version='0.0.1',
        description='LINE Notify service api',
        contact=Contact(name="wright.tsai", email="s0974129@gmail.com"),
    ),
    url=settings.REDIRECT_URI,
    public=True,
    permission_classes=[permissions.AllowAny]
)

router = SimpleRouter()
router.register(r'api/v1', EmployeeViewSet, basename='api/v1')
# print(router.urls)

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("docs/", schema_view.with_ui(), name="schema-swagger-ui"),
    path("", include(router.urls)),
    path("", welcome),
    path("index", index),

]
