from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from courses.models import Course
from django.contrib import messages

@login_required
def chat_list(request):
    if request.user.is_instructor:
        # For instructors, show chat rooms for courses they teach
        courses = Course.objects.filter(instructor=request.user)
    else:
        # For students, show chat rooms for courses they're enrolled in
        courses = Course.objects.filter(students=request.user)
    
    # Get or create chat rooms for each course
    chat_rooms = []
    for course in courses:
        # Get or create a general chat room for each course
        chat_room, created = ChatRoom.objects.get_or_create(
            course=course,
            name=f"General - {course.title}"
        )
        chat_rooms.append(chat_room)
    
    return render(request, 'chat/chat_list.html', {
        'chat_rooms': chat_rooms
    })

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