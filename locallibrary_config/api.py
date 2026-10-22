# locallibrary_config/api.py
from ninja import ModelSchema
from ninja import NinjaAPI
from ninja import Schema, Status
from django.shortcuts import get_object_or_404
from chat.models import Room
from ninja.pagination import paginate
from ninja.security import django_auth

api = NinjaAPI(auth=django_auth)

@api.delete("/rooms/{room_id}", response={204: None})
def delete_room(request, room_id: int):
    get_object_or_404(Room, id=room_id).delete()

