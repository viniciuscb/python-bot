from django.shortcuts import render
from django.conf import settings


def index(request):
    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'current_user': request.user,
        'messages_limit': settings.CHAT_MESSAGES_LIMIT
    })