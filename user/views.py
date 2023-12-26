import os
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.views import APIView
from datetime import datetime

from .serializers import UserSerializers, MangaSerializers, HistorySerializers
from .models import Manga, History as HistoryModel, User


class MyInfo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserSerializers(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            old_pw = request.data["oldPassword"]
            new_pw = request.data["newPassword"]
        except:
            return Response(
                {"error": '"oldPassword" or "newPassword" are missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check old password
        if not request.user.check_password(old_pw):
            return Response(
                {"error": 'Incorrect "oldPassword".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # set new password
        request.user.set_password(new_pw)
        request.user.save()

        serializer = UserSerializers(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Clear(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            pw = request.data["password"]
        except:
            return Response(
                {"error": '"password" is missing.'}, status=status.HTTP_400_BAD_REQUEST
            )

        # check password
        if not request.user.check_password(pw):
            return Response(
                {"error": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST
            )

        request.user.collections.all().delete()
        request.user.history.all().delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class Create(APIView):
    def post(self, request, format=None):
        try:
            pw = request.data["password"]
            em = request.data["email"]
            key = request.data["key"]
        except:
            return Response(
                {"error": '"email", "password", or "key" are missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        REGISTER_KEY = os.getenv("REGISTER_KEY")
        if REGISTER_KEY and REGISTER_KEY != key:
            return Response(
                {"error": "Register Key is not matching."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.create_user(email=em, password=pw)
        except:
            return Response(
                {
                    "error": "An error occurred when creating a user. Check if the email is registered."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserSerializers(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ObtainToken(APIView):
    def post(self, request):
        try:
            pw = request.data["password"]
            em = request.data["email"]
        except:
            return Response(
                {"error": '"email" or "password" are missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=em)
            if user.check_password(pw):
                return Response(
                    {"token": Token.objects.get_or_create(user=user)[0].key},
                    status=status.HTTP_200_OK,
                )

            raise
        except:
            return Response(
                {"error": '"email" or "password" are incorrect.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Collections(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = MangaSerializers(request.user.collections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            # loop through the data
            for i in request.data:
                # check if the object exists
                try:
                    manga = request.user.collections.get(
                        id=i.get("id"), driver=i.get("driver")
                    )
                except Manga.DoesNotExist:
                    # only create if not existing
                    serializer = MangaSerializers(data=i)

                    if serializer.is_valid():
                        manga = serializer.save()
                        request.user.collections.add(manga)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(
                {"error": "An unexpected error occurred when syncing the collections."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, format=None):
        try:
            # try to delete the manga
            request.user.collections.get(
                id=request.query_params.get("id"),
                driver=request.query_params.get("driver"),
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Manga.DoesNotExist:
            return Response(
                {"error": "The responding manga was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class Histories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = HistorySerializers(request.user.history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            if request.data:
                for record in request.data:
                    try:
                        old_record = request.user.history.get(
                            id=record["id"], driver=record["driver"]
                        )

                        if old_record.datetime > record["datetime"]:
                            continue

                        serializer = HistorySerializers(old_record, data=record)
                    except HistoryModel.DoesNotExist:
                        serializer = HistorySerializers(data=record)

                    if serializer.is_valid():
                        request.user.history.add(serializer.save())

            date = request.query_params.get("date")
            serializer = HistorySerializers(
                request.user.history.filter(
                    update_datetime__gte=datetime.fromtimestamp(int(date) / 1e3)
                )
                if date
                else request.user.history,
                many=True,
            )

            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        except:
            return Response(
                {"error": "An unexpected error occurred when syncing the histories."},
                status=status.HTTP_400_BAD_REQUEST,
            )
