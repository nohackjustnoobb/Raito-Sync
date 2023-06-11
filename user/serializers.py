from rest_framework import serializers
from .models import User, Manga, History


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]


class MangaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Manga
        exclude = ["_id"]


class HistorySerializers(serializers.ModelSerializer):
    class Meta:
        model = History
        exclude = ["_id"]
