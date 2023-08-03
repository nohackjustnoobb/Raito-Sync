from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager


class Manga(models.Model):
    _id = models.AutoField(primary_key=True, editable=False)
    id = models.TextField()
    driver = models.TextField()


class History(models.Model):
    _id = models.AutoField(primary_key=True, editable=False)
    update_datetime = models.DateTimeField(auto_now=True)
    id = models.TextField()
    driver = models.TextField()
    title = models.TextField()
    thumbnail = models.TextField()
    latest = models.TextField()
    datetime = models.IntegerField()
    new = models.BooleanField()
    chapter = models.TextField(null=True)
    page = models.IntegerField(null=True)
    isExtra = models.BooleanField(null=True)


class User(AbstractBaseUser):
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    collections = models.ManyToManyField(Manga, blank=True, related_name="collections")
    history = models.ManyToManyField(History, blank=True, related_name="history")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
