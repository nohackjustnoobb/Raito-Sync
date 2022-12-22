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
from django.contrib import admin
from django.urls import path
from main.views import List, Recommendation, Categories, Details, Search, Episode

urlpatterns = [
    path("admin/", admin.site.urls),
    path("list/", List.as_view()),
    path("recommendation/", Recommendation.as_view()),
    path("search/", Search.as_view()),
    path("episode", Episode.as_view()),
    path("categories", Categories.as_view()),
    path("details", Details.as_view()),
]
