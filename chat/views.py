from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from courses.models import Course
from django.contrib import messages

@login_required
def chat_list(request):
    if request.user.is_instructor:
        courses = Course.objects.filter(instructor=request.user)
    else:
        courses = Course.objects.filter(students=request.user)
    chat_rooms = ChatRoom.objects.filter(course__in=courses)
    return render(request, 'chat/chat_list.html', {'chat_rooms': chat_rooms})

@login_required
def chat_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    # Add permission check
    if not (request.user.is_instructor and room.course.instructor == request.user) and \
       not (request.user.is_student and room.course.students.filter(id=request.user.id).exists()):
        messages.error(request, 'You do not have permission to access this chat room.')
        return redirect('chat_list')
    messages = room.messages.order_by('-timestamp')[:50]
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages
    }) 