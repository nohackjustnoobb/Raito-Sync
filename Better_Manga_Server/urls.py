"""Better_Manga_Server URL Configuration

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
from django.urls import path
from rest_framework.authtoken import views
from main.views import (
    List,
    Suggestion,
    Drivers,
    getManga,
    Search,
    Chapter,
    Proxy,
    Online,
)
from user.views import MyInfo, Collections, Histories, Clear, Create

urlpatterns = [
    path("list", List.as_view()),
    path("suggestion", Suggestion.as_view()),
    path("search", Search.as_view()),
    path("chapter", Chapter.as_view()),
    path("manga", getManga),
    path("driver", Drivers.as_view()),
    path("driver/proxy", Proxy.as_view()),
    path("driver/online", Online.as_view()),
    path("user/me", MyInfo.as_view()),
    path("user/clear", Clear.as_view()),
    path("user/create", Create.as_view()),
    path("user/collections", Collections.as_view()),
    path("user/histories", Histories.as_view()),
    path("user/token", views.obtain_auth_token),
]
